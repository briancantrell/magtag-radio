import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests
import terminalio
import displayio
import time
import alarm
import board

from adafruit_magtag.magtag import MagTag
from adafruit_display_text import label, wrap_text_to_lines
from secrets import secrets

magtag = MagTag()

def owntone_server():
    return secrets['owntone_server']

def owntone_radio_playlist_id():
    return secrets['owntone_radio_playlist_id']

def owntone_api(method, path):
  request_types = {
      "get" : requests.get,
      "put" : requests.put,
      "post" : requests.post,
      }
  return request_types[method](owntone_server() + path)

def queue_radio_playlist():
  owntone_api("put", "/api/queue/clear")
  owntone_api(
      "post", 
      "/api/queue/items/add?uris=library:playlist:" + owntone_radio_playlist_id()
      )

def queue():
  queue_response = owntone_api("get", "/api/queue")
  return queue_response.json()

def toggle_playback():
  owntone_api("put", "/api/player/toggle")

def play():
  owntone_api("put", "/api/player/play")

def stop():
  owntone_api("put", "/api/player/stop")

def next_track():
  owntone_api("put", "/api/player/next")

def volume_up():
  owntone_api("put", "/api/player/volume?step=+20")

def volume_down():
  owntone_api("put", "/api/player/volume?step=-20")

def find_currently_play_item(queue, item_id):
  for(index, item) in enumerate(queue["items"]):
    if item["id"] == item_id:
      return item

def initialize_texts():
  magtag.add_text(
    text_font="/fonts/Arial-12.bdf",
    text_color=0x000000,
    text_position=(5, 10),
    text_anchor_point=(0, 0),
  )

  magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_color=0x000000,
    text_position=(5, 60),
    text_anchor_point=(0, 0),
  )

def initialize_album_label():
  album_label = label.Label(
    terminalio.FONT, 
    text="Starting...", 
    color=0x000000,
    scale=1
  )
  album_label.anchor_point = (0, 0)
  album_label.anchored_position = (0, 10)
  group = displayio.Group(max_size=3, x=10, y=10)
  group.append(album_label)
  magtag.splash.append(group)
  return album_label

def display_status():
  status_response = owntone_api("get", "/api/player")
  status_json = status_response.json()
  current_playing_item_id = status_json["item_id"]
  current_state = status_json["state"]
  current_volume = status_json["volume"]
  item = find_currently_play_item(queue(), current_playing_item_id)
  print(item)

  artist = "\n".join(wrap_text_to_lines(item["album_artist"], 35)) 
  magtag.set_text(artist, 0, False)

  album = "\n".join(wrap_text_to_lines(item["album"], 35))
  magtag.set_text(album, 1, False)

  magtag.display.refresh()

def start_deep_sleep():
  album_label.text = "Sleeping...zzz zzz zzz"
  magtag.display.refresh()
  magtag.peripherals.deinit()
  pin_alarm = alarm.pin.PinAlarm(pin=board.BUTTON_A, value=False, pull=True)
  alarm.exit_and_deep_sleep_until_alarms(pin_alarm)

def initialize_network_client():
  wifi.radio.connect(secrets["ssid"], secrets["password"])
  time.sleep(0.5)
  pool = socketpool.SocketPool(wifi.radio)
  return adafruit_requests.Session(pool, ssl.create_default_context())


# album_label = initialize_album_label()
initialize_texts()
magtag.display.refresh()

requests = initialize_network_client()

queue_radio_playlist()
play()
display_status()

i=0
awake = True

while awake:
    time.sleep(0.1)
    i=i+1
    if magtag.peripherals.button_a_pressed == True:
      awake = False
      stop()
      start_deep_sleep()
    if magtag.peripherals.button_b_pressed == True:
      print("next")
      next_track()
      display_status()
    if magtag.peripherals.button_c_pressed == True:
      volume_down()
      display_status()
    if magtag.peripherals.button_d_pressed == True:
      volume_up()
      display_status()
    if i % 2000 == 0:
      i=0
      display_status()
