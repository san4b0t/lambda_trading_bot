import pytest
from unittest.mock import AsyncMock
from src.adapters.lob_wrapper import LocalLobEngine

@pytest.fixture
def mock_subprocess(mocker):
    mock_proc = AsyncMock()
    mock_proc.stdin.write = mocker.MagicMock()
    mock_proc.stdin.drain = AsyncMock()
    mock_proc.returncode = None
    
    mocker.patch("asyncio.create_subprocess_exec", return_value=mock_proc)
    return mock_proc

async def test_lob_wrapper_pushes_tick(mock_subprocess):
    lob = LocalLobEngine()
    await lob.start()
    
    await lob.push_tick(price=45000.0, qty=1.5, side="buy")
    
    # Verify the JSON payload was correctly formatted and sent to stdin
    mock_subprocess.stdin.write.assert_called_once()
    call_arg = mock_subprocess.stdin.write.call_args[0][0].decode()
    assert '"action": "add"' in call_arg
    assert '"price": 45000.0' in call_arg