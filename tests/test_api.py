"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
import pytest
import logging
import json
from pathlib import Path
from market import create_app


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("market-test")

xfail = pytest.mark.xfail


@pytest.fixture(scope="class", autouse=True)
def client(request):
    """Create and configure a new app instance for each test."""
    app = create_app({"TESTING": True})

    app.config.from_pyfile(Path(__file__).parent / "test.cfg")
    log.debug("setup: create test client")
    return app.test_client()


def json_of_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode("utf8"))


def check_response_format(response):
    json_response = json_of_response(response)
    # assert response format
    assert "result" in json_response.keys()


@pytest.mark.market
class Test_env():
    """Data test suite
    """

    def test_register(self, client):
        data = dict(
            name="agent1",
            cash=100000,
            asset_qty=0.0,
            asset_val=0.0,
            invested=False,  # ?
            bah_base=0
        )
        rv = client.post("/api/reset",
                         content_type="application/json",
                         data=json.dumps(data))
        assert rv.status_code == 200
        assert all([a == b for a, b in zip(json_of_response(rv).keys(),
                                           ["state"])])

    def test_step(self, client):
        agent = dict(
            name="agent1",
            cash=100000,
            asset_qty=0.0,
            asset_val=0.0,
            invested=False,  # ?
            bah_base=0
        )
        data = dict(agent=agent,
                    decision="buy",
                    price=10.2,
                    qty=2
                    )
        rv = client.post("/api/step",
                         content_type="application/json",
                         data=json.dumps(data))
        assert rv.status_code == 200
        assert all([a == b for a, b in zip(json_of_response(rv).keys(),
                                           ["done", "info", "new_state", "reward"])])
