from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://pfmea:pfmea@localhost:5432/pfmea"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    bootstrap_admin_email: str = "admin@drindus.local"
    bootstrap_admin_password: str = "admin123"


settings = Settings()
