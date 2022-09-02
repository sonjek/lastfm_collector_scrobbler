#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# https://pypi.org/project/pylast/
# https://github.com/pylast/pylast
#
# https://click.palletsprojects.com/en/7.x/options/
#
#
# https://www.last.fm/ru/api/authentication
# https://www.last.fm/api/webauth
# https://www.last.fm/api/show/auth.getToken
#

import sys
from os import path
from dateutil import parser
from configparser import ConfigParser
from console_progressbar import ProgressBar
from random import shuffle
import random
from pathlib import Path
import glob
import os
import time
import logging
import itertools
import click
import pylast
import utils


def parce_config():
    file_path = "data/config.ini"
    if not path.exists(file_path):
        click.echo(click.style(f"No config file: ", fg="red") + click.style(file_path, fg="cyan"))
        sys.exit()

    configuration = ConfigParser()
    configuration.read(file_path)
    return configuration


def auth():
    config = parce_config()
    try:
        return pylast.LastFMNetwork(
            api_key=config["API"]["api_key"],
            api_secret=config["API"]["api_secret"],
            username=config["LOGIN"]["username"],
            password_hash=config["LOGIN"]["password_hash"]
        )
    except KeyError:
        click.secho(Path.cwd(), fg='red')
        raise


def set_now_playing(last_fm, artist, track, album=None):
    try:
        last_fm.update_now_playing(artist=artist, title=track, album=album)
    except (pylast.WSError, pylast.MalformedResponseError, pylast.NetworkError):
        return


def scrobble_track(last_fm, artist, track, album, time_stamp=utils.timestamp()):
    try:
        last_fm.scrobble(artist=artist, title=track, album=album, timestamp=time_stamp)
    except (pylast.WSError, pylast.MalformedResponseError, pylast.NetworkError):
        return


