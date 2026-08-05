from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "COREF Logistique API"
    app_version: str = "1.0.0"
    database_url: str = (
        "postgresql+psycopg://coref:change_me@db:5432/coref_logistique"
    )
    frontend_origin: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
