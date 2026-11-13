import os

os.environ["OTHCTL_MACHINE"] = "minimal_machine"

from oth.libraries.oth_database_loggers.db_backends.oth_influxdb import InfluxDBLogger
from oth.libraries.oth_database_loggers.oth_database_logger import OthDatabaseLogger
from oth.libraries.output_hub import OutputHub


def test_multiple_influxdb(monkeypatch):

    logger = OutputHub(
        name="test_multiple_influxdb",
        log_level="DEBUG",
        log_file=None,
        console_log_level="DEBUG",
        file_log_level="DEBUG",
    )

    with monkeypatch.context() as mp:
        test_uri = "https://a.com:1234/api/v2/write?org=myorg&bucket=mybucket&precision=ns;https://b.com/api/v2/write?org=myorg&bucket=mybucket"
        test_token = "mytoken1234;mytoken5678"
        mp.setenv("OTHCTL_INFLUXDB_URI", test_uri)
        mp.setenv("OTHCTL_INFLUXDB_TOKEN", test_token)

        from oth.config import othctl_runtime_config

        othctl_runtime_config.influxdb_uri = test_uri
        othctl_runtime_config.influxdb_token = test_token

        othdb_logger = OthDatabaseLogger(logger, check_health=False)
        assert len(othdb_logger.enabled_backends) == 2


def test_influxdb_url_parsing(monkeypatch):

    logger = OutputHub(
        name="test_influxdb_url_parsing",
        log_level="CRITICAL",
        log_file=None,
        console_log_level="CRITICAL",
        file_log_level="CRITICAL",
    )

    test_url = "https://a.com:1234/api/v2/write?org=myorg&bucket=mybucket&precision=myprecision"

    db_backend = InfluxDBLogger(
        uri=test_url,
        token="abc123",
        logger=logger,
        check_health=False,
    )

    assert db_backend.url == "https://a.com:1234"
    assert db_backend.org == "myorg"
    assert db_backend.bucket == "mybucket"
    assert db_backend.precision == "myprecision"
    assert db_backend._get_write_url() == test_url
