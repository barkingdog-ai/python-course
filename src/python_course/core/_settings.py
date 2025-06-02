from functools import lru_cache
from typing import Any, override
from zoneinfo import ZoneInfo

from dotenv import find_dotenv, load_dotenv
from icecream import ic
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="allow",
    )

    HOST: str = "localhost"
    PORT: int = Field(24790, ge=1024, le=49151)
    WORKERS: int | None = Field(None, gt=0)

    TZ: ZoneInfo = ZoneInfo("Asia/Taipei")

    OPENAI_API_KEY: SecretStr = SecretStr("")

    STREAMLIT_HOST: str = "localhost"
    STREAMLIT_PORT: int = 15792

    @override
    def model_post_init(self, _: Any) -> None:
        if self.model_extra:
            extra_env_var = f"從 .env 中取得的額外環境變數 {self.model_extra}"
            ic(extra_env_var)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    return Settings()
