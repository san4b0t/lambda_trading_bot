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
    
    mock_subprocess.stdin.write.assert_called_once()
    call_arg = mock_subprocess.stdin.write.call_args[0][0].decode()
    assert call_arg == "add 45000.0 1.5 buy\n"