# Mining and Consensus Tools
# MIT Course Chapter 4 - Proof of Work, Mining Economics, Difficulty

from .pow_simulator import mine_block, estimate_mining_time
from .mining_calc import calculate_mining_profit, get_breakeven_price
from .difficulty import predict_difficulty_adjustment, get_current_difficulty
from .fork_monitor import get_confirmation_safety, check_recent_reorgs
from .inflation import get_inflation_stats, get_halving_countdown

__all__ = [
    'mine_block', 'estimate_mining_time',
    'calculate_mining_profit', 'get_breakeven_price',
    'predict_difficulty_adjustment', 'get_current_difficulty',
    'get_confirmation_safety', 'check_recent_reorgs',
    'get_inflation_stats', 'get_halving_countdown'
]
