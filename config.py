#!/usr/bin/env python3.6
import json
import os

class configuration:
    def __init__( self, path=os.path.join( "config", 'organization.json' ) ):
        with open( path ) as fh:
            conf = json.load( fh )
        for k, v in conf.items():
            self.__dict__[ k ] = v

    def __repr__( self ):
        return repr( self.__dict__ )

if __name__ == '__main__':
    c = configuration()
    print( c )
    
