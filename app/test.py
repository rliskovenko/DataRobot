import random
import string
import app
import unittest


class DataRobotTestCase( unittest.TestCase ):
    def __dbNameGen(self):
        return 'test' + ''.join( random.SystemRandom().choice( string.ascii_uppercase + string.digits ) for _ in range( 8 ) )

    def setUp(self):
        app.MONGODB_HOST = 'localhost'
        app.MONGODB_PORT = 27017
        app.MONGODB_DB = self.__dbNameGen()
        app.TESTING = True

    def tearDown(self):
        app.connection.drop_database( app.MONGODB_DB )

if __name__ == '__main__':
    unittest.main()
