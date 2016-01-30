"""
    Microservice for writing JSON data to MongoDB.

    For DataRobot

    :license: BSD, see LICENSE for more details.
"""

from flask import Flask, request
from mongokit import Connection, Document
from werkzeug import exceptions as wExceptions
import datetime
import sys
import hashlib
import json

# Configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'docs'
MONGODB_COLLECTION = 'docs'
# JSON fields should be ordered before MD5
JSON_ORDERED = False
JSON_ORDER_ALNUM = False
JSON_FIELD_ORDER = [ 'date', 'uid', 'name' ]

# Create Flask app
app = Flask( __name__ )
app.config.from_object( __name__ )
app.debug = True

# Connect to DB
connection = Connection( app.config['MONGODB_HOST'], app.config['MONGODB_PORT'] )


def md5validator( obj, v ):
    return True

@connection.register
class Doc( Document ):
    structure = {
        'uid' : unicode,
        'name' : unicode,
        'date' : unicode,
        'md5checksum' : unicode
    }

    required_fields = [ 'uid', 'name', 'date', 'md5checksum' ]

    def validate( self, *args, **kwargs ):
        m = hashlib.md5()
        ref = self['md5checksum']
        clone = self
        clone.__delitem__( 'md5checksum' )

        m.update( json.dumps( clone ) )
        calc = m.hexdigest()
        return ref == calc


@app.route( '/', methods=[ 'POST' ] )
def add_rec():
    try:
        collection = connection[ app.config['MONGODB_DB']][ app.config['MONGODB_COLLECTION']]
        d = request.json

        if d and isinstance( d, list ):
            for item in d:
                doc = collection.Doc()
                for ( k, v ) in item.iteritems():
                    doc[k] = v
                doc.save()
        elif d and isinstance( d, dict ):
            doc = collection.Doc()
            for ( k, v ) in d.iteritems():
                doc[k] = v
            doc.save()
    except wExceptions.BadRequest:
        return json.dumps( { "status": "ERROR", "info": "Bad request" } )
    except Exception:
        return json.dumps( { "status": "ERROR", "info": sys.exc_info().__str__() } )

    return json.dumps( { "status": "OK" } )


@app.route( '/<uid>/<date>', methods=[ 'GET' ] )
def get_rec(uid, date):
    try:
        collection = connection[ app.config['MONGODB_DB']][ app.config['MONGODB_COLLECTION']]
        item = list( collection.Doc.find() )

        return json.dumps( { "status": "OK", item: item } )
    except Exception:
        return json.dumps( { "status": "ERROR", "info": sys.exc_info().__str__() } )