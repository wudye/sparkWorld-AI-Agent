import pytest

class TestAppHandler:
    @pytest.mark.parametrize("query", [None, "hello world"])
    def test_response(self, query, client):
        r = client.post("/api/test", json={"query": query})
        assert r.status_code == 404
        data = r.json()
        if query is None:
            assert data["code"] == 404
            #assert data["msg"] == "bad request"
        else:
            assert data["code"] == 404
            #assert data["msg"] == "success"
            #assert data["data"] == query