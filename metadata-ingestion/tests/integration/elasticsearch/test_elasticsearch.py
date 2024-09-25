import subprocess

import pytest
from freezegun import freeze_time

from datahub.ingestion.api.source import SourceCapability
from datahub.ingestion.source.elastic_search import ElasticsearchSource
from tests.test_helpers import mce_helpers, test_connection_helpers
from tests.test_helpers.click_helpers import run_datahub_cmd
from tests.test_helpers.docker_helpers import wait_for_port

FROZEN_TIME = "2020-04-14 07:00:00"


@pytest.fixture(scope="module")
def test_resources_dir(pytestconfig):
    return pytestconfig.rootpath / "tests/integration/elasticsearch"


@pytest.fixture(scope="module")
def mock_elasticsearch_service(docker_compose_runner, test_resources_dir):
    with docker_compose_runner(
        test_resources_dir / "docker-compose.yml", "elasticsearch"
    ) as docker_services:
        wait_for_port(docker_services, "test_elasticsearch", 9200, timeout=120)

        # Set up topics and produce some data
        command = f"{test_resources_dir}/send_records.sh {test_resources_dir}"
        subprocess.run(command, shell=True, check=True)

        yield docker_compose_runner


@pytest.mark.parametrize(
    "config_dict, is_success",
    [
        (
            {
                "host": "localhost:9201",
            },
            False,
        ),
        (
            {
                "host": "localhost:9201",
                "username": "invalid",
                "password": "invalid",
            },
            False,
        ),
        (
            {
                "host": "localhost:9201",
                "username": "elastic",
                "password": "test_pass",
            },
            True,
        ),
        (
            {
                "host": "localhost:9201",
                "api_key": "invalid",
            },
            False,
        ),
    ],
)
@pytest.mark.integration
@freeze_time(FROZEN_TIME)
def test_elasticsearch_test_connection(
    mock_elasticsearch_service, config_dict, is_success
):
    report = test_connection_helpers.run_test_connection(
        ElasticsearchSource, config_dict
    )
    print(f"{report=}")
    if is_success:
        test_connection_helpers.assert_basic_connectivity_success(report)
        # test_connection_helpers.assert_capability_report(
        #     capability_report=report.capability_report,
        #     success_capabilities=[],  # SourceCapability.SCHEMA_METADATA
        # )
    else:
        test_connection_helpers.assert_basic_connectivity_failure(
            report, "Failed to get metadata"
        )
        # test_connection_helpers.assert_capability_report(
        #     capability_report=report.capability_report,
        #     failure_capabilities={
        #         # SourceCapability.SCHEMA_METADATA: "Failed to establish a new connection"
        #     },
        # )
