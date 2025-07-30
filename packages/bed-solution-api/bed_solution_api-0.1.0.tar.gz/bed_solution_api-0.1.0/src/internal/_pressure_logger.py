from pressure_info import PressureInfo
from ._logger import _Logger
from ._api_config import api_config
from ._register_device import _DeviceInfo
from ._database import _Database
from enum import Enum
import os, json, datetime

class _PressureInfoLogStatus(Enum):
    PENDING = 'pending'
    SENDING = 'sending'
    SENT = 'sent'
    FAILED = 'failed'

class _PressureInfoLog:
    def __init__(self, pressure_info: PressureInfo, status: _PressureInfoLogStatus):
        self.pressure_info = pressure_info
        self._status = status

    @classmethod
    def from_json(cls, data: dict):
        return cls(PressureInfo.from_json(data['pressure_info']), _PressureInfoLogStatus(data['status']))

    def get_created_at(self):
        return self.pressure_info.created_at

    def to_json(self):
        return {
            'pressure_info': self.pressure_info._to_json(),
            'status': self._status.value
        }

class _PressureLogQueue:
    def __init__(self):
        self._logger = _Logger.from_config('PressureLogQueue')
        self._MAX_SENT_LOGS = 30
        self.pending_logs = []
        self.sent_logs = []
        self.failed_logs = []
        self.sending_logs = []
        self._is_scheduled = False
        self._load_logs()

    def _get_log_file_path(self):
        return os.path.join(os.path.dirname(__file__), 'pressure_logs.json')

    def _load_logs(self):
        path = self._get_log_file_path()
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    self.pending_logs = [_PressureInfoLog.from_json(log) for log in data['pending_logs']]
                    self.sent_logs = [_PressureInfoLog.from_json(log) for log in data['sent_logs']]
                    self.failed_logs = [_PressureInfoLog.from_json(log) for log in data['failed_logs']]
                    self.sending_logs = [_PressureInfoLog.from_json(log) for log in data['sending_logs']]
            except Exception as e:
                self._logger.critical(f"Failed to load pressure logs: {e}. This problem cause the pressure logs will be lost.")

    # 로그를 파일에 저장
    def _save_logs(self):
        path = self._get_log_file_path()
        try:
            with open(path, 'w') as f:
                json.dump(self._to_json(), f)
        except Exception as e:
            self._logger.critical(f"Failed to save pressure logs: {e}. This problem cause the pressure logs will be lost.")

    # 최소 간격 체크
    def _is_min_interval_valid(self, pressure_info: PressureInfo):
        if not self._is_scheduled:
            self._schedule_logs()

        previous_log = None
        next_log = None

        if self.pending_logs:
            previous = next((log for log in reversed(self.pending_logs) if log.get_created_at() < pressure_info.created_at), None)
            next_item = next((log for log in self.pending_logs if log.get_created_at() > pressure_info.created_at), None)
            if previous and (not previous_log or previous_log.get_created_at() < previous.get_created_at()):
                previous_log = previous
            if next_item and (not next_log or next_log.get_created_at() > next_item.get_created_at()):
                next_log = next_item

        if self.sent_logs:
            previous = next((log for log in reversed(self.sent_logs) if log.get_created_at() < pressure_info.created_at), None)
            next_item = next((log for log in self.sent_logs if log.get_created_at() > pressure_info.created_at), None)
            if previous and (not previous_log or previous_log.get_created_at() < previous.get_created_at()):
                previous_log = previous
            if next_item and (not next_log or next_log.get_created_at() > next_item.get_created_at()):
                next_log = next_item

        if self.sending_logs:
            previous = next((log for log in reversed(self.sending_logs) if log.get_created_at() < pressure_info.created_at), None)
            next_item = next((log for log in self.sending_logs if log.get_created_at() > pressure_info.created_at), None)
            if previous and (not previous_log or previous_log.get_created_at() < previous.get_created_at()):
                previous_log = previous
            if next_item and (not next_log or next_log.get_created_at() > next_item.get_created_at()):
                next_log = next_item

        if previous_log and previous_log.get_created_at() + datetime.timedelta(minutes=api_config.get_min_interval()) > pressure_info.created_at:
            self._logger.warning(f"Pressure info has invalid interval. This pressure info will be ignored.")
            return False

        if next_log and next_log.get_created_at() - datetime.timedelta(minutes=api_config.get_min_interval()) < pressure_info.created_at:
            self._logger.warning(f"Pressure info has invalid interval. This pressure info will be ignored.")
            return False

        return True

    def _remove_sending_log(self, pressure_info: PressureInfo):
        for sending_log in self.sending_logs:
            if sending_log.pressure_info.created_at == pressure_info.created_at:
                self.sending_logs.remove(sending_log)
                break
    
    def push(self, pressure_info: PressureInfo, status: _PressureInfoLogStatus) -> bool:
        if status == _PressureInfoLogStatus.PENDING or status == _PressureInfoLogStatus.FAILED:
            if not self._is_min_interval_valid(pressure_info):
                return False

        if status == _PressureInfoLogStatus.PENDING:
            self.pending_logs.append(_PressureInfoLog(pressure_info, status))
            self._is_scheduled = False
            self._save_logs()
            return True
        elif status == _PressureInfoLogStatus.SENT:
            self.sent_logs.append(_PressureInfoLog(pressure_info, status))
            self._remove_sending_log(pressure_info)
            if len(self.sent_logs) > self._MAX_SENT_LOGS:
                self.sent_logs = self.sent_logs[self._MAX_SENT_LOGS:]
            self._save_logs()
            return True
        elif status == _PressureInfoLogStatus.FAILED:
            self.failed_logs.append(_PressureInfoLog(pressure_info, status))
            self._remove_sending_log(pressure_info)
            self._is_scheduled = False
            self._save_logs()
            return True

        return False
    
    # pending logs와 failed logs를 조합하여 재스케쥴링합니다.
    def _schedule_logs(self):
        if self.failed_logs:
            self.pending_logs.extend(self.failed_logs)
            self.failed_logs.clear()
            
        if self.pending_logs:
            self.pending_logs.sort(key=lambda x: x.get_created_at()) # 날짜가 앞선 순으로 높은 우선순위 부여

        self._is_scheduled = True
        self._save_logs()
    
    # 대기열이 비어있는지 확인
    def is_empty(self):
        return len(self.pending_logs) == 0 and len(self.sending_logs) == 0 and len(self.failed_logs) == 0

    def pop(self):
        if not self._is_scheduled:
            self._schedule_logs()

        log: _PressureInfoLog = None
        if self.pending_logs:
            log = self.pending_logs.pop(0)
            self.sending_logs.append(log)
            return log.pressure_info
        return None
        
    def _to_json(self):
        return {
            'pending_logs': [log.to_json() for log in self.pending_logs],
            'sent_logs': [log.to_json() for log in self.sent_logs],
            'failed_logs': [log.to_json() for log in self.failed_logs],
            'sending_logs': [log.to_json() for log in self.sending_logs]
        }

