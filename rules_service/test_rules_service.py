import pytest
from unittest.mock import MagicMock, patch
import json
import pandas as pd

@pytest.fixture
def client():
    # Fake redis_client module
    fake_redis = MagicMock()
    import sys
    sys.modules.pop("rules_service", None)

    with patch("rules_service.create_redis_client", return_value=fake_redis):
        # TODO: Complete setting up the client
        # Get the testing app for the rules_service
        from rules_service import app
        app.config["TESTING"] = True
        yield app.test_client()


# Test the successful calculation of rules
def test_rules_success(client):
    # Import the mocked redis client
    from rules_service import create_redis_client
    r = create_redis_client()

    # TODO: Prepare fake Redis receipts
    r.hset("fake-receipt:123", "products", json.dumps(["apple"]))

    fake_frequent = pd.DataFrame({
        'support': [0.5],
        'itemsets': [frozenset(['apple'])]
    })
    
    fake_rules = pd.DataFrame({
        'antecedents': [frozenset(['apple'])],
        'consequents': [frozenset()],
        'support': [0.5],
        'confidence': [1.0],
        'lift': [1.0]
    })

    # Use the following to mock apriori + association_rules
    # We do not need to test the algorithm as it is not always deterministic
    with patch("rules_service.apriori") as mock_apriori, \
         patch("rules_service.association_rules") as mock_rules:
        
        # TODO: Complete the test
        mock_apriori.return_value = fake_frequent
        mock_rules.return_value = fake_rules
        
        response = client.get("/api/rules")
        
        assert response.status_code == 200
        assert "antecedents" in response.json[0]  
        assert "confidence" in response.json[0]
        
        mock_apriori.assert_called_once()
        mock_rules.assert_called_once()
        r.hset.assert_called()        


# Test the attempt to determine rules without receipts in the database
# The service should still return HTTP:200, but an empty response
def test_rules_no_receipts(client):
    from rules_service import create_redis_client
    r = create_redis_client()

    # TODO: Redis returns no receipts
    r.hgetall.return_value = {}

    empty_frequent = pd.DataFrame(columns=['support', 'itemsets'])
    empty_rules = pd.DataFrame(columns=['antecedents', 'consequents', 'support', 'confidence', 'lift'])

    # Use the following to mock apriori + association_rules
    # We do not need to test the algorithm as it is not always deterministic
    with patch("rules_service.apriori") as mock_apriori, \
         patch("rules_service.association_rules") as mock_rules:
        
        #TODO: Complete the test
        mock_apriori.return_value = empty_frequent
        mock_rules.return_value = empty_rules
        
        response = client.get("/api/rules")
        
        assert response.status_code == 200
        assert response.json == []  
        
        mock_apriori.assert_called_once()
        mock_rules.assert_called_once()
