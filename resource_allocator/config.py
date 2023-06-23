import configparser
from dataclasses import dataclass, field
import os
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy.engine import url


@dataclass
class Config:
    AAD_CLIENT_ID: str | None
    AAD_CLIENT_SECRET: str | None
    AZURE_CONFIGURED: bool = field(init=False)
    DB_DATABASE: str
    DB_HOST: str
    DB_PASSWORD: str = field(repr=False)
    DB_PORT: str
    DB_USER: str
    LOCAL_LOGIN_ENABLED: bool
    REDIRECT_URI: str | None
    SECRET: str = field(repr=False)
    SERVER_NAME: str | None
    TENANT_ID: str | None
    URL: str = field(init=False, repr=False)

    _sess: Session = None
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

    def __post_init__(self):
        """
        Create compound variables or variables that depend on others
        """
        self.AZURE_CONFIGURED = self.AAD_CLIENT_ID is not None \
            and self.AAD_CLIENT_SECRET is not None \
            and self.REDIRECT_URI is not None \
            and self.SERVER_NAME is not None \
            and self.TENANT_ID is not None

        self.URL=url.URL.create(
            drivername="postgresql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_DATABASE,
        )
        self.__class__._instance.append(self)

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
            LOCAL_LOGIN_ENABLED=os.environ.get("LOCAL_LOGIN_ENABLED") in (None, "1", "yes", "true"),
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
            DB_USER=default["DB_USER"],
            DB_PASSWORD=default["DB_PASSWORD"],
            DB_HOST=default["DB_HOST"],
            DB_PORT=int(default["DB_PORT"]),
            DB_DATABASE=default["DB_DATABASE"],
            SECRET=default["SECRET"],
            AAD_CLIENT_ID=default.get("AAD_CLIENT_ID"),
            AAD_CLIENT_SECRET=default.get("AAD_CLIENT_SECRET"),
            REDIRECT_URI=default.get("REDIRECT_URI"),
            SERVER_NAME=default.get("SERVER_NAME"),
            TENANT_ID=default.get("SERVER_NAME"),
            LOCAL_LOGIN_ENABLED=default.getboolean("LOCAL_LOGIN_ENABLED"),
        )
