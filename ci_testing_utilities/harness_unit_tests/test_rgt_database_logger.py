import os
import tempfile
import unittest

from harness.libraries.rgt_database_loggers.rgt_database_logger import RgtDatabaseLogger


class FakeLogger:
    def __init__(self):
        self.warning_messages = []

    def doWarningLogging(self, message):
        self.warning_messages.append(message)


class TestRgtDatabaseLogger(unittest.TestCase):
    def test_log_event_skips_missing_run_archive(self):
        logger = FakeLogger()
        database_logger = RgtDatabaseLogger.__new__(RgtDatabaseLogger)
        database_logger.logger = logger
        database_logger.enabled_backends = []

        event = {
            'test_id': 'test-id',
            'app': 'app',
            'test': 'test',
            'runtag': 'runtag',
            'machine': 'machine',
            'run_archive': os.path.join(tempfile.gettempdir(), 'missing-run-archive'),
        }
        current_directory = os.getcwd()

        self.assertFalse(database_logger.log_event(event))
        self.assertEqual(current_directory, os.getcwd())
        self.assertEqual(len(logger.warning_messages), 1)
        self.assertIn(event['run_archive'], logger.warning_messages[0])


if __name__ == '__main__':
    unittest.main()
