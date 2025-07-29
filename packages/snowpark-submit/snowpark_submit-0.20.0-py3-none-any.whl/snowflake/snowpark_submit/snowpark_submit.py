#!/usr/bin/env python

"""A utility script that takes a pyspark script and runs it in the SAS environment.

Typical usage example:
    snowpark-submit ./tools/examples_row.py

"""
import argparse
import logging
import sys
from functools import partial

from snowflake.snowpark_submit.cluster_mode.job_runner import StatusInfo
from snowflake.snowpark_submit.cluster_mode.spark_connect.spark_connect_job_runner import (
    SparkConnectJobRunner,
)

logger = logging.getLogger("snowpark-submit")


def setup_logging(log_level):
    logger = logging.getLogger("snowpark-submit")
    logger.setLevel(log_level)
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [Thread %(thread)d] - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    sas_logger = logging.getLogger("snowflake_connect_server")
    sas_logger.setLevel(log_level)
    for handler in sas_logger.handlers:
        handler.setLevel(log_level)


def init_args(args: list[str] | None = None) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run a Spark script in SAS environment.",
        add_help=False,
        usage="""NOTE: All spark-submit options are displayed here, currently unsupported options are marked [DEPRECATED]
    Usage: snowpark-submit [options] <app jar | python file> [app arguments]
    """,
    )
    # Other spark-submit usage (we may add support for these in the future):
    # Usage: snowpark-submit --kill [submission ID] --master [spark://...]
    # Usage: snowpark-submit --status [submission ID] --master [spark://...]
    # Usage: snowpark-submit run-example [options] example-class [example args]
    options_group = parser.add_argument_group("Options")
    spark_connect_group = parser.add_argument_group("Spark Connect only")
    cluster_deploy_group = parser.add_argument_group("Cluster Deploy mode only")
    spark_standalone_or_mesos_cluster_group = parser.add_argument_group(
        "[Unsupported] Spark standalone or Mesos with cluster deploy mode only"
    )
    k8s_group = parser.add_argument_group(
        "[Unsupported] Spark standalone, Mesos or K8s with cluster deploy mode only"
    )
    spark_standalone_mesos_group = parser.add_argument_group(
        "[Unsupported] Spark standalone and Mesos only"
    )
    spark_standalone_yarn_group = parser.add_argument_group(
        "[Unsupported] Spark standalone, YARN and Kubernetes only"
    )
    spark_yarn_k8s_group = parser.add_argument_group(
        "[Unsupported] Spark on YARN and Kubernetes only"
    )
    spark_yarn_group = parser.add_argument_group("Spark on YARN only")
    snowflake_configs_group = parser.add_argument_group("Snowflake specific configs")

    options_group.add_argument(
        "--master",
        metavar="MASTER_URL",
        type=str,
        help="[DEPRECATED] spark://host:port, mesos://host:port, yarn, k8s://https://host:port, or local (Default: local[*]).",
    )
    options_group.add_argument(
        "--deploy-mode",
        metavar="DEPLOY_MODE",
        type=str,
        choices=["client", "cluster"],
        help="[DEPRECATED] Whether to launch the driver program locally ('client') or on one of the worker machines inside the cluster ('cluster') (Default: client).",
    )
    options_group.add_argument(
        "--class",
        metavar="CLASS_NAME",
        type=str,
        help="Your application's main class (for Java / Scala apps).",
    )
    options_group.add_argument(
        "--name",
        metavar="NAME",
        type=str,
        help="A name of your application.",
    )
    options_group.add_argument(
        "--jars",
        metavar="JAR",
        type=str,
        help="Comma-separated list of jars to include on the driver and executor classpaths.",
    )
    options_group.add_argument(
        "--packages",
        type=str,
        nargs="*",
        help="[DEPRECATED] Comma-separated list of maven coordinates of jars to include on the driver and executor classpaths. Will search the local maven repo, then maven central and any additional remote repositories given through --repositories. The format for the coordinates should be groupId:artifactId:version.",
    )
    options_group.add_argument(
        "--exclude-packages",
        type=str,
        nargs="*",
        help="Comma-separated list of groupId:artifactId, to exclude while resolving the dependencies provided in --packages to avoid dependency conflicts.",
    )
    options_group.add_argument(
        "--repositories",
        type=str,
        nargs="*",
        help="[DEPRECATED] Comma-separated list of additional remote repositories to search for the maven coordinates given with --packages.",
    )
    options_group.add_argument(
        "--py-files",
        metavar="PY_FILES",
        type=str,
        help="Comma-separated list of .zip, .egg, or .py files to place on the PYTHONPATH for Python apps.",
    )
    options_group.add_argument(
        "--files",
        metavar="FILES",
        type=str,
        nargs="*",
        help="[DEPRECATED] Comma-separated list of files to be placed in the working directory of each executor.",
    )
    options_group.add_argument(
        "--archives",
        metavar="ARCHIVES",
        type=str,
        nargs="*",
        help="[DEPRECATED] Comma-separated list of archives to be extracted into the working directory of each executor.",
    )
    options_group.add_argument(
        "--conf",
        "-c",
        metavar="PROP=VALUE",
        type=str,
        nargs="*",
        help="Arbitrary Spark configuration property.",
    )
    options_group.add_argument(
        "--properties-file",
        metavar="FILE",
        type=str,
        help="Path to a file from which to load extra properties. If not specified, this will look for conf/spark-defaults.conf.",
    )
    options_group.add_argument(
        "--driver-memory",
        metavar="MEM",
        type=str,
        help="[DEPRECATED] Memory for driver (e.g. 1000M, 2G) (Default: 1024M).",
    )
    options_group.add_argument(
        "--driver-java-options",
        type=str,
        help="[DEPRECATED] Extra Java options to pass to the driver.",
    )
    options_group.add_argument(
        "--driver-library-path",
        type=str,
        help="[DEPRECATED] Extra library path entries to pass to the driver.",
    )
    options_group.add_argument(
        "--driver-class-path",
        type=str,
        help="[DEPRECATED] Extra class path entries to pass to the driver. Note that jars added with --jars are automatically included in the classpath.",
    )
    options_group.add_argument(
        "--executor-memory",
        metavar="MEM",
        type=str,
        help="[DEPRECATED] Memory per executor (e.g. 1000M, 2G) (Default: 1G).",
    )
    options_group.add_argument(
        "--proxy-user",
        type=str,
        help="[DEPRECATED] User to impersonate when submitting the application. This argument does not work with --principal / --keytab.",
    )
    options_group.add_argument(
        "--help",
        "-h",
        action="help",
        help="Show this help message and exit.",
    )
    options_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print additional debug output.",
    )
    options_group.add_argument(
        "--version",
        action="store_true",
        help="Print the version of current Spark.",
    )
    spark_connect_group.add_argument(
        "--remote",
        metavar="CONNECT_URL",
        type=str,
        default="sc://localhost:15002",  # Different from snowpark-session, to avoid conflicts.
        help="URL to connect to the server for Spark Connect, e.g., sc://host:port. --master and --deploy-mode cannot be set together with this option. This option is experimental, and might change between minor releases.",
    )
    spark_connect_group.add_argument(
        "--skip-init-sas",
        action="store_true",
        help="If given, skip initialize SAS. This is used in server side testing.",
    )
    cluster_deploy_group.add_argument(
        "--driver-cores",
        metavar="NUM",
        type=str,
        help="[DEPRECATED] Number of cores used by the driver, only in cluster mode (Default: 1).",
    )
    spark_standalone_or_mesos_cluster_group.add_argument(
        "--supervise",
        action="store_true",
        help="[DEPRECATED] If given, restart the driver on failure.",
    )
    k8s_group.add_argument(
        "--kill",
        metavar="SUBMISSION_ID",
        type=str,
        help="[DEPRECATED] If given, kills the driver specified.",
    )
    k8s_group.add_argument(
        "--status",
        metavar="SUBMISSION_ID",
        type=str,
        help="[DEPRECATED] If given, requests the status of the driver specified.",
    )
    spark_standalone_mesos_group.add_argument(
        "--total-executor-cores",
        metavar="NUM",
        type=str,
        help="[DEPRECATED] Total cores for all executors.",
    )
    spark_standalone_yarn_group.add_argument(
        "--executor-cores",
        metavar="NUM",
        type=str,
        help="[DEPRECATED] Number of cores per executor. (Default: 1 in YARN mode, or all available cores on the worker in standalone mode).",
    )
    spark_yarn_k8s_group.add_argument(
        "--num-executors",
        metavar="NUM",
        type=str,
        help="[DEPRECATED] Number of executors to launch (Default: 2).\nIf dynamic allocation is enabled, the initial number of executors will be at least NUM.",
    )
    spark_yarn_k8s_group.add_argument(
        "--principal",
        metavar="PRINCIPAL",
        type=str,
        help="[DEPRECATED] Principal to be used to login to KDC.",
    )
    spark_yarn_k8s_group.add_argument(
        "--keytab",
        metavar="KEYTAB",
        type=str,
        help="[DEPRECATED] The full path to the file that contains the keytab for the principal specified.",
    )
    spark_yarn_group.add_argument(
        "--queue",
        metavar="QUEUE_NAME",
        type=str,
        help="[DEPRECATED] The YARN queue to submit to (Default: 'default').",
    )
    snowflake_configs_group.add_argument(
        "--snowpark-connect-version",
        metavar="SNOWPARK_CONNECT_VERSION",
        type=str,
        help="Version for Snowpark Connect server and client images (default: latest). Accepts version in the form of `x.y.z` or `x.y` (points to latest patch version of x.y)",
    )
    snowflake_configs_group.add_argument(
        "--account",
        metavar="SNOWFLAKE_ACCOUNT",
        type=str,
        help="Snowflake account to be used. Overrides the account in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--user",
        metavar="SNOWFLAKE_USER",
        type=str,
        help="Snowflake user to be used. Overrides the user in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--authenticator",
        metavar="SNOWFLAKE_AUTHENTICATOR",
        type=str,
        help="Authenticator for snowflake login. Overrides the authenticator in the connections.toml file if specified. If not specified, defaults to user password authenticator.",
    )
    snowflake_configs_group.add_argument(
        "--token-file-path",
        metavar="SNOWFLAKE_TOKEN_FILE_PATH",
        type=str,
        help="Path to a file containing the OAuth token for Snowflake. Overrides the token file path in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--password",
        metavar="SNOWFLAKE_PASSWORD",
        type=str,
        help="Password for snowflake user. Overrides the password in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--role",
        metavar="SNOWFLAKE_ROLE",
        type=str,
        help="Snowflake role to be used. Overrides the role in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--host",
        metavar="SNOWFLAKE_HOST",
        type=str,
        help="Host for snowflake deployment. Overrides the host in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--database",
        metavar="SNOWFLAKE_DATABASE_NAME",
        type=str,
        help="Snowflake database to be used in the session. Overrides the database in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--schema",
        metavar="SNOWFLAKE_SCHEMA_NAME",
        type=str,
        help="Snowflake schema to be used in the session. Overrides the schema in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--warehouse",
        metavar="SNOWFLAKE_WAREHOUSE_NAME",
        type=str,
        help="Snowflake warehouse to be used in the session. Overrides the warehouse in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--compute-pool",
        metavar="SNOWFLAKE_COMPUTE_POOL",
        type=str,
        help="Snowflake compute pool for running provided workload. Overrides the compute pool in the connections.toml file if specified.",
    )
    snowflake_configs_group.add_argument(
        "--comment",
        metavar="COMMENT",
        type=str,
        help="A message associated with the workload. Can be used to identify the workload in Snowflake.",
    )

    def snowflake_stage_str(value: str) -> str:
        if not value.startswith("@"):
            raise argparse.ArgumentTypeError(
                "The --snowflake-stage argument must start with '@', e.g., '@my_stage'."
            )
        return value

    snowflake_configs_group.add_argument(
        "--snowflake-stage",
        metavar="SNOWFLAKE_STAGE",
        type=snowflake_stage_str,
        help="Snowflake stage, where workload files are uploaded.",
    )
    snowflake_configs_group.add_argument(
        "--external-access-integrations",
        metavar="SNOWFLAKE_EXTERNAL_ACCESS_INTEGRATIONS",
        type=str,
        nargs="*",
        help="Snowflake External Acccess Integrations required by the workload.",
    )
    snowflake_configs_group.add_argument(
        "--snowflake-log-level",
        metavar="SNOWFLAKE_LOG_LEVEL",
        type=str,
        choices=["INFO", "ERROR", "NONE"],
        help="Log level for Snowflake event table. ['INFO', 'ERROR', 'NONE'] (Default: INFO).",
    )
    snowflake_configs_group.add_argument(
        "--snowflake-workload-name",
        metavar="SNOWFLAKE_WORKLOAD_NAME",
        type=str,
        help="Name of the workload to be run in Snowflake.",
    )
    snowflake_configs_group.add_argument(
        "--snowflake-connection-name",
        metavar="SNOWFLAKE_CONNECTION_NAME",
        type=str,
        default=None,
        help="Name of the connection in connections.toml file to use as base configuration. Command-line arguments will override any values from connections.toml.",
    )
    snowflake_configs_group.add_argument(
        "--workload-status",
        action="store_true",
        help="Print the detailed status of the workload.",
    )
    snowflake_configs_group.add_argument(
        "--display-logs",
        action="store_true",
        help="Whether to print application logs to console when --workload-status is specified.",
    )
    snowflake_configs_group.add_argument(
        "--kill-workload",
        action="store_true",
        help="Adds tag to terminate the workload given by --workload-name.",
    )
    snowflake_configs_group.add_argument(
        "--wait-for-completion",
        action="store_true",
        help="In cluster mode, when specified, run the workload in blocking mode and wait for completion. Can also be used with --workload-status to wait for an existing workload to complete.",
    )
    snowflake_configs_group.add_argument(
        "--requirements-file",
        metavar="REQUIREMENTS_FILE",
        type=str,
        help="Path to a requirements.txt file containing Python package dependencies to install before running the workload. Requires external access integration for PyPI.",
    )
    parser.add_argument(
        "filename",
        metavar="FILE",
        nargs="?",
        type=str,
        help=argparse.SUPPRESS,
    )

    args, unknown_args = parser.parse_known_args(args)
    args.app_arguments = unknown_args

    return args, [action.dest for action in snowflake_configs_group._group_actions]


