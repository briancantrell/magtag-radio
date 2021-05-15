from adafruit_display_text import label, wrap_text_to_lines
import json

def parse_metadata(metadata):
    # print(metadata)
    line1_max_width = 35
    line1 = metadata['title']
    line1_formatted = "\n".join(wrap_text_to_lines(line1, line1_max_width))

    line2_max_width = 30
    line2 = metadata['album']
    line2_formatted = "\n".join(wrap_text_to_lines(line2, line2_max_width))
    line1_line_count = line1_formatted.count("\n")+1
    if line1_line_count > 1:
        line2_formatted = "\n" + line2_formatted

    line3_max_width = 25
    line3 = metadata['artist']
    line3_formatted = "\n".join(wrap_text_to_lines(line3, line3_max_width))

    if line3 == line1 or line3 == line2:
        line3_formatted = ""

    display_data = {
            'line1': line1_formatted,
            'line2': line2_formatted,
            'line3': line3_formatted
            }

    return display_data

def load_example_metadata():
    with open('example-metadata.json') as f:
          data = json.load(f)
          for track in data['songs']:
              parsed_track = parse_metadata(track)
              debug_track(parsed_track)

def debug_track(track):
    print("---------------------------------")
    print(track['line1'])
    print(track['line2'])
    print(track['line3'])

