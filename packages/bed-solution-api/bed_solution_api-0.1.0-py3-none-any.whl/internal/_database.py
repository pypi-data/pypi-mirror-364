from ._api_config import api_config
from ._logger import _Logger
from supabase import create_client

class _Database:
    def __init__(self):
        self._logger = _Logger.from_config('API Database')
        self._logger.info('Initializing api database')
        try:
            self._logger.info(f'API URL: {api_config.get_api_url()}')
            self._database = create_client(api_config.get_api_url(), api_config.get_api_key())
            self._logger.info('API database initialized')
        except Exception as e:
            self._logger.error(f'Failed to initialize api database: {e}')
            raise e

    def get_device_table(self):
        return self._database.table('devices')

    def get_pressure_logs_table(self):
        return self._database.table('pressure_logs')