def generate_spark_submit_cmd(
    args: argparse.Namespace,
    snowflake_config_keys: list[str],
    entrypoint_arg: str = "spark-submit",
) -> list[str]:
    args_for_spark = [entrypoint_arg]
    for k, v in vars(args).items():
        if (
            v is not None
            and k
            not in [
                "filename",
                "verbose",
                "version",
                "supervise",
                "skip_init_sas",
                "deploy_mode",
                "app_arguments",
            ]
            + snowflake_config_keys
        ):
            args_for_spark.append(f"--{k.replace('_', '-')}")
            args_for_spark.append(v)
    if args.verbose:
        args_for_spark.append("--verbose")
        setup_logging(logging.INFO)
    else:
        setup_logging(logging.ERROR)
    if args.version:
        args_for_spark.append("--version")
    args_for_spark.append(args.filename)
    args_for_spark.extend(args.app_arguments)
    return args_for_spark


def run():
    args, snowflake_config_keys = init_args()

    # Check that exactly one of the main operations is specified
    operations_count = sum(
        [args.workload_status, args.kill_workload, bool(args.filename)]
    )

    if operations_count != 1:
        error_msg = "You must specify exactly one operation at a time: 1) either a Python file to run, 2) --workload-status, or 3) --kill-workload"
        logger.error(error_msg)
        return StatusInfo(
            exit_code=1,
            error=error_msg,
        )

    job_runner = SparkConnectJobRunner(
        args,
        partial(generate_spark_submit_cmd, snowflake_config_keys=snowflake_config_keys),
    )

    if args.workload_status:
        result = job_runner.describe()
        if args.wait_for_completion and not result.terminated:
            result = job_runner.wait_for_service_completion(
                args.snowflake_workload_name
            )
        return result

    elif args.kill_workload:
        return job_runner.end_workload()

    else:
        exit_code = job_runner.run()
        return StatusInfo(exit_code=exit_code)


def runner_wrapper(test_mode=False):
    logger.debug("Runner starts.")

    result = run()
    exit_status = result.exit_code
    # send the exit status in lower byte as 0/1 flag
    if exit_status != 0:
        logger.error("Unexpected Exit: non-zero exit code.")
        exit_status = 1
    if test_mode:
        return result
    else:
        sys.exit(exit_status)


if __name__ == "__main__":
    runner_wrapper()
