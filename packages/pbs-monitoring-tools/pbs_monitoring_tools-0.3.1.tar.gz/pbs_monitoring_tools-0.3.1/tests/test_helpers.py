# helpers.py
# Tests helpers functions

import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
from pbs_monitoring_tools.helpers.helpers import (  # noqa 420
    _backup_errors,
    BackupError,
    check_backups_status,
    check_last_backups_expiration,
)

dataset = [
    [
        "ns1",
        [
            {
                "backup-type": "vm",
                "backup-id": "101",
                "verification": {"state": "failed"},
                "backup-time": datetime.timestamp(datetime.now()),
            },
            {
                "backup-type": "vm",
                "backup-id": "102",
                "backup-time": datetime.timestamp(datetime.now() + timedelta(days=10)),
            },
            {
                "backup-type": "vm",
                "backup-id": "103",
                "verification": {"state": "failed"},
                "backup-time": datetime.timestamp(datetime.now() - timedelta(days=10)),
            },
            {
                "backup-type": "vm",
                "backup-id": "104",
                "verification": {"state": "ok"},
                "backup-time": datetime.timestamp(datetime.now() - timedelta(days=20)),
            },
        ],
    ]
]


class HelpersTest(unittest.TestCase):

    def test_check_backups_status(self):
        """
        Test to check backups status and add errors to _backup_errors correctly if backups failed.
        """

        check_backups_status(dataset)

        # Test that we have 2 errors
        self.assertEqual(len(_backup_errors[BackupError.VerificationFailed]), 2)

    def test_check_last_backups_expiration(self):
        """
        Test to check last backups age and add errors to _backup_errors correctly if some backups are too old.
        """

        check_last_backups_expiration(dataset, 24)
        # Test that we have 1 error if we set max_spnashot_age_hours to 24 hours
        self.assertEqual(len(_backup_errors[BackupError.VerificationTooOld]), 2)
