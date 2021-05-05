# Magtag Radio

This app turns a [Magtag](https://www.adafruit.com/product/4800) into a remote control for the [Owntone Media Server](https://github.com/owntone/owntone-server). It was designed to quickly start a playlist of streaming radio stations, display the currently playing station and song, and allow cycling through stations.

## Controls

Button 1: Erase the current queue and begin playing a user configured playlist. Or if already playing, pause the media server and put Magtag into deep sleep.

Button 2: Advance to next radio staion (or song) in playlist.

Button 3: Volume down.

Button 4: Volume up.

## TODO

1. Fix bug where Magtag sometimes crashes with too frequent screen refresh error.
2. Make artist/album/song display smarter. Radio stations use these attributes inconsistently and some basic string checking will go a long way towards making the display more useful.


