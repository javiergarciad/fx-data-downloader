# python imports
import csv
import datetime
import gzip
import logging
import random
from io import BytesIO
from multiprocessing import Pool
from time import sleep

# third party imports
import requests

# local imports
from src.common import logging_setup
from src.database import DB, database_init
from src.models import FxTick, Instrument

# logging setup
logger = logging.getLogger(__name__)


def weeks_between_dates(d0: datetime.date, d1: datetime.date) -> int:
    """
    Compute the number of weeks between two dates.

    :param d0: The first date.
    :param d1: The second date.
    :return: The number of weeks between the two dates.
    """
    delta = (d1 - d0).days
    weeks = delta // 7
    if delta % 7 != 0:
        weeks += 1
    return weeks


def download_and_process_gz(url_data: str, batch_size=10000) -> bool:
    """
    Downloads and processes the data from a gzipped file for a given instrument.

    :param ticket: The instrument ticker.
    :param url_data: The URL of the gzipped data file.
    :param batch_size: The number of rows to add to the database in each batch.
    :return: True if the download and processing were successful, False otherwise.
    """
    start_time = datetime.datetime.now()

    try:
        # get some info from the url
        url_parts = url_data.split("/")
        ticket, yr, wk = url_parts[-3], url_parts[-2], url_parts[-1].split(".")[0]
        this = f"{ticket}-{yr}-{wk}"
        logger.info(f"Downloading tick data for: '{this}'")

        # set the database
        db = DB()
        # get the data from url
        response = requests.get(url_data, stream=True)
        response.raise_for_status()  # Raise exception for non-2xx status codes

        # process downlaoded data
        with gzip.open(BytesIO(response.content), "rt") as file:
            logger.info(f"Processing tick data for: '{this}'")
            # read and remove \Null characters
            reader = csv.reader(x.replace("\0", "") for x in file)

            next(reader)

            rows = []
            count = 0
            # datetimes com in different flavours, try to parse them
            datetime_fmts = ["%m/%d/%Y %H:%M:%S.%f", "%m-%d-%Y %H:%M:%S.%f"]

            with db.session() as session:
                for row in reader:
                    if row:
                        try:
                            # datetime parser
                            for fmt in datetime_fmts:
                                try:
                                    dt = datetime.datetime.strptime(row[0], fmt)
                                except ValueError:
                                    pass

                            # create tick obj
                            rows.append(
                                FxTick(
                                    dt=dt,
                                    bid=row[1],
                                    ask=row[2],
                                    ticket=ticket,
                                )
                            )
                            count += 1
                        except (ValueError, IndexError) as e:
                            logger.warning(
                                f"Error parsing row: {row} for '{this}'. {str(e)}"
                            )

                    # add to dtabase in batches
                    if count % batch_size == 0:
                        session.add_all(rows)
                        session.commit()
                        rows = []

                if rows:
                    session.add_all(rows)
                    session.commit()

        processing_time = round((datetime.datetime.now() - start_time).total_seconds(),1)
        logger.info(
            f"Finished processing tick data for '{this}' in {processing_time}s"
        )
        return True, this

    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading: '{this}'. {str(e)}")
        return False, this

    except (gzip.BadGzipFile, csv.Error) as e:
        logger.error(f"Error processing gzipped for: '{this}'. {str(e)}")
        return False, this


def download_tick_data(
    ticket: str,
    d0: datetime.date,
    d1: datetime.date,
    multiprocess=False,
    num_processes: int = 4,
) -> bool:
    """
    Downloads tick data for a given instrument from FXCM using multiprocessing.

    :param ticket: The instrument ticker.
    :param d0: The start date.
    :param d1: The end date.
    :param num_processes: The number of processes to use for parallel downloading.
    :return: True if the download was successful, False otherwise.
    """
    base_url = "https://tickdata.fxcorporate.com"
    url_suffix = ".csv.gz"

    try:
        # find how many weeks between the two dates
        weeks = weeks_between_dates(d0, d1)

        if multiprocess:
            # create a pool of processes
            pool = Pool(num_processes)
            results = []
        for i in range(weeks):
            # construct the url for the week for this symbol
            new_date = d0 + datetime.timedelta(weeks=i)
            yr, wk, _ = new_date.isocalendar()
            url_data = f"{base_url}/{ticket}/{yr}/{wk}{url_suffix}"

            # process the download
            if multiprocess:
                # download and process in parallel
                result = pool.apply_async(download_and_process_gz, args=(url_data,))
                results.append(result)
            else:
                # download and process in sequence
                result = download_and_process_gz(url_data)
                if not result[0]:
                    logger.warning(f"Failed to download: '{result[1]}'")
                    return False, result[1]

            sleep(random.randint(1, 3))

        if multiprocess:
            # close the pool and wait for the processes to finish
            pool.close()
            pool.join()

        logger.info(f"Finished process for '{ticket}, {len(results)} files'")
        return True, ticket

    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading tick data for '{ticket}'. {str(e)}")
        return False, ticket

    except Exception as e:
        logger.exception(
            f"An unexpected error for '{ticket}'. {str(e)}"
        )
        return False, ticket


def downloader(tickets=None, start_date=None, end_date=None, multiprocess=False):
    """
    Main entry point of the program.

    Downloads and processes tick data for multiple instruments
    within the specified date range.

    :param  tickets: a list of strs representing available tickets in the database. None will download all the tickets.

    :param  multiprocess: True if multiprocessing should be used, False otherwise.
    :return: None.

    """
    # arguments validation or defaults
    if start_date is None:
        # FXCM informs that has tick data from 2019 week 1
        # https://github.com/fxcm/MarketData/tree/master/TickData
        start_date = datetime.date(2019, 1, 1)
    else:
        if not isinstance(start_date, datetime.date):
            raise TypeError("start_date must be a datetime.date object")

    if end_date is None:
        # Also they say the data is update monthly so we need to
        # get the last day of the last month as our final date
        today = datetime.date.today()
        date_to = today.replace(day=1) - datetime.timedelta(days=1)
    else:
        if not isinstance(end_date, datetime.date):
            raise TypeError("end_date must be a datetime.date object")

    # getting the instruments we are going to update
    instruments = Instrument().get(tickets)
    for each_instrument in instruments:
        latest_tick = FxTick().get_latest(each_instrument.ticket)
        if isinstance(latest_tick, datetime.datetime):
            date_to = latest_tick.dt.date() + datetime.timedelta(days=1)

        download_tick_data(
            ticket=each_instrument.ticket,
            d0=start_date,
            d1=end_date,
            multiprocess=multiprocess,
        )
