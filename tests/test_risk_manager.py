from src.core.risk_manager import RiskManager

def test_risk_manager_updates_peak_equity():
    risk = RiskManager(max_drawdown_pct=0.08)
    risk.update_equity(10000.0)
    assert risk.peak_equity == 10000.0
    risk.update_equity(10500.0)
    assert risk.peak_equity == 10500.0

def test_risk_manager_triggers_kill_switch():
    risk = RiskManager(max_drawdown_pct=0.08) # 8% drawdown
    risk.update_equity(10000.0) # Peak is now 10000
    assert risk.allow_trade() is True
    
    # Drop to 9300 (7% drawdown - should be fine)
    risk.update_equity(9300.0)
    assert risk.allow_trade() is True

    # Drop to 9100 (9% drawdown - KILL SWITCH)
    risk.update_equity(9100.0)
    assert risk.allow_trade() is False

    # Equity recovers, but kill switch should remain permanently locked
    risk.update_equity(12000.0)
    assert risk.allow_trade() is False