import pytest
from unittest.mock import patch, AsyncMock, MagicMock, call
from decouple import Config, RepositoryEnv
from aiohttp import ClientSession


with patch.object(RepositoryEnv, "__init__", return_value=None):
    with patch.object(Config, "__init__", return_value=None):
        with patch.object(Config, "__call__", return_value="ENV_VALUE{}"):
            from caronte import OuroInvestErrorReturn
            from caronte.src.transports.ouroinvest.transport import OuroInvestApiTransport


dummy_url = "url"
dummy_token = "token"
dummy_user_id = 15489
dummy_response = AsyncMock(raise_for_status=MagicMock())
dummy_env_value = "ENV_VALUE{}"
dummy_body = {"controle": True}
dummy_auth = {"Authorization": f"Bearer {dummy_token}"}
dummy_control = {"controle": {
    "dataHoraCliente": dummy_env_value,
    "recurso": {"codigo": dummy_env_value, "sigla": dummy_env_value},
    "origem": {"nome": dummy_env_value, "chave": dummy_env_value, "endereco": dummy_env_value}
}}


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_auth)
@patch.object(OuroInvestApiTransport, "_request_method_get", return_value=dummy_response)
async def test_execute_get_with_default_token(mocked_response, mocked_auth, mocked_token):
    response = await OuroInvestApiTransport.execute_get_with_default_token(dummy_url)
    assert response == dummy_response
    mocked_token.assert_called_once_with()
    mocked_auth.assert_called_once_with(dummy_token)
    mocked_response.assert_called_once_with(dummy_url, dummy_auth)


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_control", return_value=dummy_control)
@patch.object(OuroInvestApiTransport, "_get_user_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_auth)
@patch.object(OuroInvestApiTransport, "_request_method_get", return_value=dummy_response)
async def test_execute_get_with_user_token_with_body(mocked_response, mocked_auth, mocked_token, mocked_control):
    response = await OuroInvestApiTransport.execute_get_with_user_token(dummy_url, dummy_user_id, dummy_body)
    assert response == dummy_response
    mocked_control.assert_called_once_with()
    mocked_token.assert_called_once_with(dummy_user_id)
    mocked_auth.assert_called_once_with(dummy_token)
    mocked_response.assert_called_once_with(dummy_url, dummy_auth, dummy_control, dummy_user_id)


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_control", return_value=dummy_control)
@patch.object(OuroInvestApiTransport, "_get_user_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_auth)
@patch.object(OuroInvestApiTransport, "_request_method_get", return_value=dummy_response)
async def test_execute_get_with_user_token_without_body(mocked_response, mocked_auth, mocked_token, mocked_control):
    response = await OuroInvestApiTransport.execute_get_with_user_token(dummy_url, dummy_user_id)
    assert response == dummy_response
    mocked_control.assert_not_called()
    mocked_token.assert_called_once_with(dummy_user_id)
    mocked_auth.assert_called_once_with(dummy_token)
    mocked_response.assert_called_once_with(dummy_url, dummy_auth, None, dummy_user_id)


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_control", return_value=dummy_control)
@patch.object(OuroInvestApiTransport, "_get_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_auth)
@patch.object(OuroInvestApiTransport, "_request_method_post", return_value=dummy_response)
async def test_execute_post_with_default_token(mocked_response, mocked_auth, mocked_token, mocked_control):
    response = await OuroInvestApiTransport.execute_post_with_default_token(dummy_url, dummy_body)
    assert response == dummy_response
    mocked_control.assert_called_once_with()
    mocked_token.assert_called_once_with()
    mocked_auth.assert_called_once_with(dummy_token)
    mocked_response.assert_called_once_with(dummy_url, dummy_body, dummy_auth)


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_control", return_value=dummy_control)
@patch.object(OuroInvestApiTransport, "_get_user_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_auth)
@patch.object(OuroInvestApiTransport, "_request_method_post", return_value=dummy_response)
async def test_execute_post_with_user_token(mocked_response, mocked_auth, mocked_token, mocked_control):
    response = await OuroInvestApiTransport.execute_post_with_user_token(dummy_url, dummy_user_id, dummy_body)
    assert response == dummy_response
    mocked_control.assert_called_once_with()
    mocked_token.assert_called_once_with(dummy_user_id)
    mocked_auth.assert_called_once_with(dummy_token)
    mocked_response.assert_called_once_with(dummy_url, dummy_body, dummy_auth, dummy_user_id)


def test_get_control():
    response = OuroInvestApiTransport._get_control()
    assert dummy_control == response


def test__get_auth():
    response = OuroInvestApiTransport._get_auth(dummy_token)
    assert dummy_auth == response


fake_cache = AsyncMock()
stub_json = {"tokenAcesso": {"token": dummy_token}}


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_control", return_value=dummy_control)
@patch.object(OuroInvestApiTransport, "_request_method_post", return_value=dummy_response)
async def test_get_cached_token(mocked_request, mocked_control, monkeypatch):
    fake_cache.get.return_value = dummy_token
    monkeypatch.setattr(OuroInvestApiTransport, "cache", fake_cache)
    dummy_response.json.return_value = stub_json
    response = await OuroInvestApiTransport._get_token()
    fake_cache.get.assert_called_once_with(dummy_env_value*2)
    fake_cache.delete_folder.assert_not_called()
    fake_cache.set.assert_not_called()
    mocked_control.assert_not_called()
    mocked_request.assert_not_called()
    assert response == dummy_token


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_control", return_value=dummy_control)
@patch.object(OuroInvestApiTransport, "_request_method_post", return_value=dummy_response)
async def test_get_cached_user_token(mocked_request, mocked_control, mocked_token, mocked_headers, monkeypatch):
    fake_cache.get.return_value = dummy_token
    monkeypatch.setattr(OuroInvestApiTransport, "cache", fake_cache)
    monkeypatch.setattr(OuroInvestApiTransport, "_user_token_cache_key_format", dummy_env_value)
    dummy_response.json.return_value = stub_json
    response = await OuroInvestApiTransport._get_user_token(dummy_user_id)
    mocked_token.assert_called_once_with()
    fake_cache.get.assert_called_with(dummy_env_value.format(dummy_user_id))
    fake_cache.set.assert_not_called()
    fake_cache.delete_folder.assert_not_called()
    mocked_control.assert_not_called()
    mocked_headers.assert_not_called()
    mocked_request.assert_not_called()
    assert response == dummy_token


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_control", return_value=dummy_control)
@patch.object(OuroInvestApiTransport, "_request_method_post", return_value=dummy_response)
async def test_get_new_token(mocked_request, mocked_control, monkeypatch):
    fake_cache.get.return_value = None
    monkeypatch.setattr(OuroInvestApiTransport, "cache", fake_cache)
    dummy_response.json.return_value = stub_json
    response = await OuroInvestApiTransport._get_token()
    fake_cache.get.assert_called_with(dummy_env_value*2)
    fake_cache.set.assert_called_once_with(dummy_env_value*2, dummy_token, 12 * 60 * 60)
    fake_cache.delete_folder.assert_called_once_with(dummy_env_value)
    mocked_request.assert_called_once_with(dummy_env_value, body={
        "chave": dummy_env_value, "senha": dummy_env_value,
        **dummy_control
    })
    mocked_control.assert_called_once_with()
    assert response == dummy_token


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_control", return_value=dummy_control)
@patch.object(OuroInvestApiTransport, "_request_method_post", return_value=dummy_response)
async def test_get_new_user_token(mocked_request, mocked_control, mocked_token, mocked_headers, monkeypatch):
    fake_cache.get.return_value = None
    monkeypatch.setattr(OuroInvestApiTransport, "cache", fake_cache)
    monkeypatch.setattr(OuroInvestApiTransport, "_user_token_cache_key_format", dummy_env_value)
    dummy_response.json.return_value = stub_json
    response = await OuroInvestApiTransport._get_user_token(dummy_user_id)
    mocked_token.assert_called_once_with()
    cache_key = dummy_env_value.format(dummy_user_id)
    fake_cache.get.assert_called_with(cache_key)
    fake_cache.set.assert_called_with(cache_key, dummy_token, 12 * 60 * 60)
    mocked_request.assert_called_once_with(dummy_env_value, body={
        "codigoCliente": dummy_user_id, **dummy_control
    }, headers=dummy_token)
    mocked_headers.assert_called_once_with(dummy_token)
    mocked_control.assert_called_once_with()
    assert response == dummy_token


@pytest.mark.asyncio
@patch.object(ClientSession, "__init__", return_value=None)
async def test_get_session(mocked_client):
    new_connection_created = await OuroInvestApiTransport._get_session()
    assert isinstance(new_connection_created, ClientSession)
    mocked_client.assert_called_once()

    reused_client = await OuroInvestApiTransport._get_session()
    assert isinstance(reused_client, ClientSession)
    mocked_client.assert_called_once()
    OuroInvestApiTransport.client = None


fake_client = AsyncMock()


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_session", return_value=fake_client)
@patch.object(OuroInvestApiTransport, "_raise_for_status", return_value=fake_client)
async def test_request_method_get(mocked_raise, mocked_session, mocked_token, mocked_auth, monkeypatch):
    monkeypatch.setattr(OuroInvestApiTransport, "cache", fake_cache)
    monkeypatch.setattr(OuroInvestApiTransport, "MAX_RETRY", "2")
    _dummy_response = MagicMock(status=200)
    fake_client.get = AsyncMock(return_value=_dummy_response)
    response = await OuroInvestApiTransport._request_method_get(dummy_url, dummy_auth)
    mocked_session.assert_called_once_with()
    fake_client.get.assert_called_once_with(dummy_url, headers=dummy_auth, json=None)
    assert response == _dummy_response
    mocked_token.assert_not_called()
    mocked_auth.assert_not_called()
    mocked_raise.assert_called_once_with(_dummy_response)


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_session", return_value=fake_client)
@patch.object(OuroInvestApiTransport, "_raise_for_status", return_value=fake_client)
async def test_request_method_post(mocked_raise, mocked_session, mocked_token, mocked_auth, monkeypatch):
    monkeypatch.setattr(OuroInvestApiTransport, "cache", fake_cache)
    monkeypatch.setattr(OuroInvestApiTransport, "MAX_RETRY", "2")
    _dummy_response = MagicMock(status=200)
    fake_client.post = AsyncMock(return_value=_dummy_response)
    response = await OuroInvestApiTransport._request_method_post(dummy_url, dummy_body)
    mocked_session.assert_called_once_with()
    fake_client.post.assert_called_once_with(dummy_url, headers=None, json=dummy_body)
    assert response == _dummy_response
    mocked_token.assert_not_called()
    mocked_auth.assert_not_called()
    mocked_raise.assert_called_once_with(_dummy_response)


async def return_response(url, headers, json):
    dummy_response.status = 200 if headers == dummy_token else 403
    return dummy_response


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_session", return_value=fake_client)
@patch.object(OuroInvestApiTransport, "_get_user_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_raise_for_status", return_value=fake_client)
async def test_request_method_get_forbidden(mocked_raise, mocked_user_token, mocked_session, mocked_token,
                                            mocked_auth, monkeypatch):
    monkeypatch.setattr(OuroInvestApiTransport, "MAX_RETRY", "2")
    monkeypatch.setattr(OuroInvestApiTransport, "cache", fake_cache)
    _dummy_response = MagicMock(status=200)
    fake_client.get = AsyncMock(side_effect=[MagicMock(status=403), _dummy_response])
    response = await OuroInvestApiTransport._request_method_get(dummy_url, dummy_auth, dummy_body)
    mocked_session.assert_has_calls((call(), call()))
    assert response == _dummy_response
    mocked_user_token.assert_not_called()
    mocked_token.assert_called_once_with()
    mocked_auth.assert_called_once_with(dummy_token)
    mocked_raise.assert_called_once_with(_dummy_response)


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_session", return_value=fake_client)
@patch.object(OuroInvestApiTransport, "_get_user_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_raise_for_status", return_value=fake_client)
async def test_request_method_get_forbidden_user_token(mocked_raise, mocked_user_token, mocked_session, mocked_token,
                                                       mocked_auth, monkeypatch):
    monkeypatch.setattr(OuroInvestApiTransport, "MAX_RETRY", "2")
    monkeypatch.setattr(OuroInvestApiTransport, "cache", fake_cache)
    _dummy_response = MagicMock(status=200)
    fake_client.get = AsyncMock(side_effect=[MagicMock(status=403), _dummy_response])
    response = await OuroInvestApiTransport._request_method_get(dummy_url, dummy_auth, dummy_body, dummy_user_id)
    mocked_session.assert_has_calls((call(), call()))
    assert response == _dummy_response
    mocked_user_token.assert_called_once_with(dummy_user_id)
    mocked_token.assert_not_called()
    mocked_auth.assert_called_once_with(dummy_token)
    mocked_raise.assert_called_once_with(_dummy_response)


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_session", return_value=fake_client)
@patch.object(OuroInvestApiTransport, "_get_user_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_raise_for_status", return_value=fake_client)
async def test_request_method_post_forbidden(mocked_raise, mocked_user_token, mocked_session, mocked_token, mocked_auth, monkeypatch):
    monkeypatch.setattr(OuroInvestApiTransport, "cache", fake_cache)
    monkeypatch.setattr(OuroInvestApiTransport, "MAX_RETRY", "2")
    _dummy_response = MagicMock(status=200)
    fake_client.post = AsyncMock(side_effect=[MagicMock(status=403), _dummy_response])
    response = await OuroInvestApiTransport._request_method_post(dummy_url, dummy_auth, dummy_body)
    mocked_session.assert_has_calls((call(), call()))
    assert response == _dummy_response
    mocked_user_token.assert_not_called()
    mocked_token.assert_called_once_with()
    mocked_auth.assert_called_once_with(dummy_token)
    mocked_raise.assert_called_once_with(_dummy_response)


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_session", return_value=fake_client)
@patch.object(OuroInvestApiTransport, "_get_user_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_raise_for_status", return_value=fake_client)
async def test_request_method_post_forbidden_user_token(mocked_raise, mocked_user_token, mocked_session, mocked_token,
                                                        mocked_auth, monkeypatch):
    monkeypatch.setattr(OuroInvestApiTransport, "MAX_RETRY", "2")
    monkeypatch.setattr(OuroInvestApiTransport, "cache", fake_cache)
    _dummy_response = MagicMock(status=200)
    fake_client.post = AsyncMock(side_effect=[MagicMock(status=403), _dummy_response])
    response = await OuroInvestApiTransport._request_method_post(dummy_url, dummy_auth, dummy_body, dummy_user_id)
    mocked_session.assert_has_calls((call(), call()))
    assert response == _dummy_response
    mocked_user_token.assert_called_once_with(dummy_user_id)
    mocked_token.assert_not_called()
    mocked_auth.assert_called_once_with(dummy_token)
    mocked_raise.assert_called_once_with(_dummy_response)


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_session", return_value=fake_client)
@patch.object(OuroInvestApiTransport, "_get_user_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_raise_for_status", side_effect=OuroInvestErrorReturn())
async def test_request_method_post_max_retries(mocked_raise, mocked_user_token, mocked_session, mocked_token,
                                               mocked_auth, monkeypatch):
    monkeypatch.setattr(OuroInvestApiTransport, "cache", fake_cache)
    monkeypatch.setattr(OuroInvestApiTransport, "MAX_RETRY", "2")
    dummy_response.status = 403
    fake_client.post = AsyncMock(side_effect=[dummy_response]*3)
    with pytest.raises(OuroInvestErrorReturn):
        await OuroInvestApiTransport._request_method_post(dummy_url, dummy_auth, dummy_body)
    assert mocked_session.mock_calls.count(call()) == 3
    mocked_user_token.assert_not_called()
    assert mocked_token.mock_calls.count(call()) == 2
    assert mocked_auth.mock_calls.count(call(dummy_token)) == 2
    mocked_raise.assert_called_once_with(dummy_response)


@pytest.mark.asyncio
@patch.object(OuroInvestApiTransport, "_get_auth", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_get_session", return_value=fake_client)
@patch.object(OuroInvestApiTransport, "_get_user_token", return_value=dummy_token)
@patch.object(OuroInvestApiTransport, "_raise_for_status", side_effect=OuroInvestErrorReturn())
async def test_request_method_get_max_retries(mocked_raise, mocked_user_token, mocked_session, mocked_token,
                                              mocked_auth, monkeypatch):
    monkeypatch.setattr(OuroInvestApiTransport, "cache", fake_cache)
    monkeypatch.setattr(OuroInvestApiTransport, "MAX_RETRY", "2")
    dummy_response.status = 403
    fake_client.get = AsyncMock(side_effect=[dummy_response]*3)
    with pytest.raises(OuroInvestErrorReturn):
        await OuroInvestApiTransport._request_method_get(dummy_url, dummy_body, dummy_auth)
    assert mocked_session.mock_calls.count(call()) == 3
    mocked_user_token.assert_not_called()
    assert mocked_token.mock_calls.count(call()) == 2
    assert mocked_auth.mock_calls.count(call(dummy_token)) == 2
    mocked_raise.assert_called_once_with(dummy_response)


@pytest.mark.asyncio
async def test_raise_for_status():
    await OuroInvestApiTransport._raise_for_status(MagicMock(ok=True))


@pytest.mark.asyncio
async def test_raise_for_status_raising():
    stub_response = MagicMock(ok=False)
    stub_response.content.read = AsyncMock()
    stub_response.content.read.return_value.decode = MagicMock
    with pytest.raises(OuroInvestErrorReturn):
        await OuroInvestApiTransport._raise_for_status(stub_response)
