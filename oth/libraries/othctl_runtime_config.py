
import os
from pathlib import Path

class othctl_runtime_config:
    """
    The othctl_runtime_config class gathers all available
    runtime settings into a single class. All variables are
    public and generally shouldn't be changed after this class
    is initialized.
    """

    def __init__(self):

        # Set defaults for each variable
        self.harness_dir = Path(__file__).resolve().parent.parent.parent
        self.machine_name = set_from_environ('OTHCTL_MACHINE', default='master', regex=r'^[a-zA-Z0-9]+$')
        self.machine_type = set_from_environ('OTHCTL_MACHINE_TYPE', default='linux_x86_64')
        self.scheduler_type = set_from_environ('OTHCTL_SCHEDULER_TYPE')

        # Repository settings
        self.type_of_repository = set_from_environ('OTHCTL_TYPE_OF_REPOSITORY', default='git')
        self.git_data_transfer_protocol = set_from_environ('OTHCTL_GIT_DATA_TRANSFER_PROTOCOL', default='ssh')
        self.git_machine_name = set_from_environ('OTHCTL_GIT_MACHINE_NAME', default=self.__machine_name)
        self.git_app_parent_dir = set_from_environ('OTHCTL_GIT_APP_PARENT_DIR', default='')
        self.git_ssh_server_url = set_from_environ('OTHCTL_GIT_SSH_SERVER_URL')
        self.git_https_server_url = set_from_environ('OTHCTL_GIT_HTTPS_SERVER_URL')

        # Queueing defaults
        self.batch_queue = set_from_environ('OTHCTL_BATCH_QUEUE')
        self.project_id = set_from_environ('OTHCTL_PROJECT_ID')
        self.path_to_sspace = set_from_environ('OTHCTL_PATH_TO_SSPACE')
        self.path_to_tests = set_from_environ('OTHCTL_PATH_TO_TESTS')
        self.system_log_tag = set_from_environ('OTHCTL_SYSTEM_LOG_TAG')

        # Overrides for batch queueing defaults
        self.submit_args = set_from_environ('OTHCTL_SUBMIT_ARGS')
        self.submit_queue = set_from_environ('OTHCTL_SUBMIT_QUEUE')
        self.submit_acct = set_from_environ('OTHCTL_SUBMIT_ACCT')

        self.node_metadata_file = set_from_environ('OTHCTL_NODE_LOCATION_FILE', default='NONE')

        # Kafka variables
        self.kafka_uri = set_from_environ('OTHCTL_KAFKA_URI')
        self.kafka_username = set_from_environ('OTHCTL_KAFKA_USERNAME')
        self.kafka_events_topic = set_from_environ('OTHCTL_KAFKA_EVENTS_TOPIC')
        self.kafka_metrics_topic = set_from_environ('OTHCTL_KAFKA_METRICS_TOPIC')
        self.kafka_node_health_topic = set_from_environ('OTHCTL_KAFKA_NODE_HEALTH_TOPIC')
        self.kafka_db_type = set_from_environ('OTHCTL_KAFKA_DB_TYPE')
        self.kafka_ssl_ca_location = set_from_environ('OTHCTL_KAFKA_SSL_CA_LOCATION')
        self.kafka_ssl_certificate_location = set_from_environ('OTHCTL_KAFKA_SSL_CERTIFICATE_LOCATION')
        self.kafka_dry_run = set_from_environ('OTHCTL_KAFKA_DRY_RUN')
        self.kafka_disable = set_from_environ('OTHCTL_KAFKA_DISABLE')

        # InfluxDB variables
        self.influxdb_uri = set_from_environ('OTHCTL_INFLUXDB_URI')
        self.influxdb_token = set_from_environ('OTHCTL_INFLUXDB_TOKEN')
        self.influxdb_bucket = set_from_environ('OTHCTL_INFLUXDB_BUCKET')
        self.influxdb_org = set_from_environ('OTHCTL_INFLUXDB_ORG')
        self.influxdb_precision = set_from_environ('OTHCTL_INFLUXDB_PRECISION', default='ns')
        self.influxdb_dry_run = set_from_environ('OTHCTL_INFLUXDB_DRY_RUN')
        self.influxdb_disable = set_from_environ('OTHCTL_INFLUXDB_DISABLE')

def set_from_environ(envvar_name, default=None, regex=r"^.+$", required=False):
    """
    Given an environment variable name, safely checks if the
    variable is set and optionally matches the filter.
    If set in the environment and matches the filter, returns that value.
    If not set, returns the provided default value.
    """
    ret_val = os.getenv(envvar_name)
    if not ret_val:
        if required:
            raise EnvvarMissing(f"Missing environment variable: {envvar_name}.")
        # if setting by default, don't check regex matching
        ret_val = default
    elif not re.fullmatch(ret_val, regex):
        # then envvar does not pass the provided regex filter
        raise EnvvarRegexCheckFailure(f"Envvar {envvar_name} failed regular expression check of {regex}.")
    return ret_val


class EnvvarMissing(Exception):
    """Exception raised when a required environment variable is missing."""
    pass

class EnvvarRegexCheckFailure(Exception):
    """Exception raised when an environment variable does not match the provided regex."""
    pass
