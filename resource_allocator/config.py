import configparser
from dataclasses import dataclass, field
import os
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy.engine import url


@dataclass(kw_only=True)
class Config:
    #   Authentication
    AAD_CLIENT_ID: str | None = None
    AAD_CLIENT_SECRET: str | None = field(default=None, repr=False)
    TENANT_ID: str | None = None
    REDIRECT_URI: str | None = None
    LOCAL_LOGIN_ENABLED: bool = False

    #   Database
    DB_DATABASE: str
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str = field(repr=False)
    URL: url.URL = field(init=False, repr=False)

    #   App settings
    SECRET: str = field(repr=False)
    SERVER_NAME: str | None
    ALLOWED_ORIGINS: list[str] = field(default_factory=list)

    _sess: Session = field(init=False, default=None)
    _default_paths = (
        Path("config"),
        Path().home() / ".resource_allocator",
        Path().home() / ".config" / "resource_allocator" / "config",
    )
    _instance = []

    @classmethod
    def get_instance(cls) -> "Config":
        """
        Get the single active config instance if any
        """
        if cls._instance:
            return cls._instance[0]

        raise RuntimeError("No Config instance initialized")

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = []

    def __post_init__(self):
        """
        Create compound variables or variables that depend on others
        """
        if (
            self.AAD_CLIENT_ID is None
            or self.AAD_CLIENT_SECRET is None
            or self.REDIRECT_URI is None
            or self.TENANT_ID is None
        ) and not (
            self.AAD_CLIENT_ID is None
            and self.AAD_CLIENT_SECRET is None
            and self.REDIRECT_URI is None
            and self.TENANT_ID is None
        ):
            raise ValueError(
                "Either all or none of AAD_CLIENT_ID, AAD_CLIENT_SECRET, REDIRECT_URI, TENANT_ID "
                "must be configured"
            )

        if not isinstance(self.LOCAL_LOGIN_ENABLED, bool):
            self.LOCAL_LOGIN_ENABLED = str(self.LOCAL_LOGIN_ENABLED).lower() in ("1", "true", "yes")

        if not self.AZURE_CONFIGURED and not self.LOCAL_LOGIN_ENABLED:
            raise ValueError("Either Azure or local logins must be enabled")

        if isinstance(self.ALLOWED_ORIGINS, str):
            self.ALLOWED_ORIGINS = self.ALLOWED_ORIGINS.split(",")

        if not isinstance(self.DB_PORT, int):
            self.DB_PORT = int(self.DB_PORT)

        self.URL = url.URL.create(
            drivername="postgresql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_DATABASE,
        )
        self.__class__._instance.append(self)

    @property
    def AZURE_CONFIGURED(self) -> bool:
        return self.AAD_CLIENT_ID is not None

    @classmethod
    def from_environment(cls) -> "Config":
        """
        Create a configuration from environment variables.
        """
        if cls._instance:
            return cls._instance[0]

        return cls(
            DB_USER=os.environ["DB_USER"],
            DB_PASSWORD=os.environ["DB_PASSWORD"],
            DB_HOST=os.environ["DB_HOST"],
            DB_PORT=os.environ["DB_PORT"],
            DB_DATABASE=os.environ["DB_DATABASE"],
            SECRET=os.environ["SECRET"],
            AAD_CLIENT_ID=os.environ.get("AAD_CLIENT_ID"),
            AAD_CLIENT_SECRET=os.environ.get("AAD_CLIENT_SECRET"),
            REDIRECT_URI=os.environ.get("REDIRECT_URI"),
            SERVER_NAME=os.environ.get("SERVER_NAME"),
            TENANT_ID=os.environ.get("TENANT_ID"),
            LOCAL_LOGIN_ENABLED=os.environ.get("LOCAL_LOGIN_ENABLED"),
            ALLOWED_ORIGINS=os.getenv("ALLOWED_ORIGINS"),
        )

    @classmethod
    def from_config(cls, path: str | Path) -> "Config":
        if cls._instance:
            return cls._instance[0]

        with open(path, "r", encoding="utf-8") as cur_file:
            data = cur_file.read()

        if "[DEFAULT]" not in data:
            data = f"[DEFAULT]\n{data}"

        config = configparser.ConfigParser()
        config.read_string(data)
        default = config["DEFAULT"]

        return cls(
            AAD_CLIENT_ID=default.get("AAD_CLIENT_ID"),
            AAD_CLIENT_SECRET=default.get("AAD_CLIENT_SECRET"),
            REDIRECT_URI=default.get("REDIRECT_URI"),
            DB_USER=default["DB_USER"],
            DB_PASSWORD=default["DB_PASSWORD"],
            DB_HOST=default["DB_HOST"],
            DB_PORT=int(default["DB_PORT"]),
            DB_DATABASE=default["DB_DATABASE"],
            SECRET=default["SECRET"],
            SERVER_NAME=default.get("SERVER_NAME"),
            TENANT_ID=default.get("SERVER_NAME"),
            LOCAL_LOGIN_ENABLED=default.getboolean("LOCAL_LOGIN_ENABLED"),
            ALLOWED_ORIGINS=default.get("ALLOWED_ORIGINS"),
        )
