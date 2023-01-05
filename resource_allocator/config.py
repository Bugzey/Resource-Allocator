import os

from sqlalchemy.engine import url

URL = url.URL(
    drivername = "postgresql",
    username = os.environ["USER"],
    password = os.environ["PASSWORD"],
    host = os.environ["SERVER"],
    port = os.environ["PORT"],
    database = os.environ["DATABASE"],
)
SECRET = os.environ["SECRET"]

#   Optional Azure Active Directory integration
AAD_CLIENT_ID = os.environ.get("AAD_CLIENT_ID")
AAD_CLIENT_SECRET = os.environ.get("AAD_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")
SERVER_NAME = os.environ.get("SERVER_NAME")
TENANT_ID = os.environ.get("TENANT_ID")

AZURE_CONFIGURED = AAD_CLIENT_ID is not None and AAD_CLIENT_SECRET is not None \
    and REDIRECT_URI is not None and SERVER_NAME is not None \
    and TENANT_ID is not None

#   Local logins enabled
LOCAL_LOGIN_ENABLED = os.environ.get("LOCAL_LOGIN_ENABLED") in (None, "1", "yes", "true")

