"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
import pytest
import logging
import json
# from pathlib import Path
from market import app, db
from market.model import Agents

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("market-test")

xfail = pytest.mark.xfail


@pytest.fixture(scope="class", autouse=True)
def client(request):
    """Create and configure a new app instance for each test."""
    # TODO: use seperate db
    db.drop_all()
    db.create_all()
    # app.config.from_pyfile(Path(__file__).parent / "test.cfg")
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
            agent_id="test_agent",
        )
        # Delete test_agent
        Agents.query.filter_by(name=data["agent_id"]).delete()
        rv = client.post("/api/reset",
                         content_type="application/json",
                         data=json.dumps(data))
        assert rv.status_code == 200
        assert all([a == b for a, b in zip(json_of_response(rv).keys(),
                                           ["state"])])

    def test_step(self, client):
        data = dict(agent_id="test_agent",
                    decision="buy",
                    ticker=1,
                    trad_price=10.2,
                    trad_qty=2
                    )
        rv = client.post("/api/step",
                         content_type="application/json",
                         data=json.dumps(data))
        assert rv.status_code == 200
        assert all([a == b for a, b in zip(json_of_response(rv).keys(),
                                           ["done", "info", "next_state", "reward"])])
