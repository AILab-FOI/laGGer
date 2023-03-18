#!/usr/bin/env python3.6
import warnings
warnings.filterwarnings("ignore")
from talking_agent import TalkingAgent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template

from config import configuration
# Partially stolen from aiortc janus example (https://github.com/aiortc/aiortc/blob/master/examples/janus/janus.py)
import argparse
import json
import asyncio
import logging
import random
import string
import time

import aiohttp

from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRecorder


pcs = set()


def transaction_id():
    return "".join(random.choice(string.ascii_letters) for x in range(12))


class JanusPlugin:
    def __init__(self, session, url):
        self._queue = asyncio.Queue()
        self._session = session
        self._url = url

    async def send(self, payload):
        message = {"janus": "message", "transaction": transaction_id()}
        message.update(payload)
        async with self._session._http.post(self._url, json=message, ssl=False) as response:
            data = await response.json()
            print( data )
            assert data["janus"] == "ack" or data["janus"] == "success"
            if data["janus"] == "success":
                return response

        response = await self._queue.get()
        assert response["transaction"] == message["transaction"]
        return response


class JanusSession:
    def __init__(self, url):
        self._http = None
        self._poll_task = None
        self._plugins = {}
        self._root_url = url
        self._session_url = None

    async def attach(self, plugin_name: str) -> JanusPlugin:
        message = {
            "janus": "attach",
            "plugin": plugin_name,
            "transaction": transaction_id(),
        }
        async with self._http.post(self._session_url, json=message, ssl=False) as response:
            data = await response.json()
            assert data["janus"] == "success"
            plugin_id = data["data"]["id"]
            plugin = JanusPlugin(self, self._session_url + "/" + str(plugin_id))
            self._plugins[plugin_id] = plugin
            return plugin

    async def create(self):
        self._http = aiohttp.ClientSession()
        message = {"janus": "create", "transaction": transaction_id()}
        async with self._http.post(self._root_url, json=message, ssl=False) as response:
            data = await response.json(content_type=None)
            assert data["janus"] == "success"
            session_id = data["data"]["id"]
            self._session_url = self._root_url + "/" + str(session_id)

        self._poll_task = asyncio.ensure_future(self._poll())

    async def destroy(self):
        if self._poll_task:
            self._poll_task.cancel()
            self._poll_task = None

        if self._session_url:
            message = {"janus": "destroy", "transaction": transaction_id()}
            async with self._http.post(self._session_url, json=message, ssl=False) as response:
                data = await response.json()
                assert data["janus"] == "success"
            self._session_url = None

        if self._http:
            await self._http.close()
            self._http = None

    async def _poll(self):
        while True:
            params = {"maxev": 1, "rid": int(time.time() * 1000)}
            async with self._http.get(self._session_url, params=params, ssl=False) as response:
                data = await response.json()
                if data["janus"] == "event":
                    plugin = self._plugins.get(data["sender"], None)
                    if plugin:
                        await plugin._queue.put(data)
                    else:
                        print(data)


class VideoStreamingAgent( TalkingAgent ):

    class CreateRoom( CyclicBehaviour ):
        async def run( self ):
            msg = Message()
            msg = await self.receive() #  timeout=1 
            if msg:
                self.agent.say( f"I received a message: {msg.body}" )

                in_reply_to = msg.metadata[ "reply-with" ]
                room_name = msg.body

                msg = msg.make_reply()

                self.agent.say( "Creating video room..." )

                await self.agent.session.create()

                plugin = await self.agent.session.attach( "janus.plugin.videoroom" )
    
                response = await plugin.send(
                    {
                        "body": {
                            "request": "create",
                            "is_private": True,
                            "room": self.agent.room
                        }
                    }
                )
                data = await response.json()
                if data[ 'plugindata' ][ 'data' ][ 'videoroom' ] == 'created':
                    self.agent.rooms[ room_name ] = self.agent.room
                    self.agent.room += 1
                    success = "Room created!"
                elif data[ 'plugindata' ][ 'data' ][ 'videoroom' ] == 'event':
                    if 'error' in data[ 'plugindata' ][ 'data' ].keys():
                        success = data[ 'plugindata' ][ 'data' ][ 'error' ]
                    else:
                        success = 'Error creating videoroom!'
                else:
                    success = 'Error creating videoroom - cause unknown!'

                metadata = {
                    "performative":"accept-proposal",
                    "in-reply-to":in_reply_to,
                    "room-no":str( self.agent.room )
                }

                msg.body = str( success )
                msg.metadata = metadata
                self.agent.say( success )
                await self.send( msg )

    async def setup( self ):
        behaviourCreateRoom = self.CreateRoom()
        metadata = {
            "performative":"request",
            "content":"create-room"
        }
        templateCreateRoom = Template( metadata=metadata )
        self.add_behaviour( behaviourCreateRoom, templateCreateRoom )
        self.janus_url = "https://%s:%d/janus" % ( CONF.janus_host, CONF.janus_port )
        self.session = JanusSession( self.janus_url )
        self.rooms = {}
        self.room = 1

CONF = configuration()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument( "--node", const=True, nargs='?', type=bool, help="Specify if the agent shoud be started as node. If blank it will start as a master agent." )
    args = parser.parse_args()
    
    NODE = bool( args.node )

    

    name = "%s@%s" % ( CONF.video_streaming_agent, CONF.xmpp_server )
    a = VideoStreamingAgent( name, CONF.password )
    a.start()
    a.web.start( port=CONF.video_streaming_agent_port )
