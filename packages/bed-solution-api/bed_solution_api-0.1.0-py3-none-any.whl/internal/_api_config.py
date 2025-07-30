from ._logger import _Logger
from dotenv import load_dotenv
import os

# Bad solution API config
class _APIConfig:
    def __init__(self):
        self._logger = _Logger('[Bed Solution API] APIConfig', debugging=False)
        self._load_config()

    def _load_config(self):
        is_loaded = load_dotenv()
        if not is_loaded:
            self._logger.critical('Failed to load .env file. .env file must be in the same directory as the script.')
            raise FileNotFoundError('Failed to load .env file')
        
        try:
            self._api_key = os.getenv('API_KEY')
            self._api_url = os.getenv('API_URL')
            self._debugging = os.getenv('ENABLE_DEBUGGING') == 'True'
            self._enable_console = os.getenv('ENABLE_LOG_CONSOLE') == 'True'
            self._enable_file = os.getenv('ENABLE_LOG_FILE') == 'True'
            self._log_dir_path = os.getenv('LOG_DIR_PATH')
            self._min_interval = int(os.getenv('MIN_INTERVAL'))
        except Exception as e:
            self._logger.critical(f"Failed to get environment variables: {e}")
            raise ValueError(f"Failed to get environment variables: {e}")

    # 로깅 레벨이 DEBUG인지 확인, 디버깅 모드에서는 더 많은 로그를 출력
    def get_debugging(self):
        return self._debugging
    
    # 콘솔 로깅 활성화 여부 반환
    def get_enable_console(self):
        return self._enable_console
    
    # 파일 로깅 활성화 여부 반환
    def get_enable_file(self):
        return self._enable_file
    
    # 로그 디렉토리 경로 반환
    def get_log_dir_path(self):
        return self._log_dir_path

    # 서버 API 키 반환
    def get_api_key(self):
        return self._api_key

    # 서버 API URL 반환
    def get_api_url(self):
        return self._api_url

    # 최소 간격 반환 (초 단위)
    def get_min_interval(self):
        return self._min_interval

api_config = _APIConfig()

