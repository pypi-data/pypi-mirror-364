import unittest

from tests import *
from umu_commander import db, tracking
from umu_commander.classes import Element


class Tracking(unittest.TestCase):
    def setUp(self):
        db.DB_DIR = TESTING_DIR
        setup()
        db.load()

    def tearDown(self):
        teardown()

    def test_track_untrack(self):
        os.chdir(USER_DIR)

        tracking.track(Element(PROTON_DIR_1, PROTON_BIG), refresh_versions=False)
        self.assertIn(PROTON_BIG, db.get(PROTON_DIR_1))
        self.assertIn(USER_DIR, db.get(PROTON_DIR_1, PROTON_BIG))

        tracking.untrack(quiet=True)
        self.assertIn(PROTON_BIG, db.get(PROTON_DIR_1))
        self.assertNotIn(USER_DIR, db.get(PROTON_DIR_1, PROTON_BIG))

    def test_track_auto_untrack(self):
        os.chdir(USER_DIR)

        tracking.track(Element(PROTON_DIR_1, PROTON_BIG), refresh_versions=False)
        self.assertIn(PROTON_BIG, db.get(PROTON_DIR_1))
        self.assertIn(USER_DIR, db.get(PROTON_DIR_1, PROTON_BIG))

        os.rmdir(USER_DIR)
        tracking.untrack_unlinked()
        self.assertIn(PROTON_BIG, db.get(PROTON_DIR_1))
        self.assertNotIn(
            USER_DIR,
            db.get(PROTON_DIR_1, PROTON_BIG),
            "Auto untrack did not untrack removed directory.",
        )