def progressbar(prefix: str, m_track: str, wait: int):
    pb = ProgressBar(total=100,
                     prefix=prefix,
                     suffix=m_track,
                     decimals=0,
                     length=10,
                     fill='|',
                     zfill=' '
                     )
    for i in range(1, wait + 1):
        time.sleep(1)
        pb.print_progress_bar(int(100 * i // wait))


def start_scrobble_track(last_fm, artist, title, album=None, duration=None, idx=None, date_time=None, silent=False):
    if not artist:
        return

    if not silent:
        set_now_playing(last_fm, artist, title, album)

    run_date, duration, wait = utils.prepate_old_date(duration, date_time)
    if utils.check_date_from_future(run_date):
        click.secho("Scrobble to future is not allowed. Use current date and time.", fg="red")
        run_date, duration, wait = utils.prepate_old_date(duration, None)

    m_date = click.style(f'[{utils.datetime_to_str(run_date)}]', fg="green")
    m_progress = click.style(f'({idx})', fg="yellow", bold=True)
    m_track = click.style(f'  {artist} - {title}', fg="cyan") + ' (' + click.style(album, fg="green") + ')'
    m_time = utils.sec_to_hms(duration) if not date_time else f'{utils.sec_to_hms(wait)}({utils.sec_to_hms(duration)})'
    prefix = f'{m_progress}\t{m_date}\t{m_time}'
    progressbar(prefix, m_track, wait)

    if not silent:
        scrobble_track(last_fm, artist, title, album, utils.timestamp(run_date))


def get_artist_albums(artist_title, limit, last_fm):
    try:
        return pylast.Artist(artist_title, last_fm).get_top_albums(limit=limit)
    except Exception as e:
        click.secho(f"get_artist_albums: {artist_title}\nError: {e}", fg='red')
        time.sleep(20)
        return get_artist_albums(artist_title, limit, last_fm)


def get_album_tracks(artist_title, album_title, last_fm):
    try:
        return pylast.Album(artist_title, album_title, last_fm).get_tracks()
    except pylast.WSError as e:
        if "Album not found" in e.details:
            return None
    except pylast.MalformedResponseError as e:
        click.secho(f"get_album_tracks: {artist_title} - {album_title}\nError: {e}", fg='red')
        return None
    except Exception as e:
        click.secho(f"get_album_tracks: {artist_title} - {album_title}\nError: {e}", fg='red')
        time.sleep(20)
        return get_album_tracks(artist_title, album_title, last_fm)


def get_track_album(artist_title, track_title, last_fm):
    try:
        return pylast.Track(artist_title, track_title, last_fm).get_album()
    except pylast.WSError as e:
        if "Track not found" in e.details:
            return None
    except Exception as e:
        click.secho(f"get_track_album: {artist_title} - {track_title}\nError: {e}", fg='red')
        time.sleep(20)
        return get_track_album(artist_title, track_title, last_fm)


def get_track_duration(artist_title, track_title, last_fm):
    try:
        return pylast.Track(artist_title, track_title, last_fm).get_duration()
    except pylast.WSError as e:
        if "Track not found" in e.details:
            return None
    except Exception as e:
        click.secho(f"get_track_duration: {artist_title} - {track_title}\nError: {e}", fg='red')
        time.sleep(20)
        return get_track_duration(artist_title, track_title, last_fm)


@click.group(context_settings=dict(help_option_names=["-h", "-help", "--help"]))
@click.version_option("1.0", prog_name="lastfm_collector_scrobbler")
@click.option("verbose", "--verbose/--no-verbose", default=False)
def cli(verbose: bool):
    if verbose:
        logging.basicConfig(stream=sys.stdout,
                            level=logging.DEBUG,
                            format="%(asctime)s %(levelname)s - %(name)s - %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S %p"
                            )
        click.echo(click.style("Debug mode is: ", fg="green") + 'ON')


@cli.command(short_help="Scrobble tracks from file.", help="Scrobble tracks from file.")
@click.argument("filename", required=True, type=click.Path(exists=True))
@click.option("runs", "--runs", type=click.INT, default=1, help="Scrobble from file N times.")
@click.option("infinite", "--infinite/--no-infinite", default=False, help="Infinite scrobble from file.")
@click.option("shuffle_rows", "--shuffle/--no-shuffle", default=True,
              help="Shuffle trucks from file. Disabled in infinite mode")
@click.option("silent", "--silent/--no-silent", default=False, help="Disable scrobbling.")
@click.option("date", "--date", type=click.STRING,
              help="Allow scrobbling past 13 days. Example: '2018-12-31 24:59:59'")
def scrobble(filename: str, runs: int, infinite: bool, shuffle_rows: bool, silent: bool, date: str):
    last_fm = auth() if not silent else None

    with open(Path(filename)) as file:
        lines = file.read().rstrip().splitlines()

        for run in range(1, runs + 1):
            if shuffle_rows:
                shuffle(lines)

            if not infinite:
                iterate = enumerate(lines)
                for idx, line in iterate:
                    start_scrobble_track(
                        last_fm,
                        *utils.split_artist_track(line.strip()),
                        f"{idx + 1}/{len(lines)}" if runs < 2 else f"{idx + 1}/{len(lines)}({run}/{runs})",
                        None if not date else parser.parse(date),
                        silent
                    )
            else:
                idx = 0
                while True:
                    line = random.choice(lines)
                    idx += 1
                    start_scrobble_track(
                        last_fm,
                        *utils.split_artist_track(line.strip()),
                        f"{idx}/{len(lines)}" if runs < 2 else f"{idx}/{len(lines)}({run}/{runs})",
                        None if not date else parser.parse(date),
                        silent
                    )


@cli.command(short_help="Artist name")
@click.argument("artist")
@click.option("limit", "--limit", type=click.INT, default=50, help="Albums limit for collect tracks.")
def create_artist_file(artist: str, limit: int):
    click.echo(click.style(f"Collecting {limit} first album tracks for: ", fg="green") + click.style(artist, fg="cyan"))
    last_fm = auth()
    trucks = 0

    album_excludes = parce_config()["SYSTEM"]["album_excludes"]
    list_album_excludes = [s.replace("'", "") for s in album_excludes.split(',')]

    albums = get_artist_albums(artist, limit, last_fm)
    for idx, album in enumerate(albums):
        album_title = album.item.title.replace("'", "").replace("(null)", "")
        if not album_title:
            continue

        if any(ext in album_title for ext in list_album_excludes):
            click.echo(click.style(f"Ignore album: ", fg="green") + click.style(album_title, fg="cyan"))
            continue

        click.echo(click.style(f"\n{idx+1} Album: ", fg="green") + click.style(album_title, fg="cyan"))
        tracks = get_album_tracks(artist, album_title, last_fm)
        if not tracks:
            click.echo(click.style(f"Empty album: ", fg="green") + click.style(album_title, fg="cyan"))
            continue

        utils.write_to_artist_file(artist, '')
        for tr in tracks:
            trucks += 1
            artist_track = f'{tr.artist} -- {tr.title}'
            artist_track_album = f'{artist_track} -- {album_title}'
            if utils.check_in_artist_file(artist, artist_track_album):
                click.secho(
                    click.style(f"{trucks}\tSkip already exist: ", fg="green")
                    + click.style(artist_track_album, fg="cyan")
                )
                continue

            track_duration = get_track_duration(tr.artist, tr.title, last_fm)
            if None is track_duration:
                click.secho(click.style(f'Track not found\t', fg="red") + click.style(artist_track, fg="cyan"))
                continue

            track_duration = utils.prepare_duration(track_duration)
            row = f"{artist_track_album} -- {track_duration}"
            utils.write_to_artist_file(artist, row)
            click.echo(click.style(f'{trucks}\t', fg="green") + click.style(row, fg="cyan"))
            time.sleep(2)


@cli.command(short_help='Show *.txt files in data folder.')
def ls():
    os.chdir(utils.get_playlist_folder())
    msg = click.style('Data folder files:', fg="green")
    click.echo("{}\n{}".format(msg, f'\n'.join(glob.glob('*.txt'))))


@cli.command(short_help='Save loved tracks to loved.txt file.')
@click.option("limit", "--limit", type=click.INT, default=100, help="Track limit for collect tracks.")
def save_loved(limit: int):
    click.secho(f"Collecting first {limit} loved trucks.", fg="cyan")
    last_fm = auth()
    trucks = 0
    username = parce_config()["LOGIN"]["username"]
    user = last_fm.get_user(username)
    loved = user.get_loved_tracks(limit=limit)
    for track in loved:
        artist = track.track.artist
        title = track.track.title
        album = get_track_album(artist, title, last_fm)

        track_duration = get_track_duration(artist, title, last_fm)
        if None is track_duration:
            click.echo(click.style(f'Track not found:\t', fg="red") + click.style(artist, fg="cyan"))
            continue
        track_duration = utils.prepare_duration(track_duration)

        row = f"{artist} -- {title} -- {album} -- {track_duration}"
        utils.write_to_artist_file('loved', row)
        trucks += 1
        click.echo(click.style(f'{trucks}\t', fg="green") + click.style(row, fg="cyan"))


if __name__ == '__main__':
    cli()
