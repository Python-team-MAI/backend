from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn, BaseModel

BASE_DIR = Path(__file__).parent.parent.parent


class DBSettings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: str
    EXPIRE_TIME_DAYS: int

    @property
    def DATABASE_URL_asyncpg(self):
        # DSN
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    model_config = SettingsConfigDict(env_file=".env")


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    register_token_expire_minutes: int = 10
    refresh_token_expire_days: int = 30  # days


class Oauth2(BaseSettings):
    AUTH_GOOGLE_ID: str
    AUTH_GOOGLE_SECRET: str
    AUTH_GOOGLE_API_KEY: str
    AUTH_GOOGLE_IOS_ID: str
    AUTH_SECRET: str

    AUTH_VK_ID: str
    AUTH_VK_SECRET: str

    AUTH_GITHUB_ID: str
    AUTH_GITHUB_SECRET: str

    AUTH_YANDEX_ID: str
    AUTH_YANDEX_SECRET: str

    BACKEND_HOST: str
    FRONTEND_HOST: str

    model_config = SettingsConfigDict(env_file=".env.local")


class Settings(BaseSettings):
    api_v1_prefix: str = "/v1"

    db: DBSettings = DBSettings()

    auth_jwt: AuthJWT = AuthJWT()

    oauth2: Oauth2 = Oauth2()


settings = Settings()

