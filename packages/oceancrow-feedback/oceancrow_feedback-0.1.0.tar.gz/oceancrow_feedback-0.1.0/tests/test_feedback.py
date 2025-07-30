import json
import os
import pytest
from oceancrow_feedback.src.feedback import update_feedback

@pytest.fixture
def temp_feedback_file(tmp_path):
    """Create a temporary JSON file for testing."""
    file = tmp_path / "feedback.json"
    data = [
        {"id": 1, "text": "Test feedback", "status": "new"},
        {"id": 2, "text": "Another feedback", "status": "new"}
    ]
    with open(file, "w") as f:
        json.dump(data, f, indent=2)
    return str(file)

def test_update_feedback(temp_feedback_file):
    """Test updating an existing feedback ID."""
    update_feedback([temp_feedback_file], 1, "Thank you!")
    with open(temp_feedback_file, "r") as f:
        data = json.load(f)
    assert data[0]["id"] == 1
    assert data[0]["reply"] == "Thank you!"
    assert data[0]["status"] == "replied"
    assert data[1]["id"] == 2
    assert "reply" not in data[1]
    assert data[1]["status"] == "new"