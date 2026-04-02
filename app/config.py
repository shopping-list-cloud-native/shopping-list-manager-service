import os


class Settings:
    def __init__(self) -> None:
        self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
        self.io_service_url = os.getenv("IO_SERVICE_URL", "http://io-service:8000")


settings = Settings()
