import unittest
import os
import sys
import tempfile
import shutil
import datetime
from unittest.mock import patch, MagicMock

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pressure_info import PressureInfo
from src.internal._pressure_logger import _PressureLogQueue, _PressureInfoLog, _PressureInfoLogStatus


class TestPressureLogQueue(unittest.TestCase):
    def setUp(self):
        # 테스트용 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.original_dirname = os.path.dirname
        
        # 모킹: os.path.dirname이 임시 디렉토리를 반환하도록 설정
        def mock_dirname(path):
            if path.endswith('_pressure_logger.py'):
                return self.test_dir
            return self.original_dirname(path)
        
        self.dirname_patcher = patch('os.path.dirname', side_effect=mock_dirname)
        self.dirname_patcher.start()
        
        # API 설정 모킹
        self.api_config_patcher = patch('src.internal._pressure_logger.api_config')
        self.mock_api_config = self.api_config_patcher.start()
        self.mock_api_config.get_min_interval.return_value = 10  # 10초 간격
        
        # 로거 모킹
        self.logger_patcher = patch('src.internal._pressure_logger._Logger')
        self.mock_logger_class = self.logger_patcher.start()
        self.mock_logger = MagicMock()
        self.mock_logger_class.from_config.return_value = self.mock_logger

    def tearDown(self):
        # 임시 디렉토리 정리
        shutil.rmtree(self.test_dir)
        self.dirname_patcher.stop()
        self.api_config_patcher.stop()
        self.logger_patcher.stop()

    def create_test_pressure_info(self, created_at=None):
        """테스트용 PressureInfo 객체 생성"""
        pressure_info = PressureInfo(10, 20, 30, 40)
        if created_at:
            pressure_info.created_at = created_at
        return pressure_info

    # 빈 큐 초기화 테스트
    def test_init_empty_queue(self):
        """빈 큐 초기화 테스트"""
        queue = _PressureLogQueue()
        
        self.assertEqual(len(queue.pending_logs), 0)
        self.assertEqual(len(queue.sent_logs), 0)
        self.assertEqual(len(queue.failed_logs), 0)
        self.assertEqual(len(queue.sending_logs), 0)
        self.assertFalse(queue._is_scheduled)

    # PENDING 상태 로그 추가 테스트
    def test_push_pending_log(self):
        """PENDING 상태 로그 추가 테스트"""
        queue = _PressureLogQueue()
        pressure_info = self.create_test_pressure_info()
        
        result = queue.push(pressure_info, _PressureInfoLogStatus.PENDING)
        
        self.assertTrue(result)
        self.assertEqual(len(queue.pending_logs), 1)
        self.assertEqual(queue.pending_logs[0].pressure_info, pressure_info)
        self.assertEqual(queue.pending_logs[0]._status, _PressureInfoLogStatus.PENDING)

    # SENT 상태 로그 추가 테스트
    def test_push_sent_log(self):
        """SENT 상태 로그 추가 테스트"""
        queue = _PressureLogQueue()
        pressure_info = self.create_test_pressure_info()
        
        # 먼저 sending_logs에 추가
        queue.sending_logs.append(_PressureInfoLog(pressure_info, _PressureInfoLogStatus.SENDING))
        
        result = queue.push(pressure_info, _PressureInfoLogStatus.SENT)
        
        self.assertTrue(result)
        self.assertEqual(len(queue.sent_logs), 1)
        self.assertEqual(len(queue.sending_logs), 0)
        self.assertEqual(queue.sent_logs[0].pressure_info, pressure_info)

    # FAILED 상태 로그 추가 테스트
    def test_push_failed_log(self):
        """FAILED 상태 로그 추가 테스트"""
        queue = _PressureLogQueue()
        pressure_info = self.create_test_pressure_info()
        
        # 먼저 sending_logs에 추가
        queue.sending_logs.append(_PressureInfoLog(pressure_info, _PressureInfoLogStatus.SENDING))
        
        result = queue.push(pressure_info, _PressureInfoLogStatus.FAILED)
        
        self.assertTrue(result)
        self.assertEqual(len(queue.failed_logs), 1)
        self.assertEqual(len(queue.sending_logs), 0)
        self.assertEqual(queue.failed_logs[0].pressure_info, pressure_info)
        self.assertFalse(queue._is_scheduled)

    def test_is_empty(self):
        """큐가 비어있는지 확인하는 테스트"""
        queue = _PressureLogQueue()
        
        # 초기 상태: 비어있음
        self.assertTrue(queue.is_empty())
        
        # pending 로그 추가
        pressure_info = self.create_test_pressure_info()
        queue.push(pressure_info, _PressureInfoLogStatus.PENDING)
        self.assertFalse(queue.is_empty())
        
        # 모든 로그 제거
        queue.pending_logs.clear()
        self.assertTrue(queue.is_empty())
        
        # failed 로그 추가
        queue.failed_logs.append(_PressureInfoLog(pressure_info, _PressureInfoLogStatus.FAILED))
        self.assertFalse(queue.is_empty())

    # 로그 스케줄링 테스트
    def test_schedule_logs(self):
        """로그 스케줄링 테스트"""
        queue = _PressureLogQueue()
        
        # failed 로그들 추가
        pressure_info1 = self.create_test_pressure_info(datetime.datetime(2024, 1, 1, 12, 0, 0))
        pressure_info2 = self.create_test_pressure_info(datetime.datetime(2024, 1, 1, 11, 0, 0))
        
        queue.failed_logs.append(_PressureInfoLog(pressure_info1, _PressureInfoLogStatus.FAILED))
        queue.failed_logs.append(_PressureInfoLog(pressure_info2, _PressureInfoLogStatus.FAILED))
        
        # pending 로그 추가
        pressure_info3 = self.create_test_pressure_info(datetime.datetime(2024, 1, 1, 13, 0, 0))
        queue.pending_logs.append(_PressureInfoLog(pressure_info3, _PressureInfoLogStatus.PENDING))
        
        queue._schedule_logs()
        
        # failed 로그가 pending으로 이동하고 날짜순으로 정렬되어야 함
        self.assertEqual(len(queue.failed_logs), 0)
        self.assertEqual(len(queue.pending_logs), 3)
        self.assertTrue(queue._is_scheduled)
        
        # 날짜 순으로 정렬 확인 (이른 날짜가 먼저)
        dates = [log.get_created_at() for log in queue.pending_logs]
        self.assertEqual(dates, sorted(dates))

    # 로그 팝 테스트
    def test_pop_log(self):
        """로그 팝 테스트"""
        queue = _PressureLogQueue()
        
        # pending 로그 추가
        pressure_info1 = self.create_test_pressure_info(datetime.datetime(2024, 1, 1, 12, 0, 0))
        pressure_info2 = self.create_test_pressure_info(datetime.datetime(2024, 1, 1, 11, 0, 0))
        
        queue.pending_logs.append(_PressureInfoLog(pressure_info1, _PressureInfoLogStatus.PENDING))
        queue.pending_logs.append(_PressureInfoLog(pressure_info2, _PressureInfoLogStatus.PENDING))
        
        # 첫 번째 로그 팝
        popped_info = queue.pop()
        
        # 스케줄링 후 날짜순으로 정렬되므로 더 이른 날짜(pressure_info2)가 먼저 팝되어야 함
        self.assertEqual(popped_info.created_at, pressure_info2.created_at)
        self.assertEqual(popped_info.occipu, pressure_info2.occipu)
        self.assertEqual(len(queue.pending_logs), 1)
        self.assertEqual(len(queue.sending_logs), 1)
        self.assertEqual(queue.sending_logs[0].pressure_info.created_at, pressure_info2.created_at)

    # 최소 간격 검증 테스트
    def test_min_interval_validation(self):
        """최소 간격 검증 테스트"""
        queue = _PressureLogQueue()
        
        # 첫 번째 로그 추가
        base_time = datetime.datetime(2024, 1, 1, 12, 0, 0)
        pressure_info1 = self.create_test_pressure_info(base_time)
        queue.push(pressure_info1, _PressureInfoLogStatus.PENDING)
        
        # 5초 후 로그 추가 (최소 간격 10초보다 작음)
        pressure_info2 = self.create_test_pressure_info(base_time + datetime.timedelta(seconds=5))
        result = queue.push(pressure_info2, _PressureInfoLogStatus.PENDING)
        
        # 간격이 부족하여 추가되지 않아야 함
        self.assertFalse(result)
        self.assertEqual(len(queue.pending_logs), 1)
        
        # 15초 후 로그 추가 (최소 간격 10초보다 큼)
        pressure_info3 = self.create_test_pressure_info(base_time + datetime.timedelta(seconds=15))
        result = queue.push(pressure_info3, _PressureInfoLogStatus.PENDING)
        
        # 간격이 충분하여 추가되어야 함
        self.assertTrue(result)
        self.assertEqual(len(queue.pending_logs), 2)

    def test_save_and_load_logs(self):
        """로그 저장 및 로드 테스트"""
        # 첫 번째 큐에서 로그 추가 및 저장
        queue1 = _PressureLogQueue()
        pressure_info = self.create_test_pressure_info()
        queue1.push(pressure_info, _PressureInfoLogStatus.PENDING)
        queue1._save_logs()
        
        # 새로운 큐에서 로그 로드
        queue2 = _PressureLogQueue()
        
        # 로드된 로그 확인
        self.assertEqual(len(queue2.pending_logs), 1)
        self.assertEqual(queue2.pending_logs[0].pressure_info.occipu, pressure_info.occipu)
        self.assertEqual(queue2.pending_logs[0].pressure_info.scapula, pressure_info.scapula)
        self.assertEqual(queue2.pending_logs[0].pressure_info.elbow, pressure_info.elbow)
        self.assertEqual(queue2.pending_logs[0].pressure_info.hip, pressure_info.hip)


if __name__ == '__main__':
    unittest.main()