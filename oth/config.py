import configparser
import os
import re
from pathlib import Path
from typing import Optional

from oth.libraries.rgt_utilities import set_harness_environment


class OthctlRuntimeConfig:
    """
    The othctl_runtime_config class gathers all available
    runtime settings into a single class. All variables are
    public and generally shouldn't be changed after this class
    is initialized (the main exception is when values are
    overridden via the CLI).
    """

    def __init__(self):

        # Set defaults for each variable
        self.harness_dir = Path(__file__).resolve().parent.parent
        self.machine_name = get_from_environ(
            "OTHCTL_MACHINE", default="master", regex=r"^[a-zA-Z0-9]+$"
        )

        configfile = get_from_environ("OTHCTL_CONFIG_FILE")
        self.config = configfile if configfile else f"{self.machine_name}.ini"

        if Path(self.config).name == self.config:
            # Only base file name given, search CWD, then harness_dir/configs
            working_dir_config = Path(os.getcwd(), self.config)
            harness_dir_config = Path(self.harness_dir, "configs", self.config)
            if working_dir_config.is_file():
                self.config = str(working_dir_config.resolve())
            elif harness_dir_config.is_file():
                self.config = str(harness_dir_config)

        # Read config file
        self.set_env_from_config()

        self.machine_type = get_from_environ(
            "OTHCTL_MACHINE_TYPE", default="linux_x86_64"
        )
        self.scheduler_type = get_from_environ("OTHCTL_SCHEDULER_TYPE", required=True)

        # Repository settings
        self.type_of_repository = get_from_environ(
            "OTHCTL_TYPE_OF_REPOSITORY", default="git"
        )
        self.git_data_transfer_protocol = get_from_environ(
            "OTHCTL_GIT_DATA_TRANSFER_PROTOCOL", default="ssh"
        )
        self.git_machine_name = get_from_environ(
            "OTHCTL_GIT_MACHINE_NAME", default="master"
        )
        self.git_app_parent_dir = get_from_environ(
            "OTHCTL_GIT_APP_PARENT_DIR", default=""
        )
        self.git_ssh_server_url = get_from_environ("OTHCTL_GIT_SSH_SERVER_URL")
        self.git_https_server_url = get_from_environ("OTHCTL_GIT_HTTPS_SERVER_URL")

        # Queueing defaults
        self.batch_queue = get_from_environ("OTHCTL_BATCH_QUEUE")
        self.project_id = get_from_environ("OTHCTL_PROJECT_ID")
        self.path_to_sspace: str = get_from_environ("OTHCTL_PATH_TO_SSPACE")
        self.path_to_tests = get_from_environ("OTHCTL_PATH_TO_TESTS")
        self.system_log_tag = get_from_environ("OTHCTL_SYSTEM_LOG_TAG")

        # Overrides for batch queueing defaults
        self.submit_args = get_from_environ("OTHCTL_SUBMIT_ARGS")
        self.submit_queue = get_from_environ("OTHCTL_SUBMIT_QUEUE")
        self.submit_acct = get_from_environ("OTHCTL_SUBMIT_ACCT")

        self.node_metadata_file = get_from_environ(
            "OTHCTL_NODE_LOCATION_FILE", default="NONE"
        )

        # Kafka variables
        self.kafka_uri = get_from_environ("OTHCTL_KAFKA_URI")
        self.kafka_username = get_from_environ("OTHCTL_KAFKA_USERNAME")
        self.kafka_events_topic = get_from_environ("OTHCTL_KAFKA_EVENTS_TOPIC")
        self.kafka_metrics_topic = get_from_environ("OTHCTL_KAFKA_METRICS_TOPIC")
        self.kafka_node_health_topic = get_from_environ(
            "OTHCTL_KAFKA_NODE_HEALTH_TOPIC"
        )
        self.kafka_db_type = get_from_environ("OTHCTL_KAFKA_DB_TYPE")
        self.kafka_ssl_ca_location = get_from_environ("OTHCTL_KAFKA_SSL_CA_LOCATION")
        self.kafka_ssl_certificate_location = get_from_environ(
            "OTHCTL_KAFKA_SSL_CERTIFICATE_LOCATION"
        )
        self.kafka_dry_run = get_from_environ("OTHCTL_KAFKA_DRY_RUN")
        self.kafka_disable = get_from_environ("OTHCTL_KAFKA_DISABLE")

        # InfluxDB variables
        self.influxdb_uri = get_from_environ("OTHCTL_INFLUXDB_URI")
        self.influxdb_token = get_from_environ("OTHCTL_INFLUXDB_TOKEN")
        self.influxdb_bucket = get_from_environ("OTHCTL_INFLUXDB_BUCKET")
        self.influxdb_org = get_from_environ("OTHCTL_INFLUXDB_ORG")
        self.influxdb_precision = get_from_environ(
            "OTHCTL_INFLUXDB_PRECISION", default="ns"
        )
        self.influxdb_dry_run = get_from_environ("OTHCTL_INFLUXDB_DRY_RUN")
        self.influxdb_disable = get_from_environ("OTHCTL_INFLUXDB_DISABLE")

        # Make work dir
        os.makedirs(self.path_to_sspace, exist_ok=True)

    def set_env_from_config(self):
        """Given a config file, export the environment variables to the environment"""
        if Path(self.config).is_file():
            cfg = configparser.ConfigParser()
            cfg.read(self.config)

            for section in cfg.sections():
                set_harness_environment(cfg[section])
        else:
            raise NameError(f"Harness config file not found: {self.config}")


def get_from_environ(
    envvar_name: str,
    default: Optional[str] = None,
    regex: str = r"^.*$",
    required: bool = False,
) -> Optional[str]:
    raw: Optional[str] = os.getenv(envvar_name)

    if raw is None:
        if required:
            raise ValueError(f"Missing environment variable: {envvar_name}")
        return default

    if not re.fullmatch(regex, raw):
        raise ValueError(
            f"Environment variable {envvar_name!r} failed regular expression check {regex!r}"
        )

    return raw


othctl_runtime_config: OthctlRuntimeConfig = OthctlRuntimeConfig()
