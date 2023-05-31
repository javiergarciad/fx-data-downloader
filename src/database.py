import csv
import logging
import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List

import sqlalchemy
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.common import get_project_root, logging_setup
from src.models import Base, Instrument, Version

# logging setup
logging_setup()
logger = logging.getLogger(__name__)


class DB:
    """
    Manage SQLite Database.
    :param db_filepath: SQLite database file path.
    :param echo: echo SQLAlchemy logging.
    """

    def __init__(self, db_filepath= None, echo=False):
        if db_filepath is None:
            self.db_filepath = Path(get_project_root(), "data", "db.sqlite")
        else:
            self.db_filepath = Path(db_filepath)
        self.echo = echo

    def engine(self):
        """
        Return the database engine.
        :return: SQLAlchemy engine instance.
        """
        try:
            uri = f"sqlite:///{self.db_filepath}"
            return create_engine(uri, echo=self.echo)
        except SQLAlchemyError as e:
            logger.critical(e)
            raise SystemExit

    @contextmanager
    def session(self):
        """
        Context manager for providing a session.
        :return: SQLAlchemy session instance.
        """
        try:
            Session = sessionmaker(bind=self.engine())  # Create a session factory
            session = Session()  # Create a session instance by calling the factory
            yield session
        except SQLAlchemyError as e:
            logger.critical(e)
            session.rollback()
            raise SystemExit
        finally:
            session.close()

    def get_status(self):
        """
        Check database status and schema
        :return:
        """
        # check if the database file exist
        if not Path(self.db_filepath).is_file():
            return {"db": None, "status": None, "version": None}

        # if there is a file check the shema
        try:
            inspector = sqlalchemy.inspect(self.engine())
            # Compare the schema with the expected schema
            expected_tables = set(Base.metadata.tables.keys())
            actual_tables = set(inspector.get_table_names())
            if expected_tables == actual_tables:
                with self.session() as s:
                    version = s.query(Version).first()
                    return version.to_dict()
            else:
                logger.error("schema_mismatch")
                return False
        except SQLAlchemyError() as e:
            logger.critical(e)
            raise SystemExit

    def get_tables_info(self):
        """
        Get the number of rows in each table of the database.
        :return: Dictionary with table names as keys and row counts as values.
        """
        try:
            inspector = sqlalchemy.inspect(self.engine())
            table_row_counts = {}

            # Iterate over each table in the database
            Session = self.session()
            with Session as s:
                for table_name in inspector.get_table_names():
                    stmt = select(func.count()).select_from(text(table_name))
                    row_count = s.execute(stmt).scalar()
                    table_row_counts[table_name] = row_count

            return {"rows": table_row_counts}
        except Exception as e:
            logger.critical(e)
            raise SystemExit

    def create_database(self, overwrite=False):
        """
        Create the database and all the tables.
        :return: True if successful.
        """
        if overwrite == False:
            if Path(self.db_filepath).is_file():
                logger.warning(
                    f"Database already exists at '{self.db_filepath}', overwrite=False"
                )
                logger.warning("Database creation cancelled.")
                return False

        try:
            # delete database if exist
            self.delete_database(confirm=True)
            # create new one
            Base.metadata.create_all(self.engine())
            new_version = Version(
                id=1, created=datetime.utcnow(), updated=datetime.utcnow()
            )
            with self.session() as s:
                s.add(new_version)
            logger.info(f"Database created at {self.db_filepath}")
            return True
        except SQLAlchemyError as e:
            logger.critical(e)
            raise SystemExit

    def drop_tables(self, confirm=False):
        """
        Drop all tables stored in this metadata.
        Conditional by default, will not attempt to drop tables not present in the target database.
        :param confirm: Whether to confirm the table drop.
        :return: True if successful.
        """
        if confirm:
            try:
                Base.metadata.drop_all(self.engine())
                logger.info(f"Database tables dropped from '{self.db_filepath}'")
                return True
            except SQLAlchemyError as e:
                logger.critical(e)
                raise SystemExit
        else:
            logger.warning("Database tables drop cancelled. You must confirm!")
            return False

    def delete_database(self, confirm=False):
        """
        Delete the database file.
        :param confirm: Whether to confirm the database deletion.
        :return: True if successful.
        """
        if confirm:
            if not Path(self.db_filepath).exists():
                return True
            else:
                # delete the file
                try:
                    Path(self.db_filepath).unlink()
                    logger.info(f"Database deleted at '{self.db_filepath}'")
                    return True
                except OSError as e:
                    logger.error(e)
                    raise SystemExit
        else:
            logger.warning(f"Database deletion cancelled. You must confirm!")
            return False

    def populate_database(self, data: List):
        """
        Populate the database with data.
        :param data: List of objects to populate the database.
        :return: True if successful.
        """
        try:
            with self.session() as s:
                s.add_all(data)
                s.commit()
            logger.debug(f"Database populated")
            return True
        except SQLAlchemyError as e:
            logger.error(e)
            raise SystemExit


def get_instruments(csv_file: str) -> List[Instrument]:
    """
    Get the tick instruments from the csv file.
    :param csv_path: path to the csv file.
    :return: a dataframe of tick instruments.
    """

    # Read the CSV file and create Instrument objects
    instruments_data = []
    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            ticket = row[0]
            instrument = Instrument(ticket=ticket, has_ticks=True, has_candles=False)
            instruments_data.append(instrument)

    return instruments_data


def database_init():
    db = DB()
    db.delete_database(confirm=True)
    db.create_database(overwrite=True)
    tick_instruments_csv_file = "./data/tick_instruments.csv"
    instruments = get_instruments(tick_instruments_csv_file)
    db.populate_database(instruments)
    logger.info(db.get_tables_info())
    return True


if __name__ == "__main__":
    """
    Main entry point for database inicialization.
    :return:

    """
