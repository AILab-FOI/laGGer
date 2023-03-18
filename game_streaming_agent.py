#!/usr/bin/env python3.6
import argparse
import json
import sys
import os
import glob
import subprocess as sp

import warnings
warnings.filterwarnings("ignore")

from talking_agent import TalkingAgent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template

from aiosasl import AuthenticationFailure
from aiohttp import web

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from flask import Flask, request as req, send_from_directory

from base64 import b64encode, b64decode

import _thread

from config import configuration

class XMPPRegisterException( Exception ):
    pass

class CryptoError( Exception ):
    pass


''' USER AND SYSTEM REGISTRATION '''

def register( username, password ):
    url = "https://%s:%d/register/%s/%s" % ( CONF.xmpp_server, CONF.xmpp_register_port, username, password )
    response = requests.get( url, verify=False )

    if response.status_code == 200:
        result = response.content.decode('utf-8')
        print( username, result )
        if result == 'OK':
            return True
        else:
            raise XMPPRegisterException( 'Cannot register user "%s", error from server: %s' % ( username, result ) )
    else:
        raise XMPPRegisterException( 'Error while communicating with server at "%s"' % CONF.xmpp_server )

def register_system():
    try:
        register( CONF.game_streaming_agent, CONF.password )
    except XMPPRegisterException as e:
        print( e )
    try:
        register( CONF.save_game_agent, CONF.password )
    except XMPPRegisterException as e:
        print( e )
    try:
        register( CONF.video_streaming_agent, CONF.password )
    except XMPPRegisterException as e:
        print( e )
    try:
        register( CONF.building_agent, CONF.password )
    except XMPPRegisterException as e:
        print( e )

def encode( text ):
    url = "https://%s:%d/encrypt/%s/%s" % ( CONF.crypto_service_host, CONF.crypto_service_port, text, CONF.crypto_password )
    response = requests.get( url, verify=False )

    if response.status_code == 200:
        result = json.loads( response.content.decode('utf-8') )[ "result" ]
        if result != 'Error':
            return result
        else:
            raise CryptoError( "Error while encoding string: " + text )

'''FLASK APP FOR ARCADE'''
    
app = Flask( __name__, static_url_path='' )
@app.route( '/arcade/<path:path>' )
def arcade( path ):
    return send_from_directory( 'arcade', path )




'''X11Docker AND VNC RELATED FUNCTIONS'''

def run_game( game, port ):
    gconf = configuration( os.path.join( 'catridges', game, 'catridge_template.json' ) )
    with sp.Popen(  [ 'bash', 'run_game.sh', game, str( port ), gconf.resolution ], stdout=sp.PIPE, stderr=sp.STDOUT, bufsize=1 ) as p1, open('logfile_game.txt', 'ab') as file:
        for line in p1.stdout: 
            sys.stdout.buffer.write( line ) 
            file.write( line )

def run_vnc( port1, port2 ):
    abs_dir = os.path.dirname( os.path.realpath( '__file__' ) )
    cert = os.path.join( abs_dir, CONF.cert )
    key = os.path.join( abs_dir, CONF.key )
    print(  [ 'novnc',  '--cert', cert, '--key', key, '--ssl-only', '--listen', str( port2 ), '--vnc', '0.0.0.0:%d' % port1 ] )
    with sp.Popen(  [ 'novnc',  '--cert', cert, '--key', key, '--ssl-only', '--listen', str( port2 ), '--vnc', '0.0.0.0:%d' % port1 ], stdout=sp.PIPE, stderr=sp.STDOUT, bufsize=1 ) as p2, open('logfile_vnc.txt', 'ab') as file:
        for line in p2.stdout: 
            sys.stdout.buffer.write( line ) 
            file.write( line )

'''GAME STREAMING AGENT'''

