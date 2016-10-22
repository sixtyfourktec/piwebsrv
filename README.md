# piwebsrv
Copyright (C) 2016 Christian Pötzsch

## Content

piwebsrv is a simple web service providing a RESTful API to certain aspects of a home network. It is intended to run on a Raspberry Pi with the http://www.runeaudio.com/ or http://moodeaudio.org/ music player software.

Right now there are 2 modules available:

 1. music:
    Provides information about the current playing song in the player software. This module has two entry points:  
    `v1/music/current` - returns the current song information  
    `v1/music/covers/name` - returns a cover image with the name 'name' when available  
 2. network:
    Provides basic information about the network state. This module has two entry points:  
    `v1/network/world` - returns the state of the public internet connection  
    `v1/network/people` - returns the visibility state of certain devices in the network  

## Requirements

 * bootle
 * python2-redis when used with RuneAudio

## Install

Get the code:

```
$ git clone https://github.com/sixtyfourktec/piwebsrv.git
```

Create a people.cfg file for the network configuration and also put some web radio covers into the covers directory if desired.

Change piwebsrv.service and point to the correct piwebsrv.py location. Install the systemd service file and start it:

```
$ sudo systemctl enable $PWD/piwebsrv.service
$ sudo systemctl start piwebsrv
```

## Usage

Point your browser to http://raspberry-pi-ip:8080/v1/network/world. This should return the current connection status to the public internet.

Enjoy

## Notes on security

There is no security build-in whatsoever. Only use this in a trusted environment!

## License
The MIT License (MIT)
