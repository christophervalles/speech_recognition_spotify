from __future__ import unicode_literals

import speech_recognition as sr
import re
import threading
import spotify
from subprocess import call

play_pattern = re.compile('play (.+) by (.+)', re.IGNORECASE)

session = spotify.Session()

loop = spotify.EventLoop(session)
loop.start()

audio = spotify.PortAudioSink(session)

logged_in = threading.Event()
end_of_track = threading.Event()


def on_connection_state_updated(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()


def on_end_of_track(self):
    end_of_track.set()


session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, on_connection_state_updated)
session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)

session.login('tbhot3ww', 'TBHOTH17021987')

logged_in.wait()

r = sr.Recognizer()
call(['say', 'What do you want to listen to?'])
with sr.Microphone() as source:
    audio = r.listen(source)

print 'Stopped listening'
try:
    txt = r.recognize(audio)
    print 'You said: %s' % txt
    play_info = play_pattern.match(txt)

    if play_info:
        song = play_info.group(1)
        artist = play_info.group(2)

        print 'You requested the song %s by %s' % (song, artist)

        search = session.search('%s %s' % (song, artist))
        search.load()

        for t in search.tracks:
            print "Matching with %s by %s" % (t.name, ", ".join([a.name for a in t.artists]))
            if artist.lower() in ", ".join([a.name for a in t.artists]).lower():
                track_uri = t.link.uri
                call(['say', 'Playing'])
                print 'Playing %s by %s' % (t.name, ", ".join([a.name for a in t.artists]))
                break

        track = session.get_track(track_uri).load()
        session.player.load(track)
        session.player.play()

        try:
            while not end_of_track.wait(0.1):
                pass
        except KeyboardInterrupt:
            pass
    else:
        call(['say', 'No command found'])
except LookupError:
    print("Could not understand audio")