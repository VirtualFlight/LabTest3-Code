import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def client():
    # Create a fake redis_client module
    fake_redis = MagicMock()

    with patch("receipt_service.create_redis_client", return_value=fake_redis):
        # TODO: Complete se tting up the client
        # Get the testing app for the receipt_service
        from receipt_service import app
        
        app.config["TESTING"] = True
        yield app.test_client()

# Test that a receipt was submitted successfully to the database.
def test_receipt_success(client):
    from receipt_service import create_redis_client
    r = create_redis_client()

    # TODO: Complete the test
    payload = {"products": ["testing"], "receipt_id": "42"}
    response = client.post("/api/receipt", json=payload)

    assert response.status_code == 200
    assert response.json == {"status": "ok"} 

    r.hset.assert_called_once_with("receipt:42", "products", '["testing"]')

# Test writing a receipt when there are no products in the receipt.
# The service should return error 500
def test_receipt_missing_fields(client):
    response = client.post("/api/receipt", json={"receipt_id": "2"})
    assert response.status_code == 500