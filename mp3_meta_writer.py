import os
import sys
import json
import xml.etree.ElementTree as ET
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, COMM, TPE2, TXXX, TRCK, TSO2, USLT, TXXX, TSST
from mutagen.mp3 import MP3

# Always maintain const correctness

def set_mp3_metadata(mp3_path: str, meta: dict, title: str, track_number: int):
    audio = MP3(mp3_path, ID3=ID3)
    try:
        audio.add_tags()
    except Exception:
        pass  # Tags already exist

    audio["TIT2"] = TIT2(encoding=3, text=title)
    audio["TPE1"] = TPE1(encoding=3, text=meta.get("album_artist", ""))  # Contributing artists
    audio["TPE2"] = TPE2(encoding=3, text=meta.get("album_artist", ""))  # Album artist
    audio["TALB"] = TALB(encoding=3, text=meta.get("album", ""))
    audio["TCON"] = TCON(encoding=3, text=meta.get("genre", ""))
    audio["TRCK"] = TRCK(encoding=3, text=str(track_number))
    audio["COMM"] = COMM(encoding=3, lang="eng", desc="", text="")  # Comments
    audio["TSST"] = TSST(encoding=3, text="")  # Subtitle
    audio.save()

def indent_xml(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i

def generate_album_nfo(folder: str, meta: dict, mp3_files: list):
    album = ET.Element('album')
    ET.SubElement(album, 'review')
    ET.SubElement(album, 'outline')
    ET.SubElement(album, 'lockdata').text = 'false'
    ET.SubElement(album, 'dateadded').text = ''
    ET.SubElement(album, 'title').text = meta.get('album', '')
    ET.SubElement(album, 'runtime').text = ''
    ET.SubElement(album, 'genre').text = meta.get('genre', '')
    art = ET.SubElement(album, 'art')
    ET.SubElement(album, 'artist').text = meta.get('album_artist', '')
    ET.SubElement(album, 'albumartist').text = meta.get('album_artist', '')
    for idx, mp3_file in enumerate(mp3_files, 1):
        track = ET.SubElement(album, 'track')
        ET.SubElement(track, 'position').text = str(idx)
        ET.SubElement(track, 'title').text = os.path.splitext(mp3_file)[0]
        ET.SubElement(track, 'duration').text = ''
    indent_xml(album)
    nfo_path = os.path.join(folder, 'album.nfo')
    ET.ElementTree(album).write(nfo_path, encoding='utf-8', xml_declaration=True)
    print(f"Generated: album.nfo")

def main():
    if len(sys.argv) != 2:
        print("Usage: python mp3_meta_writer.py <folder>")
        sys.exit(1)
    folder = sys.argv[1]
    meta_path = os.path.join(folder, "meta.json")
    if not os.path.isfile(meta_path):
        print(f"meta.json not found in {folder}")
        sys.exit(1)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    mp3_files = [f for f in os.listdir(folder) if f.lower().endswith(".mp3")]
    mp3_files.sort()
    for idx, mp3_file in enumerate(mp3_files, 1):
        mp3_path = os.path.join(folder, mp3_file)
        title = os.path.splitext(mp3_file)[0]
        set_mp3_metadata(mp3_path, meta, title, idx)
        print(f"Updated: {mp3_file}")
    generate_album_nfo(folder, meta, mp3_files)

if __name__ == "__main__":
    main() 