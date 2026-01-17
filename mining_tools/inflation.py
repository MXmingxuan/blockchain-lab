"""
通胀率仪表盘 (Inflation Schedule Dashboard)
可视化比特币供应量和减半倒计时
"""
import requests
import time
from typing import Optional
from dataclasses import dataclass


# 比特币常量
TOTAL_SUPPLY = 21_000_000           # 总供应量
INITIAL_REWARD = 50                  # 初始区块奖励
HALVING_INTERVAL = 210_000          # 减半间隔（区块数）
TARGET_BLOCK_TIME = 600             # 目标出块时间（秒）


@dataclass
class HalvingEvent:
    """减半事件"""
    number: int
    block_height: int
    reward_before: float
    reward_after: float
    date: str
    circulating_after: float


# 历史减半事件
HALVING_HISTORY = [
    HalvingEvent(1, 210000, 50, 25, "2012-11-28", 10_500_000),
    HalvingEvent(2, 420000, 25, 12.5, "2016-07-09", 15_750_000),
    HalvingEvent(3, 630000, 12.5, 6.25, "2020-05-11", 18_375_000),
    HalvingEvent(4, 840000, 6.25, 3.125, "2024-04 (预计)", 19_687_500),
]


def get_current_block_height() -> int:
    """获取当前区块高度"""
    try:
        resp = requests.get(
            'https://blockchain.info/q/getblockcount',
            timeout=5
        )
        if resp.status_code == 200:
            return int(resp.text)
    except Exception:
        pass
    
    # 返回估算值
    return 825000


def get_circulating_supply(block_height: int) -> float:
    """
    计算给定区块高度的流通供应量
    """
    supply = 0
    reward = INITIAL_REWARD
    blocks_remaining = block_height
    
    while blocks_remaining > 0 and reward >= 0.00000001:
        blocks_in_era = min(blocks_remaining, HALVING_INTERVAL)
        supply += blocks_in_era * reward
        blocks_remaining -= blocks_in_era
        reward /= 2
    
    return supply


def get_current_reward(block_height: int) -> float:
    """获取当前区块奖励"""
    halvings = block_height // HALVING_INTERVAL
    return INITIAL_REWARD / (2 ** halvings)


def get_inflation_rate(block_height: int) -> float:
    """
    计算年化通胀率
    """
    current_supply = get_circulating_supply(block_height)
    current_reward = get_current_reward(block_height)
    
    # 每年新增供应量（假设每10分钟一个区块）
    blocks_per_year = 365.25 * 24 * 60 / 10  # 约52,560
    annual_new_supply = blocks_per_year * current_reward
    
    # 年化通胀率
    inflation_rate = (annual_new_supply / current_supply) * 100
    
    return inflation_rate


def get_halving_countdown(current_height: Optional[int] = None) -> dict:
    """
    获取减半倒计时信息
    """
    if current_height is None:
        current_height = get_current_block_height()
    
    # 计算当前处于第几个减半周期
    current_era = current_height // HALVING_INTERVAL
    next_halving_height = (current_era + 1) * HALVING_INTERVAL
    
    blocks_remaining = next_halving_height - current_height
    
    # 估算剩余时间
    seconds_remaining = blocks_remaining * TARGET_BLOCK_TIME
    days_remaining = seconds_remaining / 86400
    
    return {
        'current_height': current_height,
        'current_era': current_era + 1,  # 人类可读（从1开始）
        'next_halving_height': next_halving_height,
        'blocks_remaining': blocks_remaining,
        'days_remaining': round(days_remaining, 1),
        'estimated_date': estimate_date(seconds_remaining),
        'current_reward': get_current_reward(current_height),
        'post_halving_reward': get_current_reward(current_height) / 2
    }


def estimate_date(seconds_from_now: float) -> str:
    """估算未来日期"""
    import datetime
    future = datetime.datetime.now() + datetime.timedelta(seconds=seconds_from_now)
    return future.strftime("%Y-%m-%d")


