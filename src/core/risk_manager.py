import logging

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, max_drawdown_pct: float = 0.08):
        self.max_drawdown_pct = max_drawdown_pct
        self.peak_equity = 0.0
        self.kill_switch_engaged = False

    def update_equity(self, current_equity: float):
        if self.kill_switch_engaged:
            return

        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
            logger.info(f"New portfolio peak equity recorded: ${self.peak_equity:.2f}")
            
        if self.peak_equity > 0:
            current_drawdown = (self.peak_equity - current_equity) / self.peak_equity
            if current_drawdown >= self.max_drawdown_pct:
                self._engage_kill_switch(current_drawdown)

    def _engage_kill_switch(self, current_drawdown: float):
        self.kill_switch_engaged = True
        logger.critical(
            f"🚨 RISK CIRCUIT BREAKER BREACHED! Current drawdown is {current_drawdown * 100:.2f}%. "
            f"Max allowed is {self.max_drawdown_pct * 100:.2f}%. Halting trading immediately."
        )

    def allow_trade(self) -> bool:
        return not self.kill_switch_engaged