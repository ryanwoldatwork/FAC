from configurations import pristinemethod
from .base import Base
import logging
import os
from base64 import b64decode

class Local(Base):
   
    @classmethod
    def setup(cls):
        super(Local, cls).setup()
        logging.info("Local(Base) config class setup()")
        # Quick-start development settings - unsuitable for production
        # See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/
        # SECURITY WARNING: keep the secret key used in production secret!
        cls.secret = pristinemethod(lambda a, b=None: os.environ.get(a, b))
        cls.secret_login_key = b64decode(cls.secret("DJANGO_SECRET_LOGIN_KEY", ""))
        cls.SECRET_KEY = cls.secret("SECRET_KEY")

        cls.SAM_API_KEY = cls.secret("SAM_API_KEY")
        cls.login_client_id = cls.secret("LOGIN_CLIENT_ID", "")
        
        Base.build_oidc_providers(Local, cls.secret_login_key)

        cls.ALLOWED_HOSTS = cls.env("ALLOWED_HOSTS", "0.0.0.0 127.0.0.1 localhost").split()



        DEBUG = cls.env.bool("DJANGO_DEBUG", default=True)
        cls.CORS_ALLOWED_ORIGINS += ["http://0.0.0.0:8000", "http://127.0.0.1:8000"]

        cls.MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")

        # FIXME: 
        # django.core.exceptions.ImproperlyConfigured: DEFAULT_FILE_STORAGE/STORAGES are mutually exclusive.
        # cls.STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
        # cls.DEFAULT_FILE_STORAGE = "report_submission.storages.S3PrivateStorage"

        # Private bucket
        cls.AWS_PRIVATE_STORAGE_BUCKET_NAME = "gsa-fac-private-s3"
        # Private CENSUS_TO_GSAFAC bucket
        cls.AWS_CENSUS_TO_GSAFAC_BUCKET_NAME = "fac-census-to-gsafac-s3"

        cls.AWS_S3_PRIVATE_REGION_NAME = os.environ.get(
            "AWS_S3_PRIVATE_REGION_NAME", "us-east-1"
        )

        # MinIO only matters for local development and GitHub action environments.
        # These should match what we're setting in backend/run.sh
        cls.AWS_PRIVATE_ACCESS_KEY_ID = os.environ.get("AWS_PRIVATE_ACCESS_KEY_ID", "longtest")
        cls.AWS_PRIVATE_SECRET_ACCESS_KEY = os.environ.get(
            "AWS_PRIVATE_SECRET_ACCESS_KEY", "longtest"
        )
        cls.AWS_S3_PRIVATE_ENDPOINT = os.environ.get(
            "AWS_S3_PRIVATE_ENDPOINT", "http://minio:9000"
        )
        cls.AWS_PRIVATE_DEFAULT_ACL = "private"

        cls.AWS_S3_ENDPOINT_URL = cls.AWS_S3_PRIVATE_ENDPOINT

        # when running locally, the internal endpoint (docker network) is different from the external endpoint (host network)
        cls.AWS_S3_PRIVATE_INTERNAL_ENDPOINT = cls.AWS_S3_ENDPOINT_URL
        cls.AWS_S3_PRIVATE_EXTERNAL_ENDPOINT = "http://localhost:9001"

        cls.DISABLE_AUTH = cls.env.bool("DISABLE_AUTH", default=False)

        # Used for backing up the database https://django-dbbackup.readthedocs.io/en/master/installation.html
        cls.DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
        cls.DBBACKUP_STORAGE_OPTIONS = {"location": cls.BASE_DIR / "backup"}

        #     USER_PROMOTION_COMMANDS_ENABLED = ENVIRONMENT in ["LOCAL", "TESTING", "UNDEFINED"]
        cls.USER_PROMOTION_COMMANDS_ENABLED = True

        cls.TEST_USERNAME = "test_user@test.test"
        cls.MIDDLEWARE.append(
            "users.middleware.authenticate_test_user",
        )
        cls.AUTHENTICATION_BACKENDS = [
            "users.auth.FACTestAuthenticationBackend",
        ]

        cls.ENABLE_DEBUG_TOOLBAR = (
            cls.env.bool("ENABLE_DEBUG_TOOLBAR", False) and not cls.TEST_RUN
        )
