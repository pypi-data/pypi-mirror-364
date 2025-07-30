from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    DEBUG_MODE: bool = True
    API_V1_PREFIX: str = "/api"

    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "fastapi_dev"

    # 日志配置
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"

    # 固定API密钥配置
    FIXED_API_KEY: str

    @property
    def database_url(self) -> str:
        """构建数据库连接URL"""
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = (".env", ".env.prod")  # 多个环境文件，后者优先


config = Settings()
