from spade.agent import Agent

class TalkingAgent( Agent ):
    def say( self, *msg ):
        print( "%s: %s" % ( self.name, ' '.join( [ str( i ) for i in msg ] ) ) )
