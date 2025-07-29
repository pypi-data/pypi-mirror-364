#! /usr/bin/python3
import sys
from cProfile import Profile
from importlib.metadata import version
from pstats import SortKey, Stats
from time import perf_counter

from appdirs import user_data_dir
from requests.exceptions import ConnectionError, ReadTimeout
from spotipy.oauth2 import SpotifyOauthError

from monthify import ERROR, appauthor, appname, console, logger
from monthify.args import get_args, parse_args
from monthify.auth import Auth
from monthify.config import Config
from monthify.playlist import clear_cache
from monthify.script import Monthify

appdata_location = user_data_dir(appname, appauthor)

config = Config()
config_args = config.get_config()

parser, args = parse_args(get_args(config))

VERSION = args.version

if VERSION:
    console.print(f"v{version('monthify')}")
    sys.exit(0)

MAKE_PUBLIC = args.public
SKIP_PLAYLIST_CREATION = args.skip_playlist_creation
CREATE_PLAYLIST = args.create_playlists
LOGOUT = args.logout
REVERSE = args.reverse
MAX_WORKERS = args.max_workers
GENERATE = args.generate
LIBRARY_PATH = ""
OUTPUT_PATH = ""
RELATIVE = args.relative
SORTING_NUMBERS = args.add_sorting_numbers
PROF = args.profile
USE_METADATA = args.dont_use_metadata
if GENERATE:
    if not args.library_path:
        parser.error("--library_path is required when --generate is specified.")
    if not args.output_path:
        parser.error("--output_path is required when --generate is specified.")
    LIBRARY_PATH = args.library_path
    OUTPUT_PATH = args.output_path

if not config.is_using_config_file():
    CLIENT_ID = args.CLIENT_ID
    CLIENT_SECRET = args.CLIENT_SECRET
else:
    if config is None or len(config_args) == 0:
        console.print("Config file empty")
        sys.exit(1)
    if not config_args["CLIENT_ID"] or not config_args["CLIENT_SECRET"]:
        console.print("Spotify keys not found in config file")
        sys.exit(1)
    CLIENT_ID = config_args["CLIENT_ID"]
    CLIENT_SECRET = config_args["CLIENT_SECRET"]

if not CLIENT_ID or not CLIENT_SECRET:
    console.print("Client id and secret needed to connect to spotify's servers", style=ERROR)
    logger.error("Client id and secret id not provided, exiting...")
    sys.exit(1)


def run():
    try:

        def mainLoop(controller: Monthify) -> None:
            # Clear database cache
            clear_cache()

            # Starting info
            controller.starting()

            # Get user saved tracks
            controller.get_saved_track_info()

            # Generate names of playlists based on month and year saved tracks were added
            controller.get_playlist_names_names()

            # Peform Tasks that can be done asynchronously
            controller.perform_async_tasks()

            # Create playlists based on month and year
            controller.create_monthly_playlists()

            # Retrieve playlist ids of created playlists
            controller.get_monthly_playlist_ids()

            # Add saved tracks to created playlists by month and year
            controller.sort_all_tracks_by_month()

            # Generate local playlists if requested
            controller.fill_and_generate_all_playlists()

            # Update last run time
            controller.update_last_run()

        controller = Monthify(
            Auth(
                CLIENT_ID=CLIENT_ID,
                CLIENT_SECRET=CLIENT_SECRET,
                LOCATION=appdata_location,
                REDIRECT="https://open.spotify.com/",
                SCOPES=(
                    "user-library-read",
                    "playlist-read-private",
                    "playlist-modify-private",
                ),
            ),
            USE_METADATA=USE_METADATA,
            SKIP_PLAYLIST_CREATION=SKIP_PLAYLIST_CREATION,
            LOGOUT=LOGOUT,
            CREATE_PLAYLIST=CREATE_PLAYLIST,
            MAKE_PUBLIC=MAKE_PUBLIC,
            REVERSE=REVERSE,
            MAX_WORKERS=MAX_WORKERS,
            GENERATE=GENERATE,
            LIBRARY_PATH=LIBRARY_PATH,
            OUTPUT_PATH=OUTPUT_PATH,
            RELATIVE=RELATIVE,
            SORTING_NUMBERS=SORTING_NUMBERS,
        )

        if PROF:
            with Profile() as profile:
                t0 = perf_counter()

                mainLoop(controller)

                logger.debug(f"Program completed in {perf_counter() - t0:.2f} s")
            (Stats(profile).strip_dirs().sort_stats(SortKey.CALLS).dump_stats("profile.stats"))
        else:
            mainLoop(controller)

    except KeyboardInterrupt:
        console.print("Exiting...")
    except ValueError as ve:
        console.print(f"An error occurred: {ve}", style=ERROR)
        logger.error(f"An error occurred: {ve}")
    except (ConnectionError, ReadTimeout) as e:
        console.print(
            "Cannot connect to Spotify servers, please check your internet connection and try again",
            style=ERROR,
        )
        logger.error(f"Could not connect to Spotify servers, stacktrace:\n{e.strerror}")
        sys.exit(1)
    except SpotifyOauthError as soe:
        console.print(
            "Spotify authentication error, please check your credentials and try again",
            style=ERROR,
        )
        logger.error(f"Spotify authentication error, stacktrace:\n{soe}")
        sys.exit(1)


if __name__ == "__main__":
    run()