class GameStreamingAgent( TalkingAgent ):
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        self.web.add_get("/start_catridge", self.start_catridge, template=None )
        self.web.add_get("/list_catridges", self.list_catridges, template='catridges/list.tpl' )
        self.web.app.add_routes( [ web.static( '/catridges', 'catridges') ] )

        self.port = CONF.port_begin

    def rotate_port( self ):
        if self.port >= CONF.port_end:
            self.port = CONF.port_begin
        self.port += 3
        return self.port

    async def list_catridges( self, request ):
        ''' return dummy list of available catridges. Request has to include player_id '''
        try:
            player_id = request.query[ 'player_id' ]
        except:
            return { 'error':'Invalid query string!' }

        games = [ ( img.split( '/' )[ 1 ], img ) for img in glob.iglob( 'catridges/*/thumbnail.png' ) ]
        print( games )

        return { 'games':games }
        
        
        
    async def start_catridge( self, request ):
        ''' request has to include game_id and player_id '''
        try:
            game_id = request.query[ 'game_id' ]
            player_id = request.query[ 'player_id' ]
        except:
            return { 'error':'Invalid query string!' }


        PORT = self.rotate_port()
        HOST = CONF.main_host

        session_id = "%s_%s_%d" % ( game_id, player_id, PORT )
        
        callback = self.VideoStreamCallback() #  game_id, HOST, PORT 
        metadata = {
            "performative": "accept-proposal",
            "in-reply-to":session_id
        }
        templateVideoStreamCallback = Template( metadata=metadata )
        self.add_behaviour( callback, templateVideoStreamCallback )

        
        initialize = self.PrepareGamingRoom( session_id )
        self.add_behaviour( initialize )
        initialize.start()
        await initialize.join()
        self.remove_behaviour( initialize )
        await callback.join()
        self.remove_behaviour( callback )
        
        _thread.start_new_thread( run_game, ( game_id, PORT+1 ) )
        _thread.start_new_thread( run_vnc, ( PORT+1, PORT+2 ) )
        
        
        def run_flask():
            app.run( port=PORT, host=HOST, debug=False, ssl_context=( CONF.cert, CONF.key ) )

        _thread.start_new_thread( run_flask, () )

        # TODO: encode URL (decode later in arcade/app/webutil.js)
        gurl = "host=baltazar&port=%d&resize=scale&autoconnect=true&shared=true&janus_host=%s&janus_port=%d&user=%s&video_room=%s" % ( PORT+2, CONF.janus_host, CONF.janus_port, player_id, self.videorooms[ session_id ] )
        vurl = gurl + "&view_only=true"

        gurl = b64encode( gurl.encode() ).decode( 'ascii' )
        vurl = b64encode( vurl.encode() ).decode( 'ascii' )

        url = "https://%s:%d/arcade/vnc.html?token="  % ( CONF.domain_name, PORT )
        
        result = { "gamer_url":url+gurl,
                   "view_url":url+vurl,
                   "session_id":session_id }

        
        return result

    class PrepareGamingRoom( OneShotBehaviour ):
        def __init__( self, session_id, *args, **kwargs ):
            super().__init__( *args, **kwargs )
            self.session_id = session_id
            
        async def run( self ):
            msg = Message()
            msg.to = "%s@%s" % ( CONF.video_streaming_agent, CONF.xmpp_server )
            self.agent.say( msg.to )

            msg.metadata = {
                "performative":"request",
                "content":"create-room",
                "reply-with":self.session_id
            }

            msg.body = self.session_id
        
            await self.send( msg )

        

    class VideoStreamCallback( OneShotBehaviour ):
        async def run( self ):
            msg = Message()
            msg = await self.receive( timeout=30 ) 
            if msg:
                self.agent.say( f"VideoStreamCallback: I received a message: {msg.body}" )
                session_id = msg.metadata[ 'in-reply-to' ]
                room_no = msg.metadata[ 'room-no' ]
                self.agent.videorooms[ session_id ] = room_no
                
    
    async def setup( self ):
        self.videorooms = {}
        
CONF = configuration()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument( "--node", const=True, nargs='?', type=bool, help="Specify if the agent shoud be started as node. If blank it will start as a master server." )
    args = parser.parse_args()
    
    NODE = bool( args.node )

    name = "%s@%s" % ( CONF.game_streaming_agent, CONF.xmpp_server )
    if not NODE:
        try:
            register_system()
        except XMPPRegisterException:
            pass
    else:
        try:
            register( CONF.game_streaming_agent, CONF.password )
        except XMPPRegisterException:
            pass
    a = GameStreamingAgent( name, CONF.password )
    a.start()
    a.web.start( CONF.main_host, port=CONF.game_streaming_agent_port )

    
            
