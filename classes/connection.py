import pymel.core as pm
import sys
import pymongo
import pymongo.errors
import logging

logger = logging.getLogger(__name__)

class Singleton(type):
    """ Simple Singleton that keep only one value for all instances
    """
    def __init__(cls, name, bases, dic):
        super(Singleton, cls).__init__(name, bases, dic)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance


class MongoDBConnection(object):
    __metaclass__ = Singleton

    def __init__(self, databaseIP='localhost', databasePort=27017, databaseName='lcPipeline'):

        client = _connectToClient(databaseIP=databaseIP, databasePort=databasePort)
        self.db = client[databaseName]


def _connectToClient(databaseIP, databasePort):
    try:
        client = pymongo.MongoClient(databaseIP, databasePort, serverSelectionTimeoutMS=5000, socketTimeoutMS=5000)
        client.server_info()
        return client
    except pymongo.errors.ServerSelectionTimeoutError as err:
        resp = pm.confirmDialog(title='Error', message='No Database Connection Found!', button=['OK'], defaultButton='Ok',
                     dismissString='Ok')
        if resp == 'Ok':
            sys.exit()


