# Personal Fork Notes

```bash
build-tools?
sudo apt-get install python3.11-dev
sudo apt-get install openjdk-17-jdk
sudo apt-get install libldap2-dev libsasl2-dev

cd metadata-ingestion
../gradlew :metadata-ingestion:installDev
source venv/bin/activate
datahub version

pip install -e '.[elasticsearch]'
```

## Testing Original Code

```bash
pip install -e '.[dev]'
pytest -m 'not integration'  # All but 2 succeed
pytest -vv tests/unit/test_elasticsearch_source.py  # OK

pytest -m 'integration'  # Some source types fail. Stuck at test_hana. Elasticsearch no tests?
```

```bash
datahub ingest -c examples/recipes/elasticsearch_to_datahub.dhub.yaml
```

## Integration Testing Elasticsearch and New Feat

```bash
pytest -vv tests/integration/elasticsearch/test_elasticsearch.py::test_docker_fixture -s
```

## Debug ES Service

sudo lsof -i TCP | grep 9201
curl -GET localhost:9201/_cluster/health  # wait a bit

