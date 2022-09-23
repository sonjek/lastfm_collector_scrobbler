#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from datetime import datetime, timedelta
import time
from os import path
import random
import click


old_datetime = datetime.now()
updated = False


def prepate_old_date(duration=None, date_time=None):
    """
    Allow fast scrobble by reduced duration of track
    """
    reduced_duration = int(duration * 0.6)
    new_duration = reduced_duration + random.randint(4, 10) if reduced_duration > 90 else duration

    """ Normal scrobble"""
    if not date_time:
        return datetime.now(), new_duration, new_duration

    """ Fast scrobble (for past time)"""
    global old_datetime
    global updated
    if not updated:
        old_datetime = date_time
        updated = True

    old_datetime = old_datetime + timedelta(seconds=new_duration)

    return old_datetime, new_duration, 15


def prepare_duration(duration=124000):
    if duration < 0 or not duration:
        duration = 124000
    return int(duration / 1000) if duration > 1000 else duration


def check_date_from_future(date_time):
    if date_time > datetime.now():
        return True
    else:
        return False


def timestamp(date=datetime.now()):
    return int(time.mktime(date.timetuple()))


def sec_to_hms(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    if seconds >= 3600:
        return f"{h:d}:{m:02d}:{s:02d}"
    else:
        return f"{m:d}:{s:02d}"


def datetime_to_str(dttime):
    return dttime.strftime("%Y-%m-%d %H:%M:%S")


def split_artist_track(artist_track_info):
    if not len(artist_track_info):
        return None, None, None, None

    artist_track_info = artist_track_info.replace(" – ", " - ")
    artist_track_info = artist_track_info.replace("“", '"')
    artist_track_info = artist_track_info.replace("”", '"')

    try:
        (artist, title, album, duration) = artist_track_info.split(" -- ", 4)
    except ValueError:
        click.echo(click.style("Wrong line: ", fg="green") + click.style(artist_track_info, fg="red"))
        return None, None, None, None

    artist = artist.strip()
    title = title.strip()
    album = album.strip()
    if len(duration.strip()) > 0:
        duration = int(duration.strip())

    if len(artist) == 0 and len(title) == 0:
        click.secho("Error: Artist and track are blank", fg='red')
    if len(artist) == 0:
        click.secho("Error: Artist is blank", fg='red')
    if len(title) == 0:
        click.secho("Error: Track is blank", fg='red')
    if len(artist) == 0 or len(title) == 0:
        return None, None, None, None

    return artist, title, album, duration


def write_to_file(file, value: str):
    with open(file.replace(' ', '_'), "a+") as f:
        f.write(f'{value}\n')


def get_playlist_folder():
    return './data/playlist/'


def get_playlist_file(filename):
    return f'{get_playlist_folder()}{filename}.txt'


def write_to_artist_file(filename, value: str):
    write_to_file(get_playlist_file(filename), value)


def check_in_artist_file(filename, value: str):
    file_path = get_playlist_file(filename)
    if not path.exists(file_path):
        return False

    with open(file_path) as f:
        if value in f.read():
            return True
        else:
            return False
