# Copyright (c) 2016 Christian Poetzsch
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

# Really simple module for testing internet connectivity as well as for the
# existence of specific devices in the local lan. The configuration file has
# the form of:
# name=ip

import bottle
import subprocess
import threading
import os

# static configuration

CFG_FILE='people.cfg'
WORLD_HOST='google.co.uk'

# module class definition

class network:
    def init(self, path, ip, port):
        print('init network module')
        self.path, self.ip, self.port = path, ip, port
        self.plist = {}
        self.presult = {}
        self.wresult = {}

        with open(os.path.join(self.path, CFG_FILE)) as f:
            for line in f:
                name, ip  = line.split('=')
                self.plist[name] = ip

        self.scan()

        return True

    def ping(self, host):
        return subprocess.call(['/usr/bin/ping', '-c', '1', '-w', '1', host], stdout=subprocess.PIPE)

    def scan(self):
        for p in self.plist:
            self.presult[p] = True if self.ping(self.plist[p]) == 0 else False
        self.wresult['World'] = True if self.ping(WORLD_HOST) == 0 else False
        timer = threading.Timer(10.0, self.scan)
        timer.setDaemon(True)
        timer.start()

    def people(self):
        return self.presult

    def world(self):
        return self.wresult

# global functions

instance = None

def create():
    global instance
    instance = network()
    return instance

@bottle.get('/v1/network/people')
def route_people():
    return instance.people()

@bottle.get('/v1/network/world')
def route_world():
    return instance.world()

# vim: tabstop=4:softtabstop=0:expandtab:shiftwidth=4:smarttab
