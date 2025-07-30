from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # debug模式
    DEBUG_MODE: bool = True

    # 静态目录
    STATIC_DIR: str = "static"
    STATIC_URL: str = "/static"
    STATIC_NAME: str = "static"

    class Config:
        env_file = (".env", ".env.prod")  # 多个环境文件，后者优先


@lru_cache()
def get_settings() -> Settings:
    return Settings()


config = get_settings()
