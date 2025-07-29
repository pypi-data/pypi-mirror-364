import copy
import os
import sys
from contextlib import contextmanager

import pytest
from snowflake.snowpark_submit.cluster_mode.job_runner import (
    generate_random_name,
    logger,
)
from snowflake.snowpark_submit.cluster_mode.spark_connect.spark_connect_job_runner import (
    SparkConnectJobRunner,
)
from snowflake.snowpark_submit.snowpark_submit import init_args, runner_wrapper

from snowflake.connector.errors import Error
from snowflake.snowpark import Row

from .conftest import DEFAULT_TEST_CONNECTION_NAME

current_dir = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = current_dir + "/resources"

# SAS versions to test against
SAS_VERSIONS = ["latest", "0.18.0", "0.19.0", "0.20.0"]


@contextmanager
def argv_context(test_args):
    original_argv = sys.argv
    try:
        sys.argv = test_args
        yield
    finally:
        sys.argv = original_argv


@contextmanager
def sas_version_set_via_env_vars(sas_version):
    try:
        os.environ["SNOWFLAKE_SYSTEM_REGISTRY_SERVER_IMAGE_TAG"] = sas_version
        os.environ["SNOWFLAKE_SYSTEM_REGISTRY_CLIENT_IMAGE_TAG"] = sas_version
        yield
    finally:
        os.environ.pop("SNOWFLAKE_SYSTEM_REGISTRY_SERVER_IMAGE_TAG", None)
        os.environ.pop("SNOWFLAKE_SYSTEM_REGISTRY_CLIENT_IMAGE_TAG", None)


