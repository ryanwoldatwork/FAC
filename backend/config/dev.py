from .cloudgov import CGov
import logging

class Dev(CGov):
    DEBUG = True

    @classmethod
    def pre_setup(cls):
        super(Dev, cls).pre_setup()

    @classmethod
    def setup(cls):
        super(Dev, cls).setup()
        logging.info("Dev(CF) config class setup()")
