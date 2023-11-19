from configurations import pristinemethod
from .base import Base
import logging
import newrelic.agent
from cfenv import AppEnv
import json
from base64 import b64decode

class CGov(Base):
    
    @classmethod
    def pre_setup(cls):
        super(CGov, cls).pre_setup()

    @classmethod
    def setup(cls):
        super(CGov, cls).setup()
        logging.info("CF(Base) config class setup()")
        cls.key_service = AppEnv().get_service(name="fac-key-service")
        cls.secret = pristinemethod(lambda a, b=None: cls.key_service.credentials.get(a, b))
        cls.secret_login_key = b64decode(cls.secret("DJANGO_SECRET_LOGIN_KEY", ""))
        cls.SAM_API_KEY = cls.secret("SAM_API_KEY")
        cls.login_client_id = cls.secret("LOGIN_CLIENT_ID", "")
        Base.build_oidc_providers(CGov, cls.secret_login_key)

        # Always initialize the newrelic agent
        newrelic.agent.initialize()
        cls.SECRET_KEY = cls.key_service("SECRET_KEY")
        cls.ALLOWED_HOSTS = cls.secret("ALLOWED_HOSTS", "0.0.0.0 127.0.0.1 localhost").split()

        # cls.STATICFILES_STORAGE = "storages.backends.s3boto3.S3ManifestStaticStorage"
        # cls.DEFAULT_FILE_STORAGE = "report_submission.storages.S3PrivateStorage"
        vcap = json.loads(cls.env.str("VCAP_SERVICES"))
        # FIXME: There should be error handling around that env call...
        for service in vcap["s3"]:
            if service["instance_name"] == "fac-public-s3":
                # Public AWS S3 bucket for the app
                s3_creds = service["credentials"]

                cls.AWS_ACCESS_KEY_ID = s3_creds["access_key_id"]
                cls.AWS_SECRET_ACCESS_KEY = s3_creds["secret_access_key"]
                cls.AWS_STORAGE_BUCKET_NAME = s3_creds["bucket"]

                cls.AWS_S3_REGION_NAME = s3_creds["region"]
                cls.AWS_DEFAULT_REGION = s3_creds["region"]

                cls.AWS_S3_CUSTOM_DOMAIN = (
                    f"{cls.AWS_STORAGE_BUCKET_NAME}.s3-{cls.AWS_S3_REGION_NAME}.amazonaws.com"
                )
                cls.AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

                cls.AWS_LOCATION = "static"
                cls.AWS_QUERYSTRING_AUTH = False
                cls.AWS_DEFAULT_ACL = "public-read"
                cls.STATIC_URL = f"https://{cls.AWS_S3_CUSTOM_DOMAIN}/{cls.AWS_LOCATION}/"

                cls.STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
                cls.AWS_IS_GZIPPED = True

            # FIXME: Why are we doing this based on the instance?
            # Is there a better way to store these credentials/configure this?
            elif service["instance_name"] == "fac-private-s3":
                # Private AWS S3 bucket for the app's Excel (or other file) uploads
                s3_creds = service["credentials"]

                cls.AWS_PRIVATE_ACCESS_KEY_ID = s3_creds["access_key_id"]
                cls.AWS_PRIVATE_SECRET_ACCESS_KEY = s3_creds["secret_access_key"]
                cls.AWS_PRIVATE_STORAGE_BUCKET_NAME = s3_creds["bucket"]

                cls.AWS_S3_PRIVATE_REGION_NAME = s3_creds["region"]
                cls.AWS_S3_PRIVATE_CUSTOM_DOMAIN = f"{cls.AWS_PRIVATE_STORAGE_BUCKET_NAME}.s3-{cls.AWS_S3_PRIVATE_REGION_NAME}.amazonaws.com"
                cls.AWS_S3_PRIVATE_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

                cls.AWS_S3_PRIVATE_ENDPOINT = s3_creds["endpoint"]
                cls.AWS_S3_ENDPOINT_URL = f"https://{cls.AWS_S3_PRIVATE_ENDPOINT}"

                # in deployed environments, the internal & external endpoint URLs are the same
                cls.AWS_S3_PRIVATE_INTERNAL_ENDPOINT = cls.AWS_S3_ENDPOINT_URL
                cls.AWS_S3_PRIVATE_EXTERNAL_ENDPOINT = cls.AWS_S3_ENDPOINT_URL

                cls.AWS_PRIVATE_LOCATION = "static"
                cls.AWS_PRIVATE_DEFAULT_ACL = "private"
                # If wrong, https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html#canned-acl

                cls.MEDIA_URL = (
                    f"https://{cls.AWS_S3_PRIVATE_CUSTOM_DOMAIN}/{cls.AWS_PRIVATE_LOCATION}/"
                )

            elif service["instance_name"] == "backups":
                s3_creds = service["credentials"]
                # Used for backing up the database https://django-dbbackup.readthedocs.io/en/master/storage.html#id2
                cls.DBBACKUP_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
                cls.DBBACKUP_STORAGE_OPTIONS = {
                    "access_key": s3_creds["access_key_id"],
                    "secret_key": s3_creds["secret_access_key"],
                    "bucket_name": s3_creds["bucket"],
                    "default_acl": "private",  # type: ignore
                }

        # secure headers
        cls.MIDDLEWARE.append("csp.middleware.CSPMiddleware")
        # see settings options https://django-csp.readthedocs.io/en/latest/configuration.html#configuration-chapter
        bucket = f"{cls.STATIC_URL}"
        allowed_sources = (
            "'self'",
            bucket,
            "https://idp.int.identitysandbox.gov/",
            "https://dap.digitalgov.gov",
            "https://www.google-analytics.com",
            "https://www.googletagmanager.com/",
        )
        cls.CSP_DEFAULT_SRC = allowed_sources
        cls.CSP_DATA_SRC = allowed_sources
        cls.CSP_SCRIPT_SRC = allowed_sources
        cls.CSP_CONNECT_SRC = allowed_sources
        cls.CSP_IMG_SRC = allowed_sources
        cls.CSP_MEDIA_SRC = allowed_sources
        cls.CSP_FRAME_SRC = allowed_sources
        cls.CSP_FONT_SRC = ("'self'", bucket)
        cls.CSP_WORKER_SRC = allowed_sources
        cls.CSP_FRAME_ANCESTORS = allowed_sources
        cls.CSP_STYLE_SRC = allowed_sources
        cls.CSP_INCLUDE_NONCE_IN = ["script-src"]
        cls.CSRF_COOKIE_SECURE = True
        cls.CSRF_COOKIE_HTTPONLY = True
        cls.SESSION_COOKIE_SECURE = True
        cls.SESSION_COOKIE_HTTPONLY = True
        cls.SESSION_COOKIE_SAMESITE = "Lax"
        cls.X_FRAME_OPTIONS = "DENY"

        cls.CORS_ALLOWED_ORIGINS = [
            f"https://{cls.AWS_S3_CUSTOM_DOMAIN}",
            cls.env.str("DJANGO_BASE_URL"),
        ]
        cls.CORS_ALLOW_METHODS = ["GET", "OPTIONS"]

        for service in vcap["aws-rds"]:
            if service["instance_name"] == "fac-db":
                rds_creds = service["credentials"]

        # used for psycopg2 cursor connection
        cls.CONNECTION_STRING = (
            "dbname='{}' user='{}' port='{}' host='{}' password='{}'".format(
                rds_creds["db_name"],
                rds_creds["username"],
                rds_creds["port"],
                rds_creds["host"],
                rds_creds["password"],
            )
        )

        # FIXME: The comment below makes no sense.
        # Comments throughout the config need significant improvement.
        # Will not be enabled in cloud environments
        cls.DISABLE_AUTH = False

        # Remove once all Census data has been migrated
        # Add these as env vars, look at the bucket for values
        cls.AWS_CENSUS_ACCESS_KEY_ID = cls.secret("AWS_CENSUS_ACCESS_KEY_ID", "")
        cls.AWS_CENSUS_SECRET_ACCESS_KEY = cls.secret("AWS_CENSUS_SECRET_ACCESS_KEY", "")
        cls.AWS_CENSUS_STORAGE_BUCKET_NAME = cls.secret("AWS_CENSUS_STORAGE_BUCKET_NAME", "")
        cls.AWS_S3_CENSUS_REGION_NAME = cls.secret("AWS_S3_CENSUS_REGION_NAME", "")
