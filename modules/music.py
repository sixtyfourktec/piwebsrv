# Copyright (c) Christian Poetzsch
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Script for providing information about the current playing song in Runeaudio
# or MoodeAudio. This needs to run on the same host where the player software
# is running.
#
# Runeaudio doesn't provide any cover art for web radios. So the script looks
# into the COVER_ROOT directory for an image file matching the radio name. If
# found a local url will returned to the client.
#
# For MoodeAudio you need to turn on the file info so that it writes out the
# current song information.

import bottle
import json
import os
import platform
import time
import urllib

# static configuration

REDIS_SERVER='localhost'
REDIS_PORT=6379

COVER_ROOT='covers'

# module class definition

class music:
    def init(self, path, ip, port):
        print('init music module')
        self.path, self.ip, self.port = path, ip, port
        if platform.node() == 'runeaudio':
            self.current = self.runeaudio_current
            if not self.connect_rune():
                return False
        elif platform.node() == 'moode':
            self.current = self.moode_current
        else:
            print('unknown platform')
            return False
        return True

    def connect_rune(self):
        try:
            import redis
            for i in range (1,3):
                try:
                    self.redisclient = redis.Redis(REDIS_SERVER, REDIS_PORT)
                    print('connected to redis service at {}:{}'.format(REDIS_SERVER, REDIS_PORT))
                    break;
                except Exception as e:
#                    print(e)
                    time.sleep(1)
            else:
                print("unable to connect to redis service on startup")
                return False
        except ImportError:
            print("redis module not installed")
            return False
        return True

    def runeaudio_current(self):
        d = {}
        r_status = json.loads(self.redisclient.get('act_player_info'))
        if r_status['radioname'] != None:
            d['artist'] = 'Radio'
            d['title'] = r_status['radioname']
            d['album'] = ''
        else:
            d['artist'] = r_status.get('currentartist')
            d['title'] = r_status.get('currentsong')
            d['album'] = r_status.get('currentalbum')
        d['volume'] = int(r_status.get('volume'))
        d['mute'] = True if d['volume'] == 0 else False
        d['state'] = r_status.get('state')
        coverfile = []
        if d['artist'] != '': coverfile.append(d['artist'])
        if d['album'] != '': coverfile.append(d['album'])
        if d['title'] != '': coverfile.append(d['title'])
        coverfile = '-'.join(coverfile) + '.jpg'
#        print coverfile
        # if there is a local cover file use that instead
        if os.path.isfile(os.path.join(COVER_ROOT, coverfile)):
            d['coverurl'] = 'http://{}:{}/v1/music/covers/{}'.format(self.ip, str(self.port), urllib.quote(coverfile))
        else:
            d['coverurl'] = 'http://{}/coverart/?v=1'.format(self.ip)
        return d

    def moode_current(self):
        d = {}
        with open("/var/www/currentsong.txt") as f:
            for line in f:
                key = line[0:line.find('=')].strip()
                val = line[line.find('=') + 1:].strip()
                if key == 'coverurl':
                    val = 'http://' + self.ip + ('' if val.startswith('/') else '/')  + urllib.quote(urllib.unquote(val))
                if key == 'mute':
                    val = True if val == '1' else False
                if key == 'volume':
                    val = int(val)
                d[key] = val
        return d

    def covers(self, name):
        return bottle.static_file(urllib.unquote(name), root=os.path.join(self.path, COVER_ROOT))

# global functions

instance = None

def create():
    global instance
    instance = music()
    return instance

@bottle.get('/v1/music/covers/<name>')
def route_covers(name):
    return instance.covers(name)

@bottle.get('/v1/music/current')
def route_current():
    return instance.current()

# vim: tabstop=4:softtabstop=0:expandtab:shiftwidth=4:smarttab
