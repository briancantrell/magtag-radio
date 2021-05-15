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

from metadata_formatter import parse_metadata

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
    text_scale=0.5
  )

  magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_color=0x000000,
    text_position=(5, 40),
    text_anchor_point=(0, 0),
  )

  magtag.add_text(
    text_font="/fonts/Arial-12.bdf",
    text_color=0x000000,
    text_position=(5, 70),
    text_anchor_point=(0, 0),
  )

# def initialize_album_label():
#   album_label = label.Label(
#     terminalio.FONT,
#     text="Starting...",
#     color=0x000000,
#     scale=1
#   )
#   album_label.anchor_point = (0, 0)
#   album_label.anchored_position = (0, 10)
#   group = displayio.Group(max_size=3, x=10, y=10)
#   group.append(album_label)
#   magtag.splash.append(group)
#   return album_label

def display_status():
  print("refreshing")

  status_response = owntone_api("get", "/api/player")
  status_json = status_response.json()
  current_playing_item_id = status_json["item_id"]
  # current_state = status_json["state"]
  # current_volume = status_json["volume"]
  item = find_currently_play_item(queue(), current_playing_item_id)
  print(item)
  display_lines = parse_metadata(item)
  print(display_lines)

  magtag.set_text(display_lines['line1'], 0, False)
  magtag.set_text(display_lines['line2'], 1, False)
  magtag.set_text(display_lines['line3'], 2, False)

  magtag.display.refresh()

def start_deep_sleep():
  magtag.set_text("Sleeping...zzz zzz zzz", 0, False)
  magtag.set_text("", 1, False)
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
    if i % 300 == 0:
      # 30 seconds
      i=0
      display_status()
