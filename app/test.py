import random
import string
import app
import json
import unittest
from datetime import datetime


App = app.app

testSet = {
    True : [
        '''[{"date": "2015-05-12T14:36:00.451765",
               "md5checksum": "e8c83e232b64ce94fdd0e4539ad0d44f",
               "name": "John Doe",
               "uid": "1"},
            {"date": "2015-05-13T14:38:00.451765",
                "md5checksum": "b419795d50db2a35e94c8364978d898f",
                "name": "Jane Doe",
                "uid": "2"}]''',
        '''{"date": "2015-05-12T14:37:00.451765",
               "md5checksum": "e8c83e232b64ce94fdd0e4539ad0d44f",
               "name": "Carl Doe",
               "uid": "3"}'''
    ],
    False : [
        '''[{"date": "2015-05-12T14:36:00.451765",
               "md5checksum": "fffffff32b64ce94fdd0e4539ad0d44f",
               "name": "John Doe",
               "uid": "11"},
            {"date": "2015-05-13T14:38:00.451765",
                "md5checksum": "b419795d50db2a35e94c8364978d898f",
                "name": "Jane Doe",
                "uid": "12"}]''',
        '''{"date": "2015-05-12T14:37:00.451765",
               "md5checksum": "ffffff232b64ce94fdd0e4539ad0d44f",
               "name": "Carl Doe",
               "uid": "13"}''',
        '''{"date": "2015-05-14T14:37:00.451765",
               "md5checksum": "ffffff232b64ce94fdd0e4539ad0d44f",
               "name": "Rozalie Doe",
               "uid": "14"}'''
    ]
}

class DataRobotTestCase( unittest.TestCase ):
    def __dbNameGen(self):
        return 'test' + ''.join( random.SystemRandom().choice( string.ascii_uppercase + string.digits ) for _ in range( 8 ) )

    def __test_add( self, data ):
        return self.app.post( '/', data )

    def __test_get( self, data ):
        jsonData = json.loads( data )
        __makeGetUrl = lambda ( x ): '/' + '/'.join( [ x['uid'], datetime.strptime( x['date'], "%Y-%m-%dT%H:%M:%S.%f" ).strftime( "%Y-%m-%d" ) ] )
        if isinstance( jsonData, list ):
            return [ self.app.get( __makeGetUrl( obj ) ) for obj in jsonData ]
        else:
            return self.app.get( __makeGetUrl( jsonData ) )

    def __run_test(self, data=testSet, sub=__test_add ):
        for ( expected, tests ) in data.iteritems():
            for test in tests:
                res = sub( test )
                if isinstance( res, list ):
                    for subRes in res:
                        assert expected == ( 'OK' in json.loads( subRes.data )['status'] )
                else:
                    assert expected == ( 'OK' in json.loads( res.data )['status'] )

    def setUp(self):
        app.MONGODB_HOST = 'localhost'
        app.MONGODB_PORT = 27017
        app.MONGODB_DB = self.__dbNameGen()
        app.TESTING = True
        self.app = App.test_client()

    def tearDown(self):
        app.connection.drop_database( app.MONGODB_DB )

    def test_add(self):
        self.__run_test( testSet, self.__test_add )

    def test_get(self):
        self.__run_test( testSet, self.__test_get )


if __name__ == '__main__':
    unittest.main()
