from dataclasses import dataclass

@dataclass
class Account:
    initial_capital: float
    
    cash_balance: float = 0.0
    blocked_margin: float = 0.0
    realized_pnl: float = 0.0
    
    def __post_init__(self):
        self.cash_balance = self.initial_capital
        
    @property #is computed when accessed, isnt stored in memory, doesnt require sync and constant updates in every function
    def equity(self) -> float:
        return self.cash_balance + self.blocked_margin
    
    @property #
    def available_margin(self) -> float:
        return self.cash_balance
    
    def apply_realized_pnl(self, pnl:float):
        self.realized_pnl += pnl
        self.cash_balance += pnl
        
    def block_margin(self,amount: float):
        if amount > self.cash_balance:
            raise ValueError("Insufficient funds to block margin")
        
        self.cash_balance -= amount
        self.blocked_margin += amount
        
    def release_margin(self, amount:float):
        if amount > self.block_margin:
            raise ValueError("Cannot release more margin than blocked")
        
        self.blocked_margin -= amount
        self.cash_balance += amount
        
        