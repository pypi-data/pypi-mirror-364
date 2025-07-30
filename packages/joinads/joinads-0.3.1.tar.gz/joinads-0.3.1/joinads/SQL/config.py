import os
from dotenv import load_dotenv

class ConfigSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigSingleton, cls).__new__(cls)
            load_dotenv()
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        """
        Carrega as configurações a partir de variáveis de ambiente.
        """
        self._initialize()

    def _initialize(self):
        """
        Inicializa as variáveis de ambiente.
        """
        # MySQL
        self.MYSQL_HOST = os.getenv('DB_HOST')
        self.MYSQL_PORT = int(os.getenv('DB_PORT'))
        self.MYSQL_USER = os.getenv('DB_USER')
        self.MYSQL_PASSWORD = os.getenv('DB_PASSWORD')
        self.MYSQL_DB = os.getenv('DB_NAME')
        # self.MYSQL_CHARSET = os.getenv('DB_CHARSET')

Config = ConfigSingleton()