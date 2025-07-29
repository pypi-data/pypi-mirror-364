import json
from unittest.mock import Mock, patch

import httpx
import pytest

from pncp.utils import get_many, get_one


@pytest.fixture
def mock_response():
    def _mock_response(
        status_code=200,
        json_data=None,
        text_data=None,
        raise_http_error=False,
        raise_json_error=False,
    ):
        mock = Mock()
        mock.status_code = status_code
        mock.raise_for_status.side_effect = (
            httpx.HTTPStatusError("Error", request=Mock(), response=mock)
            if raise_http_error
            else None
        )
        if raise_json_error:
            mock.json.side_effect = json.JSONDecodeError("Malformed", text_data, 0)
        elif json_data is not None:
            mock.json.return_value = json_data
        else:
            mock.json.return_value = []

        return mock

    return _mock_response


def test_get_many_success_no_params(mock_response):
    with patch("httpx.Client") as mock_client:
        mock_get = mock_client.return_value.__enter__.return_value.get
        mock_get.return_value = mock_response(json_data=[{"id": 1}, {"id": 2}])

        result = get_many("http://test")

        assert result == [{"id": 1}, {"id": 2}]
        mock_client.assert_called_once_with(timeout=10)
        mock_get.assert_called_once_with("http://test", params=None)


def test_get_many_success_with_params(mock_response):
    with patch("httpx.Client") as mock_client:
        mock_get = mock_client.return_value.__enter__.return_value.get
        mock_get.return_value = mock_response(json_data=[{"id": 2}])

        result = get_many("http://test", params={"id": 2})

        assert result == [{"id": 2}]
        mock_get.assert_called_once_with("http://test", params={"id": 2})


def test_get_many_empty_list(mock_response):
    with patch("httpx.Client") as mock_client:
        mock_get = mock_client.return_value.__enter__.return_value.get
        mock_get.return_value = mock_response(json_data=[])

        result = get_many("http://test")

        assert result == []


def test_get_many_http_error(mock_response):
    with patch("httpx.Client") as mock_client:
        mock_get = mock_client.return_value.__enter__.return_value.get
        mock_get.return_value = mock_response(status_code=404, raise_http_error=True)

        with pytest.raises(httpx.HTTPStatusError):
            get_many("http://test")


def test_get_many_timeout():
    with patch("httpx.Client") as mock_client:
        mock_get = mock_client.return_value.__enter__.return_value.get
        mock_get.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(httpx.TimeoutException):
            get_many("http://test")


def test_get_many_malformed_json(mock_response):
    with patch("httpx.Client") as mock_client:
        mock_get = mock_client.return_value.__enter__.return_value.get
        mock_get.return_value = mock_response(text_data="notjson", raise_json_error=True)

        with pytest.raises(json.JSONDecodeError):
            get_many("http://test")


def test_get_one_success_no_params(mock_response):
    with patch("httpx.Client") as mock_client:
        mock_get = mock_client.return_value.__enter__.return_value.get
        mock_get.return_value = mock_response(json_data={"id": 1})

        result = get_one("http://test")

        assert result == {"id": 1}
        mock_client.assert_called_once_with(timeout=10)
        mock_get.assert_called_once_with("http://test", params=None)


def test_get_one_success_with_params(mock_response):
    with patch("httpx.Client") as mock_client:
        mock_get = mock_client.return_value.__enter__.return_value.get
        mock_get.return_value = mock_response(json_data={"id": 2})

        result = get_one("http://test", params={"id": 2})

        assert result == {"id": 2}
        mock_get.assert_called_once_with("http://test", params={"id": 2})


def test_get_one_http_error(mock_response):
    with patch("httpx.Client") as mock_client:
        mock_get = mock_client.return_value.__enter__.return_value.get
        mock_get.return_value = mock_response(status_code=500, raise_http_error=True)

        with pytest.raises(httpx.HTTPStatusError):
            get_one("http://test")


def test_get_one_timeout():
    with patch("httpx.Client") as mock_client:
        mock_get = mock_client.return_value.__enter__.return_value.get
        mock_get.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(httpx.TimeoutException):
            get_one("http://test")


def test_get_one_malformed_json(mock_response):
    with patch("httpx.Client") as mock_client:
        mock_get = mock_client.return_value.__enter__.return_value.get
        mock_get.return_value = mock_response(text_data="notjson", raise_json_error=True)

        with pytest.raises(json.JSONDecodeError):
            get_one("http://test")
