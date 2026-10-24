import json
from io import BytesIO
from unittest.mock import Mock, patch
from urllib.error import HTTPError

import pytest

from meteoandalucia.api.aemet import AemetClient
from meteoandalucia.api.http import APIError, JSONClient
from meteoandalucia.api.riaweb import RiawebClient


def test_aemet_two_requests_and_token_isolation():
    http = Mock()
    http.get.side_effect = [
        {"estado": 200, "datos": "https://example.com/data"},
        [{"indicativo": "002", "provincia": "Z"}, {"indicativo": "001", "provincia": "A"}],
    ]
    rows = AemetClient("secret", http=http).stations()
    assert rows[0]["indicativo"] == "001"
    assert http.get.call_args_list[0].args[1]["api_key"] == "secret"
    assert http.get.call_args_list[1].args == ("https://example.com/data",)


@pytest.mark.parametrize("envelope", [{"estado": 429}, {"estado": 200}, [], None])
def test_aemet_envelope_errors(envelope):
    http = Mock()
    http.get.return_value = envelope
    with pytest.raises(APIError):
        AemetClient("token", http=http).stations()


@pytest.mark.parametrize("encoding", ["utf-8", "iso-8859-1"])
def test_http_encoding(encoding):
    body = json.dumps({"nombre": "CÓRDOBA, MÁLAGA, PEÑA"}, ensure_ascii=False).encode(encoding)
    with patch("meteoandalucia.api.http.urlopen", return_value=BytesIO(body)):
        assert JSONClient().get("https://example.com")["nombre"] == "CÓRDOBA, MÁLAGA, PEÑA"


def test_http_errors():
    with patch("meteoandalucia.api.http.urlopen", return_value=BytesIO(b"bad json")):
        with pytest.raises(APIError, match="JSON"):
            JSONClient().get("https://example.com")
    with patch(
        "meteoandalucia.api.http.urlopen",
        side_effect=HTTPError("https://example.com", 401, "unauthorized", {}, None),
    ):
        with pytest.raises(APIError, match="401"):
            JSONClient().get("https://example.com")
    with pytest.raises(APIError):
        JSONClient().get("file:///secret")


def test_riaweb_single_range_and_et0():
    http = Mock()
    client = RiawebClient(http=http)
    http.get.return_value = {"fecha": "2023-01-01"}
    client.measurement(4, 41, "2023-01-01", False)
    assert http.get.call_args.args[0].endswith("/4/41/2023-01-01/false")
    http.get.return_value = []
    client.measurements(4, 41, "2023-01-01", "2023-01-02", True)
    assert http.get.call_args.args[0].endswith("/4/41/2023-01-01/2023-01-02/true")
    with pytest.raises(ValueError):
        client.measurements(4, 41, "2023-02-01", "2023-01-01")


def test_aemet_date_url():
    http = Mock()
    http.get.side_effect = [{"estado": 200, "datos": "https://example.com/data"}, []]
    AemetClient("token", http=http).measurements("0010", "2023-01-01", "2023-01-02")
    assert "2023-01-01T00%3A00%3A00UTC" in http.get.call_args_list[0].args[0]
