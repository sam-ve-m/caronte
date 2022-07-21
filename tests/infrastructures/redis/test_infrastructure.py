import aioredis
from unittest.mock import patch
from decouple import Config, RepositoryEnv


with patch.object(RepositoryEnv, "__init__", return_value=None):
    with patch.object(Config, "__init__", return_value=None):
        from caronte.src.infrastructures.redis.infrastructure import RedisInfrastructure

dummy_connection = "dummy connection"


@patch.object(Config, "__call__")
@patch.object(aioredis, "from_url", return_value=dummy_connection)
def test_get_redis(mock_s3_connection, mocked_env):
    new_connection_created = RedisInfrastructure.get_redis()
    assert new_connection_created == dummy_connection
    mock_s3_connection.assert_called_once()

    reused_client = RedisInfrastructure.get_redis()
    assert reused_client == new_connection_created
    mock_s3_connection.assert_called_once()
    RedisInfrastructure.client = None
