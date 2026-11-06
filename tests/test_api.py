from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "up"}


def test_constituents_sorted_by_symbol(client: TestClient) -> None:
    response = client.get("/constituents")
    assert response.status_code == 200
    assert [s["symbol"] for s in response.json()] == ["INFY.NS", "TCS.NS"]


def test_prices_for_symbol(client: TestClient) -> None:
    response = client.get("/prices/TCS.NS")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["trade_date"] == "2026-10-01"
    assert data[0]["close"] == 100.0


def test_prices_symbol_is_case_insensitive(client: TestClient) -> None:
    assert client.get("/prices/tcs.ns").status_code == 200


def test_prices_date_range(client: TestClient) -> None:
    response = client.get("/prices/TCS.NS", params={"from": "2026-10-02", "to": "2026-10-02"})
    assert response.status_code == 200
    assert [p["trade_date"] for p in response.json()] == ["2026-10-02"]


def test_prices_unknown_symbol_returns_404(client: TestClient) -> None:
    response = client.get("/prices/FAKE")
    assert response.status_code == 404


def test_prices_reversed_range_returns_400(client: TestClient) -> None:
    response = client.get("/prices/TCS.NS", params={"from": "2026-10-03", "to": "2026-10-01"})
    assert response.status_code == 400


def test_index_latest(client: TestClient) -> None:
    response = client.get("/index/latest")
    assert response.status_code == 200
    assert response.json()["index_date"] == "2026-10-03"
    assert response.json()["level"] == 1102.5


def test_index_history_returns_all_levels_in_order(client: TestClient) -> None:
    response = client.get("/index/history")
    assert response.status_code == 200
    levels = [row["level"] for row in response.json()]
    assert levels == [1000.0, 1050.0, 1102.5]


def test_index_history_date_range(client: TestClient) -> None:
    response = client.get("/index/history", params={"from": "2026-10-02", "to": "2026-10-03"})
    assert [row["index_date"] for row in response.json()] == ["2026-10-02", "2026-10-03"]


def test_index_history_reversed_range_returns_400(client: TestClient) -> None:
    response = client.get("/index/history", params={"from": "2026-10-03", "to": "2026-10-01"})
    assert response.status_code == 400
