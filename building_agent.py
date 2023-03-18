#!/usr/bin/env python3.6
import argparse
from flask import Flask, request, send_from_directory
import json
import sys
import subprocess as sp
import threading

app = Flask( __name__, static_url_path='' )

@app.route( '/build_catridge/<game_id>', methods = ['POST'] )
def build_catridge( game_id ):
    '''Has to be called with POST request which
       sends config file and game files (if any)'''
    data = request.form
    # TODO: parse config file
    # TODO: save config file and game files (if any)
    # TODO: save game catridge data to database
    # TODO: construct Dockerfile
    # TODO: schedule building in thread (push notification when finished)
    return None # success and Dockerfile as JSON

@app.route( '/query/<query_string>' )
def query( query_string ):
    ''' Query the database and return matching catridges '''
    # TODO: query database
    return None # result as JSON


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument( "--rest", const=True, nargs='?', type=bool, help="Specify if the agent shoud be start as a RESTful server." )
    args = parser.parse_args()

    REST = bool( args.rest )

    # TODO: specify port
    app.run()
