import pytest
from unittest.mock import patch, MagicMock
import clickup_importer

@pytest.fixture
def mock_task_data():
    return {
        "name": "Implement Auth",
        "description": "Using JWT",
        "priority": 2
    }

@patch('clickup_importer.requests.get')
def test_get_id_by_name_success(mock_get):
    # Simulate API returning a list of spaces
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "spaces": [{"id": "123", "name": "Engineering"}]
    }
    
    res = clickup_importer.get_id_by_name("fake_url", "spaces", "Engineering")
    assert res == "123"

@patch('clickup_importer.requests.post')
def test_create_task_api_call(mock_post, mock_task_data):
    # Simulate successful task creation
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"id": "task_abc"}
    
    task_id = clickup_importer.create_task("list_xyz", mock_task_data)
    
    assert task_id == "task_abc"
    # Verify the payload sent to ClickUp
    args, kwargs = mock_post.call_args
    assert kwargs['json']['name'] == "Implement Auth"
    assert kwargs['json']['description'] == "Using JWT"

@patch('clickup_importer.get_sprint_list_id')
@patch('clickup_importer.create_task')
def test_main_loop_logic(mock_create, mock_get_id):
    """Tests that main() correctly loops through tasks and subtasks."""
    mock_get_id.return_value = "list_1"
    mock_create.return_value = "parent_1"
    
    # Mock the JSON file reading
    mock_data = {
        "space": "S", "folder": "F", "list": "L",
        "tasks": [
            {"name": "T1", "subtasks": [{"name": "ST1"}]}
        ]
    }
    
    with patch("builtins.open", MagicMock()):
        with patch("json.load", return_value=mock_data):
            clickup_importer.main()
    
    # Check that create_task was called twice (1 task + 1 subtask)
    assert mock_create.call_count == 2