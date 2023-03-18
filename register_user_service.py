#!/usr/bin/env python3.6
from flask import Flask
import sys
import subprocess as sp

from config import configuration

app = Flask( __name__ )

@app.route('/register/<username>/<password>')
def register( username, password ):
    with sp.Popen(  [ 'prosodyctl', 'register', username, CONF.xmpp_server, password ], stdout=sp.PIPE, stderr=sp.PIPE ) as p_reg:
        output = [ str( i ) for i in p_reg.stdout ]
        print( output )
        try:
            if 'successfully registered' in output[ 0 ]:
                return 'OK'
            else:
                return 'Error registering. Try another username.'
        except:
            return "Error registering."

if __name__ == '__main__':
    CONF = configuration()
    app.run( host="0.0.0.0", port=CONF.xmpp_register_port, ssl_context='adhoc' )