class TestSnowparkSubmit:
    @pytest.mark.parametrize("sas_version", SAS_VERSIONS)
    def test_snowpark_submit_cluster_mode_python(
        self,
        spcs_snowflake_config,
        spcs_snowpark_session,
        skip_tests_out_of_aws_us_west_2,
        pyspark_utils_zip,
        sas_version,
    ):
        with sas_version_set_via_env_vars(sas_version):
            pyspark_example_dir = RESOURCES_DIR + "/snowpark-submit-pyspark-example"

            workload_name = generate_random_name(
                prefix="snowpark_submit_python_spcs_test_"
            ).upper()
            table_name = "snowpark_submit_python_spcs_test_table"
            spcs_snowpark_session.sql(
                f"create or replace table {table_name} (id int, val float)"
            ).collect()

            test_args = [
                "snowpark-submit",
                "--py-files",
                str(pyspark_utils_zip.resolve()),
                "--wait-for-completion",
                "--snowflake-workload-name",
                workload_name,
                pyspark_example_dir + "/main.py",
                table_name,
            ]
            self._snowpark_submit_cluster_mode_helper(
                test_args + spcs_snowflake_config,
                spcs_snowpark_session,
                workload_name,
                table_name,
                [Row(ID=1, VAL=2.0), Row(ID=2, VAL=3.0), Row(ID=4, VAL=5.0)],
            )

            spcs_snowpark_session.sql(f"drop table if exists {table_name}").collect()

    @pytest.mark.parametrize("sas_version", SAS_VERSIONS)
    def test_snowpark_submit_cluster_mode_scala(
        self,
        spcs_snowflake_config,
        spcs_snowpark_session,
        spcs_scala_test_table,
        skip_tests_out_of_aws_us_west_2,
        sas_version,
    ):
        with sas_version_set_via_env_vars(sas_version):
            scala_example_dir = RESOURCES_DIR + "/snowpark-submit-scala-example"
            workload_name = generate_random_name(
                prefix="snowpark_submit_scala_spcs_test_"
            ).upper()

            test_args = [
                "snowpark-submit",
                "--class",
                "com.example.SnowparkConnectApp",
                "--snowflake-workload-name",
                workload_name,
                scala_example_dir + "/target/original-scala-maven-example-0.1.0.jar",
                spcs_scala_test_table,
            ]
            self._snowpark_submit_cluster_mode_helper(
                test_args + spcs_snowflake_config,
                spcs_snowpark_session,
                workload_name,
                spcs_scala_test_table,
                [
                    Row(NAME="Alice", AGE=29),
                    Row(NAME="Bob", AGE=31),
                    Row(NAME="Catherine", AGE=25),
                ],
            )

    @pytest.mark.parametrize("sas_version", SAS_VERSIONS)
    def test_snowpark_submit_cluster_mode_scala_user_stage(
        self,
        spcs_snowflake_config,
        spcs_snowpark_session,
        spcs_scala_test_table,
        skip_tests_out_of_aws_us_west_2,
        sas_version,
    ):
        with sas_version_set_via_env_vars(sas_version):
            scala_example_dir = RESOURCES_DIR + "/snowpark-submit-scala-example"
            workload_name = generate_random_name(
                prefix="snowpark_submit_scala_spcs_test_"
            ).upper()
            stage_name = "sas_test_spcs_user_stage"
            spcs_snowpark_session.sql(
                f"CREATE OR REPLACE STAGE {stage_name} ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') DIRECTORY = ( ENABLE = true );"
            ).collect()
            spcs_snowpark_session.sql(
                f"put file://{scala_example_dir}/target/original-scala-maven-example-0.1.0.jar @{stage_name}/snowpark-submit-scala-example/target/ auto_compress=FALSE overwrite=TRUE"
            ).collect()

            test_args = [
                "snowpark-submit",
                "--class",
                "com.example.SnowparkConnectApp",
                "--snowflake-workload-name",
                workload_name,
                "--snowflake-stage",
                f"@{stage_name}",
                f"@{stage_name}/snowpark-submit-scala-example/target/original-scala-maven-example-0.1.0.jar",
                spcs_scala_test_table,
            ]
            self._snowpark_submit_cluster_mode_helper(
                test_args + spcs_snowflake_config,
                spcs_snowpark_session,
                workload_name,
                # table_name,
                spcs_scala_test_table,
                [
                    Row(NAME="Alice", AGE=29),
                    Row(NAME="Bob", AGE=31),
                    Row(NAME="Catherine", AGE=25),
                ],
            )
            spcs_snowpark_session.sql(f"drop stage if exists {stage_name}").collect()

    def _snowpark_submit_cluster_mode_helper(
        self, test_args, snowpark_session, service_name, table_name, expected_res
    ):
        with argv_context(test_args):
            result = runner_wrapper(test_mode=True)
            assert (
                result.exit_code == 0
            ), f"Exit code should be 0, actual: {result.exit_code}"

        status_test_args = [
            "snowpark-submit",
            "--workload-status",
            "--wait-for-completion",
            "--display-logs",
            "--snowflake-workload-name",
            service_name,
            "--snowflake-connection-name",
            DEFAULT_TEST_CONNECTION_NAME,
        ]

        with argv_context(status_test_args):
            status_result = runner_wrapper(test_mode=True)
            assert (
                status_result.exit_code == 0
            ), f"Status check exit code should be 0, actual: {status_result.exit_code}"
            assert (
                status_result.service_status == "DONE"
            ), f"Service status is not DONE: {status_result.service_status}"
            assert (
                status_result.logs is not None
            ), "Logs should not be None when --display-logs is used"
            assert (
                len(status_result.logs) > 1
            ), f"Expected logs to be retrieved, but got empty logs. Status: {status_result.service_status}"

        res = snowpark_session.sql(f"SELECT * FROM {table_name}").collect()
        logger.debug(res)
        assert res == expected_res

        snowpark_session.sql(f"drop service if exists {service_name}").collect()

    def test_execute_service_sql_template(self):
        base_args = init_args(
            [
                "--compute-pool",
                "test_compute_pool",
                "--snowflake-connection-name",
                DEFAULT_TEST_CONNECTION_NAME,
                "--snowflake-workload-name",
                "snowpark_submit_test_workload",
                "workload_test_file.py",
            ]
        )[0]

        def _test_case(args, expected_sql):
            runner = SparkConnectJobRunner(args, None)
            sql = runner.generate_execute_service_sql(
                args.snowflake_workload_name, "<spcs_spec_yaml_file>"
            )
            assert sql == expected_sql

        args = copy.deepcopy(base_args)
        _test_case(
            args,
            """
EXECUTE JOB SERVICE
    IN COMPUTE POOL test_compute_pool
    NAME = snowpark_submit_test_workload
    ASYNC = TRUE
    FROM SPECIFICATION $$
    <spcs_spec_yaml_file>
    $$
    """,
        )

        args = copy.deepcopy(base_args)
        args.external_access_integrations = ["integration1", "INTEGRATION2"]
        _test_case(
            args,
            """
EXECUTE JOB SERVICE
    IN COMPUTE POOL test_compute_pool
    NAME = snowpark_submit_test_workload
    ASYNC = TRUE
    EXTERNAL_ACCESS_INTEGRATIONS = (integration1, INTEGRATION2)
    FROM SPECIFICATION $$
    <spcs_spec_yaml_file>
    $$
    """,
        )

    @pytest.mark.parametrize("sas_version", SAS_VERSIONS)
    def test_snowpark_submit_cluster_mode_python_without_connection_file(
        self,
        spcs_snowpark_session,
        skip_tests_out_of_aws_us_west_2,
        pyspark_utils_zip,
        sas_version,
    ):
        with sas_version_set_via_env_vars(sas_version):
            from snowflake.connector.config_manager import CONFIG_MANAGER

            connection_config = CONFIG_MANAGER["connections"][
                DEFAULT_TEST_CONNECTION_NAME
            ]

            pyspark_example_dir = RESOURCES_DIR + "/snowpark-submit-pyspark-example"

            workload_name = generate_random_name(
                prefix="snowpark_submit_py_spcs_cli_"
            ).upper()
            table_name = "snowpark_submit_python_spcs_test_table_cli"
            spcs_snowpark_session.sql(
                f"create or replace table {table_name} (id int, val float)"
            ).collect()

            # use explicit connection parameters
            test_args = [
                "snowpark-submit",
                "--py-files",
                str(pyspark_utils_zip.resolve()),
                "--snowflake-workload-name",
                workload_name,
                "--account",
                connection_config.get("account"),
                "--host",
                connection_config.get("host"),
                "--user",
                connection_config.get("user"),
                "--password",
                connection_config.get("password"),
                "--compute-pool",
                connection_config.get("compute_pool"),
            ]

            # optional
            if "database" in connection_config:
                test_args.extend(["--database", connection_config["database"]])
            if "warehouse" in connection_config:
                test_args.extend(["--warehouse", connection_config["warehouse"]])
            if "schema" in connection_config:
                test_args.extend(["--schema", connection_config["schema"]])
            if "role" in connection_config:
                test_args.extend(["--role", connection_config["role"]])

            test_args.extend(
                [
                    "--snowflake-log-level",
                    "NONE",
                    pyspark_example_dir + "/main.py",
                    table_name,
                ]
            )

            self._snowpark_submit_cluster_mode_helper(
                test_args,
                spcs_snowpark_session,
                workload_name,
                table_name,
                [Row(ID=1, VAL=2.0), Row(ID=2, VAL=3.0), Row(ID=4, VAL=5.0)],
            )

            spcs_snowpark_session.sql(f"drop table if exists {table_name}").collect()

    def test_snowpark_submit_missing_required_params(self):  # UNIT TEST
        pyspark_example_dir = RESOURCES_DIR + "/snowpark-submit-pyspark-example"

        def _test_missing_param(test_args, expected_missing_params):
            with argv_context(test_args):
                with pytest.raises(Error) as exc_info:
                    runner_wrapper(test_mode=True)
                error_message = str(exc_info.value)
                assert "Missing required connection parameters" in error_message
                for param in expected_missing_params:
                    assert param in error_message

        base_args = [
            "snowpark-submit",
            "--snowflake-workload-name",
            "test_workload",
            pyspark_example_dir + "/main.py",
        ]

        # test missing --account
        test_args = base_args.copy()
        test_args.extend(
            [
                "--host",
                "test.snowflakecomputing.com",
                "--user",
                "test_user",
                "--password",
                "test_password",
                "--compute-pool",
                "test_pool",
            ]
        )
        _test_missing_param(test_args, ["--account"])

        # test missing --host
        test_args = base_args.copy()
        test_args.extend(
            [
                "--account",
                "test_account",
                "--user",
                "test_user",
                "--password",
                "test_password",
                "--compute-pool",
                "test_pool",
            ]
        )
        _test_missing_param(test_args, ["--host"])

        # Test case missing --compute-pool
        test_args = base_args.copy()
        test_args.extend(
            [
                "--account",
                "test_account",
                "--host",
                "test.snowflakecomputing.com",
                "--user",
                "test_user",
                "--password",
                "test_password",
            ]
        )
        _test_missing_param(test_args, ["--compute-pool"])

        # Test when missing multiple parameters
        test_args = base_args.copy()
        test_args.extend(
            [
                "--user",
                "test_user",
                "--password",
                "test_password",
            ]
        )
        _test_missing_param(test_args, ["--account", "--host", "--compute-pool"])

    def test_snowpark_submit_cli_only_mode_session_config(self):
        # Tests that session config is created correctly when using CLI args only

        test_account = "test_account"
        test_host = "test.snowflakecomputing.com"
        test_user = "test_user"
        test_password = "test_password"
        test_compute_pool = "test_compute_pool"

        test_args = [
            "--account",
            test_account,
            "--host",
            test_host,
            "--user",
            test_user,
            "--password",
            test_password,
            "--compute-pool",
            test_compute_pool,
            "--snowflake-workload-name",
            "test_workload",
            "dummy_file.py",
        ]

        args, _ = init_args(test_args)

        assert args.snowflake_connection_name is None

        runner = SparkConnectJobRunner(args, None)

        expected_config = {
            "account": test_account,
            "host": test_host,
            "user": test_user,
            "password": test_password,
            "protocol": "https",
            "port": 443,
        }

        # Assert that session config was built correctly from CLI args, not from a connection file
        assert runner.custom_session_configs is not None
        for key, expected_value in expected_config.items():
            assert runner.custom_session_configs.get(key) == expected_value

        assert "connection_name" not in runner.custom_session_configs
        assert runner.args.compute_pool == test_compute_pool

    def test_snowpark_submit_cli_args_override_connection_file(self):  # unit test
        # provides an invalid password to override the one in the connection file
        # asserts that the connection file password is used instead of the CLI provided one

        pyspark_example_dir = RESOURCES_DIR + "/snowpark-submit-pyspark-example"

        test_args = [
            "snowpark-submit",
            "--snowflake-workload-name",
            "test_override_workload",
            "--snowflake-connection-name",
            DEFAULT_TEST_CONNECTION_NAME,
            "--password",
            "INVALID_PASSWORD_12345",
            pyspark_example_dir + "/main.py",
            "dummy_table",
        ]

        from snowflake.connector.errors import DatabaseError

        with argv_context(test_args):
            with pytest.raises(DatabaseError) as exc_info:
                runner_wrapper(test_mode=True)

            error_msg = str(exc_info.value)
            assert (
                "250001" in error_msg or "08001" in error_msg
            ), f"Expected authentication error code but got: {error_msg}"
            assert (
                "Incorrect username or password was specified" in error_msg
            ), f"Expected password error but got: {error_msg}"

    def test_snowpark_submit_validation_no_operation_specified(self):  # UNIT TEST
        """Test that validation fails when no operation is specified"""
        test_args = [
            "snowpark-submit",
            "--snowflake-connection-name",
            DEFAULT_TEST_CONNECTION_NAME,
        ]

        with argv_context(test_args):
            result = runner_wrapper(test_mode=True)
            assert result.exit_code == 1
            assert "You must specify exactly one operation at a time" in result.error

    def test_snowpark_submit_validation_multiple_operations_specified(
        self,
    ):  # UNIT TEST
        """Test that validation fails when multiple operations are specified"""
        pyspark_example_dir = RESOURCES_DIR + "/snowpark-submit-pyspark-example"

        test_args = [
            "snowpark-submit",
            "--snowflake-connection-name",
            DEFAULT_TEST_CONNECTION_NAME,
            "--workload-status",
            "--kill-workload",
            pyspark_example_dir + "/main.py",
        ]

        with argv_context(test_args):
            result = runner_wrapper(test_mode=True)
            assert result.exit_code == 1
            assert "You must specify exactly one operation at a time" in result.error

    def test_end_workload_missing_workload_name(self):  # UNIT TEST
        """Test that end_workload fails when workload name is not provided"""
        test_args = [
            "snowpark-submit",
            "--snowflake-connection-name",
            DEFAULT_TEST_CONNECTION_NAME,
            "--kill-workload",
        ]

        with argv_context(test_args):
            result = runner_wrapper(test_mode=True)
            assert result.exit_code == 1
            assert "Missing mandatory option --snowflake-workload-name" in result.error

    def test_end_workload_success(self):  # INTEGRATION TEST
        """Test complete workload lifecycle: create -> check -> kill -> verify"""

        workload_name = generate_random_name(
            prefix="snowpark_submit_lifecycle_test_"
        ).upper()

        pyspark_example_dir = RESOURCES_DIR + "/snowpark-submit-pyspark-example"

        try:
            # Step 1: Create/submit a workload
            create_args = [
                "snowpark-submit",
                "--snowflake-connection-name",
                DEFAULT_TEST_CONNECTION_NAME,
                "--snowflake-workload-name",
                workload_name,
                pyspark_example_dir + "/main.py",
                "dummy_table",
            ]

            with argv_context(create_args):
                create_result = runner_wrapper(test_mode=True)
                assert (
                    create_result.exit_code == 0
                ), f"Failed to create workload: {create_result.error}"

            # Step 2: Check if workload exists
            status_args = [
                "snowpark-submit",
                "--snowflake-connection-name",
                DEFAULT_TEST_CONNECTION_NAME,
                "--workload-status",
                "--snowflake-workload-name",
                workload_name,
            ]

            with argv_context(status_args):
                status_result = runner_wrapper(test_mode=True)
                assert (
                    status_result.exit_code == 0
                ), f"Failed to get workload status: {status_result.error}"
                assert status_result.workload_name == workload_name
                assert (
                    status_result.service_status is not None
                )  # Should have some status

            # Step 3: Kill the workload
            kill_args = [
                "snowpark-submit",
                "--snowflake-connection-name",
                DEFAULT_TEST_CONNECTION_NAME,
                "--kill-workload",
                "--snowflake-workload-name",
                workload_name,
            ]

            with argv_context(kill_args):
                kill_result = runner_wrapper(test_mode=True)
                assert (
                    kill_result.exit_code == 0
                ), f"Failed to kill workload: {kill_result.error}"

            # Step 4: Verify workload is gone/terminated
            final_status_args = [
                "snowpark-submit",
                "--snowflake-connection-name",
                DEFAULT_TEST_CONNECTION_NAME,
                "--workload-status",
                "--snowflake-workload-name",
                workload_name,
            ]

            with argv_context(final_status_args):
                final_result = runner_wrapper(test_mode=True)
                # Should either fail (service doesn't exist) or show terminated status
                if final_result.exit_code == 0:
                    # If it still exists, it should be in a terminated state
                    assert (
                        final_result.terminated is True
                    ), f"Workload should be terminated but status is: {final_result.service_status}"
                else:
                    # Or it could be completely gone, which is also acceptable
                    assert "does not exist" in final_result.error

        except Exception as e:
            # Cleanup: Try to drop the service if test fails
            try:
                cleanup_args = [
                    "snowpark-submit",
                    "--snowflake-connection-name",
                    DEFAULT_TEST_CONNECTION_NAME,
                    "--kill-workload",
                    "--snowflake-workload-name",
                    workload_name,
                ]
                with argv_context(cleanup_args):
                    runner_wrapper(test_mode=True)
            except Exception:
                pass  # Ignore cleanup failures
            raise e

    @pytest.mark.parametrize("sas_version", SAS_VERSIONS)
    def test_snowpark_connect_version_param_python(
        self,
        spcs_snowflake_config,
        spcs_snowpark_session,
        skip_tests_out_of_aws_us_west_2,
        pyspark_utils_zip,
        sas_version,
    ):
        with sas_version_set_via_env_vars("invalid"):

            pyspark_example_dir = RESOURCES_DIR + "/snowpark-submit-pyspark-example"
            workload_name = generate_random_name(
                prefix="snowpark_submit_version_test_"
            ).upper()
            table_name = "snowpark_submit_version_test_table"

            spcs_snowpark_session.sql(
                f"create or replace table {table_name} (id int, val float)"
            ).collect()

            test_args = [
                "snowpark-submit",
                "--py-files",
                str(pyspark_utils_zip.resolve()),
                "--wait-for-completion",
                "--snowflake-workload-name",
                workload_name,
                "--snowpark-connect-version",
                sas_version,
                pyspark_example_dir + "/main.py",
                table_name,
            ]

            self._snowpark_submit_cluster_mode_helper(
                test_args + spcs_snowflake_config,
                spcs_snowpark_session,
                workload_name,
                table_name,
                [Row(ID=1, VAL=2.0), Row(ID=2, VAL=3.0), Row(ID=4, VAL=5.0)],
            )

            spcs_snowpark_session.sql(f"drop table if exists {table_name}").collect()

    @pytest.mark.parametrize("sas_version", SAS_VERSIONS)
    def test_snowpark_connect_version_param_scala(
        self,
        spcs_snowflake_config,
        spcs_snowpark_session,
        spcs_scala_test_table,
        skip_tests_out_of_aws_us_west_2,
        sas_version,
    ):
        with sas_version_set_via_env_vars("invalid"):

            scala_example_dir = RESOURCES_DIR + "/snowpark-submit-scala-example"
            workload_name = generate_random_name(
                prefix="snowpark_submit_scala_spcs_test_"
            ).upper()

            test_args = [
                "snowpark-submit",
                "--class",
                "com.example.SnowparkConnectApp",
                "--snowflake-workload-name",
                workload_name,
                "--snowpark-connect-version",
                sas_version,
                scala_example_dir + "/target/original-scala-maven-example-0.1.0.jar",
                spcs_scala_test_table,
            ]
            self._snowpark_submit_cluster_mode_helper(
                test_args + spcs_snowflake_config,
                spcs_snowpark_session,
                workload_name,
                spcs_scala_test_table,
                [
                    Row(NAME="Alice", AGE=29),
                    Row(NAME="Bob", AGE=31),
                    Row(NAME="Catherine", AGE=25),
                ],
            )
