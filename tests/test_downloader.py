import unittest
from datetime import date

from src.downloader import weeks_between_dates


class WeeksBetweenDatesTestCase(unittest.TestCase):
    def test_same_date(self):
        d0 = date(2023, 5, 1)
        d1 = date(2023, 5, 1)
        self.assertEqual(weeks_between_dates(d0, d1), 0)

    def test_consecutive_dates_within_week(self):
        d0 = date(2023, 5, 1)
        d1 = date(2023, 5, 6)
        self.assertEqual(weeks_between_dates(d0, d1), 1)

    def test_consecutive_dates_across_week_boundary(self):
        d0 = date(2023, 5, 1)
        d1 = date(2023, 5, 14)
        self.assertEqual(weeks_between_dates(d0, d1), 2)

    def test_non_consecutive_dates_multiple_weeks(self):
        d0 = date(2023, 5, 1)
        d1 = date(2023, 5, 31)
        self.assertEqual(weeks_between_dates(d0, d1), 5)

    def test_d0_later_than_d1(self):
        d0 = date(2023, 6, 1)
        d1 = date(2023, 5, 1)
        self.assertEqual(weeks_between_dates(d0, d1), -4)

    def test_dates_across_leap_year(self):
        d0 = date(2020, 2, 25)
        d1 = date(2020, 3, 10)
        self.assertEqual(weeks_between_dates(d0, d1), 2)

if __name__ == '__main__':
    unittest.main()


