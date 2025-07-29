from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    pinecone_key: str | None = None
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )
