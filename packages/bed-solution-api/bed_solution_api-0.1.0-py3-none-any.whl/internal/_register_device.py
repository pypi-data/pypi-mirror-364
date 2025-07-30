from ._logger import _Logger
from ._database import _Database
from supabase import Client
from typing import Optional
import os
import datetime
import uuid
import json

# 장비 정보
class _DeviceInfo:
    def __init__(self, device_id: int, created_at: str):
        self.device_id = device_id
        self.created_at = created_at

    def get_device_id(self) -> int:
        return self.device_id

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls(data['device_id'], data['created_at'])
    
    def to_json(self) -> str:
        return json.dumps({
            'device_id': self.device_id,
            'created_at': self.created_at
        })
    
# 장비 등록 클래스
class _BedSolutionDevice:
    def __init__(self):
        self._logger = _Logger.from_config('RegisterDevice')
        self._device: _DeviceInfo = self._load_device_data()

    def _get_device_data_path(self) -> str:
        return os.path.join(os.path.expanduser('~'), '.bed_solution_api', 'device.json')

    def _load_device_data(self) -> _DeviceInfo:
        path = self._get_device_data_path()
        if not os.path.exists(path):
            self._logger.warning('Device file not found. Please register the device first.')
            return None
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return _DeviceInfo.from_json(data)
        except Exception as e:
            self._logger.error(f'Failed to load device file: {e}')
            return None

    def _save_device_data(self, new_device: _DeviceInfo):
        path = self._get_device_data_path()
        try:
            with open(path, 'w') as f:
                f.write(new_device.to_json())
        except Exception as e:
            self._logger.error(f'Failed to save device file: {e}')
            return False
        return True

    def _remove_device_data(self):
        path = self._get_device_data_path()
        if os.path.exists(path):
            os.remove(path)

    # 장비 ID 반환
    def get_device_id(self) -> int:
        if self._device is None:
            self._logger.warning('Device id is not set. Please register the device first.')
            return -1
        return self._device.get_device_id()

    # 장비 등록 여부 확인
    def is_registered(self) -> bool:
        return self._device is not None

    # 장비 ID 생성
    def _generate_device_id(self) -> int:
        return uuid.uuid4().int

    # 장비 등록
    def register(self, database: _Database) -> Optional[_DeviceInfo]:
        if self.is_registered():
            self._logger.debug('Device is already registered.')
            return self._device
        new_device = _DeviceInfo(self._generate_device_id(), datetime.datetime.now().isoformat())
        try:
            database.get_device_table().insert(new_device.to_json()).execute()
            if self._save_device_data(new_device):
                self._device = new_device
                self._logger.info(f'Device registered successfully. Device id: {self._device.get_device_id()}')
                return self._device
        except Exception as e:
            self._logger.error(f'Failed to register device: {e}')
            return None
        return None

    # 장비 등록 해제
    def deregister(self, database: _Database) -> bool:
        if not self.is_registered():
            self._logger.warning('Device is not registered.')
            return
        try:
            database.get_device_table().delete().eq('id', self._device.get_device_id()).execute()
            self._remove_device_data()
            self._device = None
            self._logger.info(f'Device deregistered successfully')
            return True
        except Exception as e:
            self._logger.error(f'Failed to deregister device: {e}')
            return False