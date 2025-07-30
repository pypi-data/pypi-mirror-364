import logging
from rich.logging import RichHandler
import os

class _Logger:
    def __init__(self, name: str, debugging: bool, enable_console: bool = True, enable_file: bool = False, dir_path: str = None):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG if debugging else logging.INFO)

        if enable_console:
            self._logger.addHandler(RichHandler())

        if enable_file and not dir_path:
            import tempfile
            temp_dir = tempfile.gettempdir()
            dir_path = os.path.join(temp_dir, 'bed_solution_api.logs')
            self.warning(f'File logging is enabled but no directory path is provided. Defaulting to {dir_path}')

        if enable_file and dir_path:
            self._setup_log_file(dir_path)
            self._logger.addHandler(logging.FileHandler(os.path.join(dir_path, 'bed_solution_api.log')))

    @classmethod
    def from_config(cls, name: str):
        from ._api_config import api_config  # 함수 내부로 import 이동
        return cls(name, api_config.get_debugging(), api_config.get_enable_console(), api_config.get_enable_file(), api_config.get_log_dir_path())
    
    def _setup_log_file(self, dir_path: str):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    # 정보 로깅
    def info(self, message: str):
        self._logger.info(message)

    # 에러 로깅
    def error(self, message: str):
        self._logger.error(message)

    # 경고 로깅
    def warning(self, message: str):
        self._logger.warning(message)

    # 디버그 로깅
    def debug(self, message: str):
        self._logger.debug(message)

    # 치명적 에러 로깅
    def critical(self, message: str):
        self._logger.critical(message, stack_info=True)

