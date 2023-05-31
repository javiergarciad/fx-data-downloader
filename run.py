# python imports
import argparse
import datetime
import logging
from pathlib import Path
import sys

# local imports
from src.common import logging_setup
from src.database import database_init
from src.downloader import downloader

# set the project root directory as the working directory
# so this can be called from the terminal
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# logging setup
logging_setup(logging.INFO)
logger = logging.getLogger(__name__)

# arguments
parser = argparse.ArgumentParser(
    description="""
        Script for downloading and processing tick data from FXCM.
        Make use of: https://github.com/fxcm/MarketData/tree/master/TickData.
        """
)

# Add the arguments
parser.add_argument(
    "-d",
    "--newdb",
    action="store_true",
    default=False,
    help="Start a new database",
)
parser.add_argument(
    "-m",
    "--multiprocess",
    action="store_true",
    default=False,
    help="Enable multiprocessing option",
)
parser.add_argument(
    "-t",
    "--tickets",
    nargs="*",
    default=None,
    help="List of tickets, default is all",
)
parser.add_argument(
    "-s",
    "--start-date",
    default=None,
    help="Start date in the format yyyy-mm-dd. Default to 2019-01-01",
)
parser.add_argument(
    "-e",
    "--end-date",
    default=None,
    help="End date in the format yyyy-mm-dd. Default to last day of past month.",
)

args = parser.parse_args()

if args.newdb:
    database_init()

if args.start_date:
    try:
        start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d").date()
    except ValueError:
        logger.critical("Invalid start date format. Please use the format yyyy-mm-dd.")
        raise SystemExit

if args.end_date:
    try:
        start_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d").date()
    except ValueError:
        logger.critical("Invalid end date format. Please use the format yyyy-mm-dd.")
        raise SystemExit


downloader(
    tickets=args.tickets,
    multiprocess=args.multiprocess,
    start_date=args.start_date,
    end_date=args.end_date,
)
