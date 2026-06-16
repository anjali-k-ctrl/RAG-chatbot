from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    GEMINI_API_KEY: str = ""

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_BUCKET_NAME: str

    OPENSEARCH_HOST: str = ""
    OPENSEARCH_PORT: int = 443

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()