class _PressureLogger:
    def __init__(self):
        self._logger = _Logger.from_config('PressureLogger')
        self._pressure_log_queue = _PressureLogQueue()
        self._MAX_TRY_CNT = 10

    # 대기열에 추가
    def add_pressure_info(self, pressure_info: PressureInfo):
        self._pressure_log_queue.push(pressure_info, _PressureInfoLogStatus.PENDING)

    def _send_to_server(self, data, database: _Database):
        database.get_pressure_logs_table().insert(data).execute()

    def send(self, database: _Database = None, device_id = None):
        if self._pressure_log_queue.is_empty():
            self._logger.info('Pressure log queue is empty. No pressure info to send.')
            return
        if database is None:
            self._logger.warning('Database is not provided. Pressure info will not be saved.')
            return
        if device_id is None:
            self._logger.warning('Device is not provided. Pressure info will not be sent.')
            return

        try_cnt = 0
        while not self._pressure_log_queue.is_empty() and try_cnt < self._MAX_TRY_CNT:
            try_cnt += 1
            log = self._pressure_log_queue.pop()
            json_data = log.to_json()
            json_data['device_id'] = device_id
            try:
                self._send_to_server(json_data, database)
                self._pressure_log_queue.push(log, _PressureInfoLogStatus.SENT)
            except Exception as e:
                self._logger.error(f'Failed to send pressure info to server: {e}')
                self._pressure_log_queue.push(log, _PressureInfoLogStatus.FAILED)
        self._pressure_log_queue._save_logs()

