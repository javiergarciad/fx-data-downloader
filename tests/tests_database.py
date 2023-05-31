from pathlib import Path
import unittest
from src.common import get_project_root

from src.database import DB
from src.models import Instrument


class DbTestCase(unittest.TestCase):
    def setUp(self):
        # Set up any necessary test fixtures
        test_path = Path(get_project_root(), "data", "test.sqlite")
        self.db = DB(db_filepath=test_path, echo=False)
        self.data = [Instrument(ticket="AAASSS", has_ticks=True, has_candles=True)]

    def tearDown(self):
        # Clean up any resources used by the test
        self.db.delete_database(confirm=True)

    def test_create_database(self):
        # Test creating a new database
        self.assertTrue(self.db.create_database())

    def test_create_database_if_exist(self):
        self.db.create_database(overwrite=True)  # Create the database before testing
        # Test creating a new database, when one already exist
        self.assertTrue(self.db.create_database(overwrite=True))

    def test_drop_database(self):
        # Test dropping the database
        self.db.create_database()  # Create the database before dropping
        self.assertTrue(self.db.drop_tables(confirm=True))

    def test_delete_database(self):
        # Test deleting the database file
        self.db.create_database()  # Create the database before deleting
        self.assertTrue(self.db.delete_database(confirm=True))

    def test_populate_database(self):
        self.db.create_database()  # Create the database before populating
        self.assertTrue(self.db.populate_database(self.data))

    def test_get_tables_info(self):
        # Test getting the number of rows in each table
        self.db.create_database()  # Create the database
        self.db.populate_database(self.data)  # Populate the database with test data
        # Get the number of rows in each table
        info = self.db.get_tables_info()
        # Assert specific values based on the expected data in the tables
        self.assertEqual(info['rows']["instruments"], 1)


if __name__ == "__main__":
    unittest.main()
