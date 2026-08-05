from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "COREF Logistique API"
    database_url: str = "postgresql+psycopg://coref:change_me@db:5432/coref_logistique"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
