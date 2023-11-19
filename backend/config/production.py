from .cloudgov import CGov
import logging

class Production(CGov):

    @classmethod
    def setup(cls):
        super(Production, cls).setup()
        logging.info("Production(CF) config class setup()")
        logging.info('production settings loaded: %s', cls)

        cls.OIDC_DISCOVERY_URL = "https://secure.login.gov"