def get_inflation_stats(current_height: Optional[int] = None) -> dict:
    """
    获取完整的通胀统计
    """
    if current_height is None:
        current_height = get_current_block_height()
    
    circulating = get_circulating_supply(current_height)
    current_reward = get_current_reward(current_height)
    inflation_rate = get_inflation_rate(current_height)
    halving = get_halving_countdown(current_height)
    
    # 供应进度
    supply_progress = (circulating / TOTAL_SUPPLY) * 100
    
    return {
        'block_height': current_height,
        'supply': {
            'circulating': round(circulating, 2),
            'total_cap': TOTAL_SUPPLY,
            'remaining': round(TOTAL_SUPPLY - circulating, 2),
            'progress_percent': round(supply_progress, 2)
        },
        'reward': {
            'current': current_reward,
            'daily_new_btc': round(current_reward * 144, 2),  # 约144个区块/天
            'annual_new_btc': round(current_reward * 52560, 2)
        },
        'inflation': {
            'annual_rate': round(inflation_rate, 2),
            'comparison': compare_inflation(inflation_rate)
        },
        'halving': halving,
        'milestones': get_supply_milestones(circulating)
    }


def compare_inflation(btc_rate: float) -> list:
    """与其他资产的通胀对比"""
    comparisons = [
        {'asset': '比特币', 'rate': btc_rate, 'type': 'crypto'},
        {'asset': '黄金', 'rate': 1.5, 'type': 'commodity'},
        {'asset': '美元 (M2)', 'rate': 6.0, 'type': 'fiat'},
        {'asset': '以太坊 (POS后)', 'rate': 0.5, 'type': 'crypto'},
    ]
    
    return comparisons


def get_supply_milestones(current_supply: float) -> list:
    """供应里程碑"""
    milestones = [
        {'threshold': 18_000_000, 'label': '1800万 BTC'},
        {'threshold': 19_000_000, 'label': '1900万 BTC'},
        {'threshold': 19_500_000, 'label': '1950万 BTC'},
        {'threshold': 20_000_000, 'label': '2000万 BTC'},
        {'threshold': 20_500_000, 'label': '2050万 BTC'},
        {'threshold': 20_900_000, 'label': '2090万 BTC (99.5%)'},
    ]
    
    result = []
    for m in milestones:
        reached = current_supply >= m['threshold']
        result.append({
            'label': m['label'],
            'reached': reached,
            'status': '✅' if reached else '⏳'
        })
    
    return result


def project_future_supply(years: int = 10) -> list:
    """预测未来供应量"""
    current_height = get_current_block_height()
    blocks_per_year = 52560
    
    projections = []
    
    for year in range(years + 1):
        future_height = current_height + year * blocks_per_year
        supply = get_circulating_supply(future_height)
        inflation = get_inflation_rate(future_height)
        
        projections.append({
            'year': year,
            'height': future_height,
            'supply': round(supply, 0),
            'inflation_rate': round(inflation, 3)
        })
    
    return projections


if __name__ == '__main__':
    print("=" * 60)
    print("比特币通胀率仪表盘 (Inflation Dashboard)")
    print("=" * 60)
    
    stats = get_inflation_stats()
    
    print(f"\n区块高度: {stats['block_height']:,}")
    
    print(f"\n供应量:")
    print(f"  流通量: {stats['supply']['circulating']:,.0f} BTC")
    print(f"  剩余: {stats['supply']['remaining']:,.0f} BTC")
    print(f"  进度: {stats['supply']['progress_percent']:.2f}%")
    
    print(f"\n通胀率:")
    print(f"  年化: {stats['inflation']['annual_rate']:.2f}%")
    print(f"  每日新增: {stats['reward']['daily_new_btc']:.2f} BTC")
    
    print(f"\n下次减半:")
    print(f"  剩余区块: {stats['halving']['blocks_remaining']:,}")
    print(f"  预计日期: {stats['halving']['estimated_date']}")
    print(f"  减半后奖励: {stats['halving']['post_halving_reward']} BTC")
