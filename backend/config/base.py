from configurations import (
    Configuration,
    pristinemethod
    )
import environs
import logging
import sys
import os
from audit.get_agency_names import get_agency_names, get_audit_info_lists
import json

# Anything in Base should apply to all environments
# Dev and Staging can override things. Production
# should not have to override anything from Base.
class Base(Configuration):
    DEBUG = False
    BASE_DIR = environs.Path(__file__).resolve(strict=True).parent.parent
    SECRET_KEY = None
    env = environs.Env()

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
        # "data_distro",
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
                    "report_submission.context_processors.certifiers_emails_must_not_match",
                ],
                "builtins": [
                    "report_submission.templatetags.get_attr",
                ],
            },
        },
    ]

    WSGI_APPLICATION = "config.wsgi.application"


    # Database
    # https://docs.djangoproject.com/en/4.0/ref/settings/#databases

    DATABASES = {
        "default": env.dj_db_url(
            "DATABASE_URL", default="postgres://postgres:password@0.0.0.0/backend"
        ),
        "census-to-gsafac-db": env.dj_db_url(
            "DATABASE_URL_CENSUS_TO_GSAFAC_DB",
            default="postgres://postgres:password@0.0.0.0/census-to-gsafac-db",
        ),
    }

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

    # Data/schema directories
    DATA_FIXTURES = BASE_DIR / "data_fixtures"
    AUDIT_TEST_DATA_ENTRY_DIR = DATA_FIXTURES / "audit" / "test_data_entries"
    AUDIT_SCHEMA_DIR = BASE_DIR / "schemas" / "output" / "audit"
    SECTION_SCHEMA_DIR = BASE_DIR / "schemas" / "output" / "sections"
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

    # which provider to use if multiple are available
    # (code does not currently support user selection)
    OIDC_ACTIVE_PROVIDER = "login.gov"
    OIDC_DISCOVERY_URL = "https://idp.int.identitysandbox.gov"


    LOGIN_URL = f"{env_base_url}/openid/login/"

    USER_PROMOTION_COMMANDS_ENABLED = False


    # FIXME: https://django-configurations.readthedocs.io/en/latest/patterns.html#pristine-methods
    # A dictionary mapping agency number to agency name. dict[str, str]
    AGENCY_NAMES = get_agency_names()
    GAAP_RESULTS = get_audit_info_lists("gaap_results")
    SP_FRAMEWORK_BASIS = get_audit_info_lists("sp_framework_basis")
    SP_FRAMEWORK_OPINIONS = get_audit_info_lists("sp_framework_opinions")
    STATE_ABBREVS = json.load(open(f"{SCHEMA_BASE_DIR}/States.json"))[
        "UnitedStatesStateAbbr"
    ]

    # Link to the most applicable static site URL. Passed in context to all templates.
    STATIC_SITE_URL = "https://fac.gov/"

    # OMB-assigned values. Number doesn't change, date does.
    OMB_NUMBER = "3090-0330"
    OMB_EXP_DATE = "09/30/2026"

    ENABLE_DEBUG_TOOLBAR = False
    

    @classmethod
    def pre_setup(cls):
        super(Base, cls).pre_setup()
        # FIXME this might not be needed now.
        cls.ENVIRONMENT = cls.env.str("ENV", "UNDEFINED").upper()
        # By default, only allow connections from the local machine
        cls.ALLOWED_HOSTS = cls.env("ALLOWED_HOSTS", "127.0.0.1 localhost").split()


    def build_oidc_providers(cls, secret_login_key):
        # FIXME: We may have a sequencing issue on the discovery URL
        # for production environments using this config mechanism.
        cls.OIDC_PROVIDERS = {
            "login.gov": {
                "srv_discovery_url": cls.OIDC_DISCOVERY_URL,
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
                    "client_id": cls.login_client_id,
                    "redirect_uris": [f"{cls.env_base_url}/openid/callback/login/"],
                    "post_logout_redirect_uris": [f"{cls.env_base_url}/openid/callback/logout/"],
                    "token_endpoint_auth_method": ["private_key_jwt"],
                    "sp_private_key": secret_login_key,
                },
            }
        }
    
    @classmethod
    def setup(cls):
        super(Base, cls).setup()
        logging.info("Base(Configuration) config class setup()")
        # SAM.gov API
        cls.SAM_API_URL = "https://api.sam.gov/entity-information/v3/entities"
    # Django debug toolbar setup
    if ENABLE_DEBUG_TOOLBAR:
        INSTALLED_APPS += [
            "debug_toolbar",
        ]
        MIDDLEWARE = [
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ] + MIDDLEWARE
        DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda _: True}
