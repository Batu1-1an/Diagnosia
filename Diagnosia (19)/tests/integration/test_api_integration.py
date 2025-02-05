import pytest
from unittest.mock import MagicMock

def test_database_connection(mock_database):
    """
    Test ID: TC005
    Test Type: Integration
    Test Case Category: API Integration
    Description: Test database connection and data retrieval
    """
    # Setup test data
    test_query = {"patient_id": "12345"}
    expected_data = {
        "name": "John Doe",
        "age": 30,
        "medical_history": ["Asthma", "Allergies"]
    }
    
    # Configure mock
    mock_database.query.return_value = expected_data
    
    # Execute query
    result = mock_database.query(test_query)
    
    # Verify results
    assert result == expected_data
    mock_database.query.assert_called_once_with(test_query)

def test_google_gemini_integration(mock_api_client):
    """
    Test ID: TC006
    Test Type: Integration
    Test Case Category: API Integration
    Description: Test Google Gemini AI integration
    """
    # Setup test data
    test_prompt = "Analyze symptoms: fever, cough, fatigue"
    expected_response = {
        "analysis": "Possible COVID-19 symptoms",
        "confidence": 0.85,
        "recommendations": ["Get tested", "Self-isolate"]
    }
    
    # Configure mock
    mock_api_client.gemini_analyze.return_value = expected_response
    
    # Execute API call
    result = mock_api_client.gemini_analyze(test_prompt)
    
    # Verify results
    assert result == expected_response
    assert "analysis" in result
    assert "confidence" in result
    assert "recommendations" in result
    mock_api_client.gemini_analyze.assert_called_once_with(test_prompt)

def test_api_error_handling(mock_api_client):
    """
    Additional test for API error handling
    """
    # Configure mock to simulate API error
    mock_api_client.gemini_analyze.side_effect = Exception("API Connection Error")
    
    # Test error handling
    with pytest.raises(Exception) as exc_info:
        mock_api_client.gemini_analyze("test prompt")
    
    assert str(exc_info.value) == "API Connection Error" 