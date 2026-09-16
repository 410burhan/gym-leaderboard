from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase gives you these from Project Settings -> API
    database_url: str  # Project Settings -> Database -> Connection string (URI, use "Transaction" pooler)
    supabase_jwt_secret: str  # Project Settings -> API -> JWT Settings -> JWT Secret
    supabase_url: str = ""  # not required by backend, but handy to keep alongside
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
