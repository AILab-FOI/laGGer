#!/usr/bin/env python3.6
from flask import Flask
import sys
import json
from base64 import b64encode, b64decode
from config import configuration

CONF = configuration()

app = Flask( __name__ )

@app.route('/encrypt/<plaintext>/<password>')
def encrypt( plaintext, password ):
    res = šifriraj( password, b64enc( plaintext ) )
    try:
        return json.dumps( { "result":res ) } )
    except Exception as e:
        print( e )
        return json.dumps( { "result":"Error" } )

@app.route('/decrypt/<cyphertext>/<password>')
def decrypt( cyphertext, password ):
    try:
        res = b64dec( dešifriraj( password, cyphertext ) )
        return json.dumps( { "result":res } )
    except Exception as e:
        print( e )
        return json.dumps( { "result":"Error" } )

def b64dec( text ):
    return b64decode( text.translate( text.maketrans( ABECEDA, B64 ) ).encode() ).decode( 'utf-8' )
    
def b64enc( text ):
    x = b64encode( text.encode() )
    return bytes( str( x )[ 2:-1 ].translate( str( x )[ 2:-1 ].maketrans( B64, ABECEDA ) ), 'utf-8' ).decode( 'utf-8' )


B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
abeceda = ' abcćčdđefghijklmnoprsštuvzžABCĆČDĐEFGHIJKLMNOPRSŠTUVZŽ'
abeceda_digrafi = 'abcćčdđ\u01C6efghijkl\u01c9mn\u01ccoprsštuvzžABCĆČDĐ\u01c4EFGHIJKL\u01c7MN\u01caOPRSŠTUVZŽ 123'

ABECEDA = abeceda_digrafi

def šifriraj( ključ, tekst ):
    šifrat = ""
    for indeks, slovo in enumerate( tekst ):
        šifrat += ABECEDA[ ( ABECEDA.index( slovo ) + ABECEDA.index( ključ[ indeks % len( ključ ) ] ) ) % len( ABECEDA )]

    return šifrat

def dešifriraj( ključ, šifrat ):
    tekst = ""
    for indeks, slovo in enumerate( šifrat ):
        tekst += ABECEDA[ ( ABECEDA.index( slovo ) - ABECEDA.index( ključ[ indeks % len( ključ ) ] ) ) % len( ABECEDA )]

    return tekst

if __name__ == '__main__':
    app.run( host="0.0.0.0", port=CONF.crypto_service_port, ssl_context='adhoc' )
