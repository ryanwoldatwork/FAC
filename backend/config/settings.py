"""
Django settings for The FAC Django backend project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from base64 import b64decode
import os
import sys
import logging
import json
from .db_url import get_db_url_from_vcap_services
import environs
from cfenv import AppEnv
from audit.get_agency_names import get_agency_names, get_audit_info_lists
import dj_database_url
import newrelic.agent

newrelic.agent.initialize()

env = environs.Env()

ENVIRONMENT = env.str("ENV", "UNDEFINED").upper()

key_service = AppEnv().get_service(name="fac-key-service")
if key_service and key_service.credentials:
    secret = key_service.credentials.get
else:
    secret = os.environ.get

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = environs.Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret("SECRET_KEY")

ALLOWED_HOSTS = env("ALLOWED_HOSTS", "0.0.0.0 127.0.0.1 localhost").split()

# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "json": {"()": "pythonjsonlogger.jsonlogger.JsonFormatter"},
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "local_debug_logger": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "formatter": "simple",
            "class": "logging.StreamHandler",
        },
        "prod_logger": {
            "level": "INFO",
            "filters": ["require_debug_false"],
            "formatter": "json",
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["local_debug_logger", "prod_logger"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {"handlers": ["local_debug_logger", "prod_logger"]},
    },
}

logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("nose").setLevel(logging.CRITICAL)
logging.getLogger("s3transfer").setLevel(logging.CRITICAL)

TEST_RUN = False
if len(sys.argv) > 1 and sys.argv[1] == "test":
    # This should reduce the volume of message displayed when running tests, but
    # unfortunately doesn't suppress stdout.
    logging.disable(logging.ERROR)
    # Set var that Django Debug Toolbar can detect so that it doesn't run; we use
    # this with ENABLE_DEBUG_TOOLBAR much further below:
    TEST_RUN = True

# Django application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.staticfiles",
]

# Third-party apps
INSTALLED_APPS += [
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "storages",
    "djangooidc",
    "dbbackup",
]

# Our apps
INSTALLED_APPS += [
    "audit",
    "api",
    "users",
    "report_submission",
    "dissemination",
    "census_historical_migration",
    "support",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.static_site_url",
                "config.context_processors.omb_num_exp_date",
                "config.context_processors.current_environment",
                "report_submission.context_processors.certifiers_emails_must_not_match",
            ],
            "builtins": [
                "report_submission.templatetags.get_attr",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

POSTGREST = {
    "URL": env.str("POSTGREST_URL", "http://api:3000"),
    "LOCAL": env.str("POSTGREST_URL", "http://api:3000"),
    "DEVELOPMENT": "https://api-dev.fac.gov",
    "STAGING": "https://api-staging.fac.gov",
    "PRODUCTION": "https://api.fac.gov",
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "EST"

USE_I18N = True

USE_TZ = True

USE_L10N = True

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = [
    BASE_DIR / "static",
    # '/var/www/static/',
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# CORS base
CORS_ALLOWED_ORIGINS = [env.str("DJANGO_BASE_URL", "http://localhost:8000")]

STATIC_URL = "/static/"


# Environment specific configurations
DEBUG = False
if ENVIRONMENT not in ["DEVELOPMENT", "PREVIEW", "STAGING", "PRODUCTION"]:
    DATABASES = {
        "default": env.dj_db_url(
            "DATABASE_URL", default="postgres://postgres:password@0.0.0.0/backend"
        ),
    }
    STORAGES = {
        "default": {
            "BACKEND": "report_submission.storages.S3PrivateStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }
    # Per whitenoise docs, insert into middleware list directly after Django
    # security middleware: https://whitenoise.readthedocs.io/en/stable/django.html#enable-whitenoise
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

    # Local environment and Testing environment (CI/CD/GitHub Actions)

    if ENVIRONMENT == "LOCAL":
        DEBUG = env.bool("DJANGO_DEBUG", default=True)
    else:
        DEBUG = env.bool("DJANGO_DEBUG", default=False)

    CORS_ALLOWED_ORIGINS += ["http://0.0.0.0:8000", "http://127.0.0.1:8000"]

    # Private bucket
    AWS_PRIVATE_STORAGE_BUCKET_NAME = "fac-private-s3"
    AWS_PUBLIC_STORAGE_BUCKET_NAME = "fac-public-s3"

    AWS_S3_PRIVATE_REGION_NAME = os.environ.get(
        "AWS_S3_PRIVATE_REGION_NAME", "us-east-1"
    )

    # MinIO only matters for local development and GitHub action environments.
    # These should match what we're setting in backend/run.sh
    AWS_PRIVATE_ACCESS_KEY_ID = os.environ.get("AWS_PRIVATE_ACCESS_KEY_ID", "nutnutnut")
    AWS_PRIVATE_SECRET_ACCESS_KEY = os.environ.get(
        "AWS_PRIVATE_SECRET_ACCESS_KEY", "longtest"
    )
    AWS_S3_PRIVATE_ENDPOINT = os.environ.get(
        "AWS_S3_PRIVATE_ENDPOINT", "http://minio:9000"
    )
    AWS_PRIVATE_DEFAULT_ACL = "private"

    AWS_S3_ENDPOINT_URL = AWS_S3_PRIVATE_ENDPOINT

    # when running locally, the internal endpoint (docker network) is different from the external endpoint (host network)
    AWS_S3_PRIVATE_INTERNAL_ENDPOINT = AWS_S3_ENDPOINT_URL
    AWS_S3_PRIVATE_EXTERNAL_ENDPOINT = "http://localhost:9001"

    DISABLE_AUTH = env.bool("DISABLE_AUTH", default=False)

    # Used for backing up the database https://django-dbbackup.readthedocs.io/en/master/installation.html
    DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
    DBBACKUP_STORAGE_OPTIONS = {"location": BASE_DIR / "backup"}

else:
    # One of the Cloud.gov environments
    STORAGES = {
        "default": {
            "BACKEND": "report_submission.storages.S3PrivateStorage",
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3ManifestStaticStorage",
        },
    }

    vcap = json.loads(env.str("VCAP_SERVICES"))

    DB_URL = get_db_url_from_vcap_services(vcap)
    DATABASES = {"default": dj_database_url.parse(DB_URL)}

    for service in vcap["s3"]:
        if service["instance_name"] == "fac-public-s3":
            # Public AWS S3 bucket for the app
            s3_creds = service["credentials"]

            AWS_ACCESS_KEY_ID = s3_creds["access_key_id"]
            AWS_SECRET_ACCESS_KEY = s3_creds["secret_access_key"]
            AWS_STORAGE_BUCKET_NAME = s3_creds["bucket"]

            AWS_S3_REGION_NAME = s3_creds["region"]
            AWS_DEFAULT_REGION = s3_creds["region"]

            AWS_S3_CUSTOM_DOMAIN = (
                f"{AWS_STORAGE_BUCKET_NAME}.s3-{AWS_S3_REGION_NAME}.amazonaws.com"
            )
            AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

            AWS_LOCATION = "static"
            AWS_QUERYSTRING_AUTH = False
            AWS_DEFAULT_ACL = "public-read"
            STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"

            STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
            AWS_IS_GZIPPED = True

        elif service["instance_name"] == "fac-private-s3":
            # Private AWS S3 bucket for the app's Excel (or other file) uploads
            s3_creds = service["credentials"]

            AWS_PRIVATE_ACCESS_KEY_ID = s3_creds["access_key_id"]
            AWS_PRIVATE_SECRET_ACCESS_KEY = s3_creds["secret_access_key"]
            AWS_PRIVATE_STORAGE_BUCKET_NAME = s3_creds["bucket"]

            AWS_S3_PRIVATE_REGION_NAME = s3_creds["region"]
            AWS_S3_PRIVATE_CUSTOM_DOMAIN = f"{AWS_PRIVATE_STORAGE_BUCKET_NAME}.s3-{AWS_S3_PRIVATE_REGION_NAME}.amazonaws.com"
            AWS_S3_PRIVATE_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

            AWS_S3_PRIVATE_ENDPOINT = s3_creds["endpoint"]
            AWS_S3_ENDPOINT_URL = f"https://{AWS_S3_PRIVATE_ENDPOINT}"

            # in deployed environments, the internal & external endpoint URLs are the same
            AWS_S3_PRIVATE_INTERNAL_ENDPOINT = AWS_S3_ENDPOINT_URL
            AWS_S3_PRIVATE_EXTERNAL_ENDPOINT = AWS_S3_ENDPOINT_URL

            AWS_PRIVATE_LOCATION = "static"
            AWS_PRIVATE_DEFAULT_ACL = "private"
            # If wrong, https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html#canned-acl

            MEDIA_URL = (
                f"https://{AWS_S3_PRIVATE_CUSTOM_DOMAIN}/{AWS_PRIVATE_LOCATION}/"
            )

        elif service["instance_name"] == "backups":
            s3_creds = service["credentials"]
            # Used for backing up the database https://django-dbbackup.readthedocs.io/en/master/storage.html#id2
            DBBACKUP_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
            DBBACKUP_STORAGE_OPTIONS = {
                "access_key": s3_creds["access_key_id"],
                "secret_key": s3_creds["secret_access_key"],
                "bucket_name": s3_creds["bucket"],
                "default_acl": "private",  # type: ignore
            }

    # secure headers
    MIDDLEWARE.append("csp.middleware.CSPMiddleware")
    # see settings options https://django-csp.readthedocs.io/en/latest/configuration.html#configuration-chapter
    bucket = f"{STATIC_URL}"
    allowed_sources = (
        "'self'",
        bucket,
        "https://idp.int.identitysandbox.gov/",
        "https://dap.digitalgov.gov",
        "https://www.google-analytics.com",
        "https://www.googletagmanager.com/",
    )
    CSP_DEFAULT_SRC = allowed_sources
    CSP_DATA_SRC = allowed_sources
    CSP_SCRIPT_SRC = allowed_sources
    CSP_CONNECT_SRC = allowed_sources
    CSP_IMG_SRC = allowed_sources
    CSP_MEDIA_SRC = allowed_sources
    CSP_FRAME_SRC = allowed_sources
    CSP_FONT_SRC = ("'self'", bucket)
    CSP_WORKER_SRC = allowed_sources
    CSP_FRAME_ANCESTORS = allowed_sources
    CSP_STYLE_SRC = allowed_sources
    CSP_INCLUDE_NONCE_IN = ["script-src"]
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    X_FRAME_OPTIONS = "DENY"

    CORS_ALLOWED_ORIGINS = [
        f"https://{AWS_S3_CUSTOM_DOMAIN}",
        env.str("DJANGO_BASE_URL"),
    ]
    CORS_ALLOW_METHODS = ["GET", "OPTIONS"]

    for service in vcap["aws-rds"]:
        if service["instance_name"] == "fac-db":
            rds_creds = service["credentials"]

    # used for psycopg2 cursor connection
    CONNECTION_STRING = (
        "dbname='{}' user='{}' port='{}' host='{}' password='{}'".format(
            rds_creds["db_name"],
            rds_creds["username"],
            rds_creds["port"],
            rds_creds["host"],
            rds_creds["password"],
        )
    )
    # Will not be enabled in cloud environments
    DISABLE_AUTH = False


ADMIN_URL = "admin/"


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST FRAMEWORK
API_VERSION = "0"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "TEST_REQUEST_RENDERER_CLASSES": [
        "rest_framework.renderers.MultiPartRenderer",
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.TemplateHTMLRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "TEST_REQUEST_DEFAULT_FORMAT": "api",
}

# SAM.gov API
SAM_API_URL = "https://api.sam.gov/entity-information/v3/entities"
SAM_API_KEY = secret("SAM_API_KEY")

# Data/schema directories
DATA_FIXTURES = BASE_DIR / "data_fixtures"
AUDIT_TEST_DATA_ENTRY_DIR = DATA_FIXTURES / "audit" / "test_data_entries"
AUDIT_SCHEMA_DIR = BASE_DIR / "schemas" / "output" / "audit"
SECTION_SCHEMA_DIR = BASE_DIR / "schemas" / "output" / "sections"
OUTPUT_BASE_DIR = BASE_DIR / "schemas" / "output" / "base"
SCHEMA_BASE_DIR = BASE_DIR / "schemas" / "source" / "base"
XLSX_TEMPLATE_JSON_DIR = BASE_DIR / "schemas" / "output" / "excel" / "json"
XLSX_TEMPLATE_SHEET_DIR = BASE_DIR / "schemas" / "output" / "excel" / "xlsx"

AV_SCAN_URL = env.str("AV_SCAN_URL", "")
AV_SCAN_MAX_ATTEMPTS = 10

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "users.auth.FACAuthenticationBackend",
]

env_base_url = env.str("DJANGO_BASE_URL", "")
login_client_id = secret("LOGIN_CLIENT_ID", "")
secret_login_key = b64decode(secret("DJANGO_SECRET_LOGIN_KEY", ""))

# which provider to use if multiple are available
# (code does not currently support user selection)
OIDC_ACTIVE_PROVIDER = "login.gov"
OIDC_DISCOVERY_URL = "https://idp.int.identitysandbox.gov"

if ENVIRONMENT == "PRODUCTION":
    OIDC_DISCOVERY_URL = "https://secure.login.gov"

OIDC_PROVIDERS = {
    "login.gov": {
        "srv_discovery_url": OIDC_DISCOVERY_URL,
        "behaviour": {
            # the 'code' workflow requires direct connectivity from us to Login.gov
            "response_type": "code",
            "scope": ["email", "profile:name", "phone", "all_emails"],
            "user_info_request": [
                "email",
                "first_name",
                "last_name",
                "phone",
                "all_emails",
            ],
            "acr_value": "http://idmanagement.gov/ns/assurance/ial/1",
        },
        "client_registration": {
            "client_id": login_client_id,
            "redirect_uris": [f"{env_base_url}/openid/callback/login/"],
            "post_logout_redirect_uris": [f"{env_base_url}/openid/callback/logout/"],
            "token_endpoint_auth_method": ["private_key_jwt"],
            "sp_private_key": secret_login_key,
        },
    }
}

LOGIN_URL = f"{env_base_url}/openid/login/"

USER_PROMOTION_COMMANDS_ENABLED = ENVIRONMENT in ["LOCAL", "TESTING", "UNDEFINED"]

if DISABLE_AUTH:
    TEST_USERNAME = "test_user@test.test"
    MIDDLEWARE.append(
        "users.middleware.authenticate_test_user",
    )

    AUTHENTICATION_BACKENDS = [
        "users.auth.FACTestAuthenticationBackend",
    ]

# A dictionary mapping agency number to agency name. dict[str, str]
AGENCY_NAMES = get_agency_names()
GAAP_RESULTS = get_audit_info_lists("gaap_results")
SP_FRAMEWORK_BASIS = get_audit_info_lists("sp_framework_basis")
SP_FRAMEWORK_OPINIONS = get_audit_info_lists("sp_framework_opinions")
STATE_ABBREVS = json.load(open(f"{SCHEMA_BASE_DIR}/States.json"))[
    "UnitedStatesStateAbbr"
]
CHARACTER_LIMITS_GENERAL = json.load(
    open(f"{SCHEMA_BASE_DIR}/character_limits/general.json")
)

ENABLE_DEBUG_TOOLBAR = (
    env.bool("ENABLE_DEBUG_TOOLBAR", False) and ENVIRONMENT == "LOCAL" and not TEST_RUN
)

# Django debug toolbar setup
if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE
    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda _: True}

# Link to the most applicable static site URL. Passed in context to all templates.
STATIC_SITE_URL = "https://fac.gov/"

# OMB-assigned values. Number doesn't change, date does.
OMB_NUMBER = "3090-0330"
OMB_EXP_DATE = "09/30/2026"

# APP-level constants
CENSUS_DATA_SOURCE = "CENSUS"
DOLLAR_THRESHOLD = 750000
SUMMARY_REPORT_DOWNLOAD_LIMIT = 1000
DEFAULT_MAX_ROWS = (
    10000  # A version of this constant also exists in schemas.scrpits.render.py
)
MAX_ROWS = 20000

# A version of these regexes also exists in Base.libsonnet
REGEX_ALN_PREFIX = r"^([0-9]{2})$"
REGEX_RD_EXTENSION = r"^RD[0-9]?$"
REGEX_THREE_DIGIT_EXTENSION = r"^[0-9]{3}[A-Za-z]{0,1}$"
REGEX_U_EXTENSION = r"^U[0-9]{2}$"
EMPLOYER_IDENTIFICATION_NUMBER = r"^[0-9]{9}$"
GSA_MIGRATION = "GSA_MIGRATION"  # There is a copy of `GSA_MIGRATION` in Base.libsonnet. If you change it here, change it there too.
GSA_MIGRATION_INT = -999999999
# A copy of theses constants exists in schema/source/base/Base.libsonnet
STATE_CLUSTER = "STATE CLUSTER"
OTHER_CLUSTER = "OTHER CLUSTER NOT LISTED ABOVE"
NOT_APPLICABLE = "N/A"
GSA_FAC_WAIVER = "GSA_FAC_WAIVER"
ONE_TIME_ACCESS_TTL_SECS = 60

# Expire sessions after 30 minutes
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-age
SESSION_COOKIE_AGE = 30 * 60
# Keep sessions alive if the user is active
# https://docs.djangoproject.com/en/dev/ref/settings/#session-save-every-request
SESSION_SAVE_EVERY_REQUEST = True
