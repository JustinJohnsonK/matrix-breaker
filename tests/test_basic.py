import pytest
from main import create_app

def test_ping():
    app = create_app()
    client = app.test_client()
    resp = client.get('/ping')
    assert resp.status_code == 200
    assert resp.json == {"ping": "pong"}
