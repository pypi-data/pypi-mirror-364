import unittest
from json import JSONDecodeError

from tests import *
from umu_commander import db


class DB(unittest.TestCase):
    def setUp(self):
        db.DB_DIR = TESTING_DIR
        setup()

    def tearDown(self):
        teardown()

    def test_missing_db(self):
        db.load()
        self.assertEqual(db.copy(), {})

    def test_malformed_db(self):
        with open(os.path.join(db.DB_DIR, db.DB_NAME), "tw") as db_file:
            db_file.write("{")

        with self.assertRaises(JSONDecodeError):
            db.load()

    def test_addition_removal(self):
        db.load()
        db.add_to(PROTON_DIR_1, PROTON_BIG, USER_DIR)

        self.assertIn(PROTON_BIG, db.get(PROTON_DIR_1))
        self.assertIn(USER_DIR, db.get(PROTON_DIR_1, PROTON_BIG))

        db.remove_from(PROTON_DIR_1, PROTON_BIG, USER_DIR)

        self.assertIn(PROTON_BIG, db.get(PROTON_DIR_1))
        self.assertNotIn(USER_DIR, db.get(PROTON_DIR_1, PROTON_BIG))

        db.delete(PROTON_DIR_1, PROTON_BIG)
        self.assertNotIn(PROTON_BIG, db.get(PROTON_DIR_1))
