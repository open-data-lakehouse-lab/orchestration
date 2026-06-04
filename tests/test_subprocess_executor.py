from unittest.mock import MagicMock, patch
from odl_orchestration.executors.subprocess_executor import SubprocessExecutor

def test_run_command_success():
    executor = SubprocessExecutor()
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "success"
    mock_result.stderr = ""
    
    with patch("subprocess.run", return_value=mock_result):
        result = executor.run_command("test", ["ls"])
        
        assert result.step_name == "test"
        assert result.status == "SUCCESS"
        assert result.return_code == 0
        assert result.stdout == "success"

def test_run_command_failure():
    executor = SubprocessExecutor()
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "error"
    
    with patch("subprocess.run", return_value=mock_result):
        result = executor.run_command("test", ["false"])
        
        assert result.step_name == "test"
        assert result.status == "FAILED"
        assert result.return_code == 1
        assert result.stderr == "error"

def test_run_command_exception():
    executor = SubprocessExecutor()
    
    with patch("subprocess.run", side_effect=Exception("Unexpected error")):
        result = executor.run_command("test", ["nonexistent"])
        
        assert result.step_name == "test"
        assert result.status == "FAILED"
        assert result.return_code == -1
        assert "Unexpected error" in result.stderr
