"""
    Microservice for writing JSON data to MongoDB.

    For DataRobot

    :license: BSD, see LICENSE for more details.
"""

from flask import Flask, request
from mongokit import Connection, Document
from werkzeug import exceptions as wExceptions
from datetime import datetime
import sys
import hashlib
import json

# Configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'docs'
MONGODB_COLLECTION = 'docs'
# JSON fields should be ordered before MD5
# Temporary disabled
# JSON_ORDERED = False
# JSON_ORDER_ALNUM = False
# JSON_FIELD_ORDER = [ 'date', 'uid', 'name' ]

# Create Flask app
app = Flask( __name__ )
app.config.from_object( __name__ )
app.debug = True

# Connect to DB
connection = Connection( app.config['MONGODB_HOST'], app.config['MONGODB_PORT'] )
docsCollection = connection[ app.config['MONGODB_DB']][ app.config['MONGODB_COLLECTION']]


def _saver( collection, item ):
    doc = collection.Doc()
    for ( k, v ) in item.iteritems():
        doc[k] = v

    return doc.save()


def json_load( data ):
    return json.loads( data )


def json_dump( data ):
    return json.dumps( data )


@connection.register
class Doc( Document ):
    structure = {
        'uid' : unicode,
        'name' : unicode,
        'date' : unicode
    }

    required_fields = [ 'uid', 'name', 'date' ]

    def validate( self, *args, **kwargs ):
        isOK = True
        m = hashlib.md5()
        ref = self['md5checksum']
        clone = self
        clone.__delitem__( 'md5checksum' )

        m.update( json.dumps( clone ) )
        calc = m.hexdigest()
        isOK = ( ref == calc )

        try:
            d = datetime.strptime( self['date'], "%Y-%m-%dT%H:%M:%S.%f" )
        except:
            isOK = False

        return isOK


@app.route( '/', methods=[ 'POST' ] )
def add_rec():
    try:
        d = request.json
        res = dict()

        # We don't need else section, valid JSON could be list/dict only
        if d and isinstance( d, list ):
            for item in d:
                res[ item['uid'] ] = _saver( docsCollection, item )
        elif d and isinstance( d, dict ):
            res[ d['uid'] ] = _saver( docsCollection, d )
    except wExceptions.BadRequest:
        return json.dumps( { "status": "ERROR", "info": "Bad request" } )
    except Exception:
        return json.dumps( { "status": "ERROR", "info": sys.exc_info().__str__() } )

    return json_dump( { "status": "OK", "info": res } )


@app.route( '/<uid>/<date>', methods=[ 'GET' ] )
def get_rec(uid, date):
    try:
        item = list(docsCollection.Doc.find())

        return json_dump( { "status": "OK", item: item } )
    except Exception:
        return json_dump( { "status": "ERROR", "info": sys.exc_info().__str__() } )