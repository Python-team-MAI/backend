from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn, BaseModel

BASE_DIR = Path(__file__).parent.parent.parent


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class DBSettings(EnvBaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: str
    BROKER_DB: str
    EXPIRE_TIME_DAYS: int

    MINIO_ENDPOINT: str
    MINIO_ACCESS: str
    MINIO_SECRET: str
    MINIO_ACL: str
    KNOWLEDGE_BUCKET: str

    @property
    def DATABASE_URL_asyncpg(self):
        # DSN
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def REDIS_URL(self):
        # DSN
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def BROKER_URL(self):
        # DSN
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.BROKER_DB}"


class MailSettings(EnvBaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_FOLDER: Path = BASE_DIR / "app" / "templates"


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

    model_config = SettingsConfigDict(env_file=".env.local")


class HostsSettings(EnvBaseSettings):
    DOMEN: str
    BACKEND_HOST: str
    FRONTEND_HOST: str


class AssistantSettings(EnvBaseSettings):
    YANDEX_CLOUD_FOLDER_ID: str
    YANDEX_CLOUD_API_KEY: str


class Settings(BaseSettings):
    api_v1_prefix: str = "/v1"

    db: DBSettings = DBSettings()

    auth_jwt: AuthJWT = AuthJWT()

    oauth2: Oauth2 = Oauth2()

    mail: MailSettings = MailSettings()

    hosts: HostsSettings = HostsSettings()

    assistant: AssistantSettings = AssistantSettings()


settings = Settings()
