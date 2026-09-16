from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Both come from your Supabase project.
    database_url: str  # "Connect" button (top of dashboard) -> Connection String -> Session pooler
    supabase_url: str  # Project Settings -> API -> Project URL. Used to verify JWTs via Supabase's JWKS endpoint.
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
