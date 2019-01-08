# lastfm_collector_scrobbler

## Overview

lastfm_collector_scrobbler is a simple LastFM scrobbling utility writen in Python.
It allows collect artist tracks from their albums to txt files and scrobble from these files to LastFM.


Initial setup
------------------
```bash
$ git clone https://github.com/sonjek/lastfm_collector_scrobbler.git
$ cd lastfm_collector_scrobbler
$ cp data/config.ini.default data/config.ini
$ nano data/config.ini
_________________________________________________________________________
[API]
api_key = <Your LastFM API key>
api_secret = <Your LastFM API secret>

[LOGIN]
username = <Your LastFM username>
password_hash = <Your LastFM password_hash>
_________________________________________________________________________
```
More info in https://www.last.fm/ru/api/authentication


Usage
------------------

Built in help:
```bash
$ docker-compose run --name lastfms lastfms -h
Usage: app.py [OPTIONS] COMMAND [ARGS]...

Options:
  --version                 Show the version and exit.
  --verbose / --no-verbose
  -h, -help, --help         Show this message and exit.

Commands:
  create-artist-file  Artist name
  ls                  Show *.txt files in data folder.
  save-loved          Save loved tracks to loved.txt file.
  scrobble            Scrobble tracks from file.
```

Start collecting tracks from 2 first Rob Zombie albums to file:
```bash
$ docker-compose run --rm --name lastfms lastfms create-artist-file 'Rob Zombie' --limit 2
Collecting 50 first albums trucks for: Rob Zombie

1 Album: Hellbilly Deluxe
1	Rob Zombie -- Call of the Zombie -- Hellbilly Deluxe -- 30
2	Rob Zombie -- Superbeast -- Hellbilly Deluxe -- 220
3	Rob Zombie -- Dragula -- Hellbilly Deluxe -- 222
```

Check result:
```bash
$ docker-compose run --rm --name lastfms lastfms ls
Data folder files:
Rob_Zombie.txt
sample.txt
```

Start realtime scrobbling not shuffled tracks from Rob_Zombie.txt file:
```bash
$ docker-compose run --rm --name lastfms lastfms scrobble data/playlist/Rob_Zombie.txt --no-shuffle
(1/598)	[2019-01-08 20:20:20]	1:49 |||||||||||| 100%   Rob Zombie - Spookshow Baby (Hellbilly Deluxe)
(2/598)	[2019-01-08 20:07:53]	0:15 |||||||||||| 100%   Rob Zombie - Call of the Zombie (Hellbilly Deluxe)
(3/598)	[2019-01-08 20:20:20]	1:50 ||||||     | 51%    Rob Zombie - Superbeast (Hellbilly Deluxe)
```

Start scrobbling tracks from Rob_Zombie.txt file for the previous day 2019-01-07 12:00:00:
```bash
$ docker-compose run --rm --name lastfms lastfms scrobble data/playlist/Rob_Zombie.txt  --date '2019-01-07 12:00:00'
(1/598)	[2019-01-07 12:01:40]	0:15(1:40) |||||||||||| 100%   Rob Zombie - Living Dead Girl (Hellbilly Deluxe)
(2/598)	[2019-01-07 12:02:32]	0:15(0:52) |||||||||||| 100%   Rob Zombie - Perversion 99 (Hellbilly Deluxe)
(3/598)	[2019-01-07 12:04:21]	0:15(1:49) |||||||||||| 100%   Rob Zombie - Spookshow Baby (Hellbilly Deluxe)
(4/598)	[2019-01-07 12:04:22]	0:15(1:50) ||||||     | 51%    Rob Zombie - Superbeast (Hellbilly Deluxe)
```

Start demonized Docker container for loop shuddled track list scrobbling from Rob_Zombie.txt file:
```bash
$ docker-compose run -d --restart always --name lastfms lastfms scrobble data/playlist/Rob_Zombie.txt --infinite
lastfms

$ docker logs -f --tail 10 lastfms
(1/598)	[2019-01-07 12:10:28]	1:47 |||||||||||| 100%   Rob Zombie - Dead City Radio - Live (Spookshow International Live)
(2/598)	[2019-01-07 12:12:17]	1:41 |||||||||||| 100%   Rob Zombie - Living Dead Girl (LP version) (Living Dead Girl)
(3/598)	[2019-01-07 12:13:59]	0:20 |||||||||||| 100%   Rob Zombie - Demon Speeding (Album Version) (Past, Present & Future [Explicit])
```

More options:
```bash
$ docker-compose run --rm --name lastfms lastfms scrobble -h
Usage: app.py scrobble [OPTIONS] FILENAME
  Scrobbe tracks from file.

Options:
  --runs INTEGER              Scrobble from file N times.
  --infinite / --no-infinite  Infinite scrobble from file.
  --shuffle / --no-shuffle    Shuffle trucks from file. Disabled in infinite mode
  --silent / --no-silent      Disable scrobbling.
  --date TEXT                 Allow scrobbling past 13 days. Example: '2018-12-31 24:59:59'
  -h, -help, --help           Show this message and exit.
```

Collect first 10 account loved tracks:
```bash
$ docker-compose run --rm --name lastfms lastfms save-loved --limit 10
Collecting first 100 loved trucks.
1	Bring Me the Horizon -- Blasphemy -- Bring Me the Horizon - That's The Spirit -- 275
2	Bring Me the Horizon -- Throne -- Bring Me the Horizon - That's The Spirit -- 191
3	Bring Me the Horizon -- Hospital for Souls -- Bring Me the Horizon - Sempiternal -- 404
```

License
-------

The contents of this repository are licensed under the [The 3-Clause BSD License](https://opensource.org/licenses/BSD-3-Clause)
