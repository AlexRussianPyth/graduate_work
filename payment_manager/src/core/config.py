from pydantic import BaseSettings, Field


class DotEnvMixin(BaseSettings):
    class Config:
        env_file = '.env'


class AuthSettings(DotEnvMixin):
    """Настройки для связи с нашим сервисом Авторизации"""
    auth_host: str = Field("localhost", env='AUTH_HOST')
    auth_port: int = Field(8999, env='AUTH_PORT')
    superuser_email: str = Field("alexvkleschov@gmail.com", env='AUTH_SUPERUSER_EMAIL')
    superuser_password: str = Field(..., env='AUTH_SUPERUSER_PASSWORD')
    roles_path: str = Field("/auth/api/v1/users/", env='AUTH_ROLES_PATH')
    login_path: str = Field("/auth/api/v1/auth/login", env='AUTH_LOGIN_PATH')

    @property
    def roles_url(self):
        """Получение полного пути к эндпоинту по работе с Ролями"""
        return f"http://{self.auth_host}:{self.auth_port}{self.roles_path}"

    @property
    def login_url(self):
        """Получение полного пути к эндпоинту по авторизации Юзера"""
        return f"http://{self.auth_host}:{self.auth_port}{self.login_path}"


class PostgresSettings(DotEnvMixin):
    user: str = Field("postgres", env='POSTGRES_USER')
    password: str = Field("password", env='POSTGRES_PASSWORD')
    host: str = Field("db", env='POSTGRES_HOST')
    port: int = Field(5432, env='POSTGRES_PORT')
    db: str = Field("payments", env='POSTGRES_DB')

    @property
    def dsn(self):
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}'

class Settings(DotEnvMixin):
    """Класс, дающий доступ к разным категориям настроек"""
    auth: AuthSettings = AuthSettings()
    postgres: PostgresSettings = PostgresSettings()


# Создаем объект Настроек
settings = Settings()
