"""
挖矿盈亏平衡计算器 (Mining Breakeven Calculator)
计算关机币价和挖矿盈亏
"""
import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class MiningEconomics:
    """挖矿经济数据"""
    hashrate_th: float          # 算力 (TH/s)
    power_watts: int            # 功耗 (W)
    electricity_cost: float     # 电费 ($/kWh)
    pool_fee_percent: float     # 矿池费 (%)
    btc_price: float            # BTC 价格
    network_difficulty: float   # 全网难度
    block_reward: float         # 区块奖励


def get_bitcoin_data() -> dict:
    """
    获取比特币实时数据
    使用多个 API 源作为备选
    """
    data = {
        'price_usd': 0,
        'difficulty': 0,
        'block_height': 0,
        'hashrate': 0,
        'success': False
    }
    
    # 尝试从 blockchain.info 获取
    try:
        # 获取价格
        price_resp = requests.get(
            'https://blockchain.info/ticker',
            timeout=5
        )
        if price_resp.status_code == 200:
            data['price_usd'] = price_resp.json().get('USD', {}).get('last', 0)
        
        # 获取难度和区块高度
        stats_resp = requests.get(
            'https://blockchain.info/q/getdifficulty',
            timeout=5
        )
        if stats_resp.status_code == 200:
            data['difficulty'] = float(stats_resp.text)
        
        height_resp = requests.get(
            'https://blockchain.info/q/getblockcount',
            timeout=5
        )
        if height_resp.status_code == 200:
            data['block_height'] = int(height_resp.text)
        
        data['success'] = True
        
    except Exception as e:
        # 使用模拟数据（教学目的）
        data = {
            'price_usd': 45000,
            'difficulty': 72_000_000_000_000,  # 72T
            'block_height': 820000,
            'hashrate': 500_000_000,  # 500 EH/s
            'success': False,
            'error': str(e),
            'note': '使用模拟数据（无法连接API）'
        }
    
    return data


def calculate_mining_profit(
    hashrate_th: float,
    power_watts: int,
    electricity_cost: float,
    pool_fee_percent: float = 2.0,
    btc_price: Optional[float] = None,
    difficulty: Optional[float] = None
) -> dict:
    """
    计算挖矿盈亏
    
    参数:
        hashrate_th: 矿机算力 (TH/s)
        power_watts: 矿机功耗 (瓦)
        electricity_cost: 电费 ($/kWh)
        pool_fee_percent: 矿池费率 (%)
        btc_price: BTC 价格 (可选，自动获取)
        difficulty: 网络难度 (可选，自动获取)
    
    返回:
        详细的盈亏计算结果
    """
    # 获取实时数据
    btc_data = get_bitcoin_data()
    
    if btc_price is None:
        btc_price = btc_data['price_usd'] or 45000
    if difficulty is None:
        difficulty = btc_data['difficulty'] or 72_000_000_000_000
    
    # 当前区块奖励（减半周期计算）
    block_height = btc_data.get('block_height', 820000)
    halvings = block_height // 210000
    block_reward = 50 / (2 ** halvings)
    
    # 每日理论产出 BTC
    # 公式: (hashrate * 86400 * block_reward) / (difficulty * 2^32)
    hashrate_h = hashrate_th * 1e12  # TH/s -> H/s
    daily_btc = (hashrate_h * 86400 * block_reward) / (difficulty * (2 ** 32))
    
    # 扣除矿池费
    daily_btc_net = daily_btc * (1 - pool_fee_percent / 100)
    
    # 每日收入 (USD)
    daily_revenue = daily_btc_net * btc_price
    
    # 每日电力成本
    daily_power_kwh = (power_watts * 24) / 1000
    daily_electricity_cost = daily_power_kwh * electricity_cost
    
    # 每日利润
    daily_profit = daily_revenue - daily_electricity_cost
    
    # 关机币价（盈亏平衡点）
    if daily_btc_net > 0:
        breakeven_price = daily_electricity_cost / daily_btc_net
    else:
        breakeven_price = float('inf')
    
    return {
        'inputs': {
            'hashrate_th': hashrate_th,
            'power_watts': power_watts,
            'electricity_cost': electricity_cost,
            'pool_fee_percent': pool_fee_percent
        },
        'market_data': {
            'btc_price': btc_price,
            'difficulty': difficulty,
            'block_reward': block_reward,
            'block_height': block_height,
            'data_source': 'live' if btc_data['success'] else 'simulated'
        },
        'daily_mining': {
            'btc_mined': round(daily_btc, 8),
            'btc_after_fee': round(daily_btc_net, 8),
            'revenue_usd': round(daily_revenue, 2),
            'electricity_cost': round(daily_electricity_cost, 2),
            'profit_usd': round(daily_profit, 2)
        },
        'monthly': {
            'btc_mined': round(daily_btc_net * 30, 6),
            'revenue_usd': round(daily_revenue * 30, 2),
            'electricity_cost': round(daily_electricity_cost * 30, 2),
            'profit_usd': round(daily_profit * 30, 2)
        },
        'breakeven': {
            'shutdown_price': round(breakeven_price, 2),
            'current_margin': round((btc_price - breakeven_price) / btc_price * 100, 1) if breakeven_price < btc_price else 0,
            'profitable': daily_profit > 0
        }
    }


def get_breakeven_price(
    hashrate_th: float,
    power_watts: int,
    electricity_cost: float,
    pool_fee_percent: float = 2.0
) -> float:
    """简化版：直接返回关机币价"""
    result = calculate_mining_profit(
        hashrate_th, power_watts, electricity_cost, pool_fee_percent
    )
    return result['breakeven']['shutdown_price']


def compare_miners(electricity_cost: float = 0.05) -> list:
    """
    对比常见矿机型号的盈亏情况
    """
    miners = [
        {'name': 'Antminer S19 Pro', 'hashrate': 110, 'power': 3250},
        {'name': 'Antminer S19j Pro+', 'hashrate': 122, 'power': 3355},
        {'name': 'Whatsminer M50S', 'hashrate': 126, 'power': 3276},
        {'name': 'Antminer S21', 'hashrate': 200, 'power': 3500},
    ]
    
    results = []
    for miner in miners:
        profit = calculate_mining_profit(
            hashrate_th=miner['hashrate'],
            power_watts=miner['power'],
            electricity_cost=electricity_cost
        )
        results.append({
            'name': miner['name'],
            'hashrate': miner['hashrate'],
            'power': miner['power'],
            'daily_profit': profit['daily_mining']['profit_usd'],
            'shutdown_price': profit['breakeven']['shutdown_price'],
            'profitable': profit['breakeven']['profitable']
        })
    
    return results


if __name__ == '__main__':
    print("=" * 60)
    print("挖矿盈亏计算器 (Mining Profit Calculator)")
    print("=" * 60)
    
    # 示例：Antminer S19 Pro
    result = calculate_mining_profit(
        hashrate_th=110,      # 110 TH/s
        power_watts=3250,     # 3250 W
        electricity_cost=0.05 # $0.05/kWh
    )
    
    print(f"\n市场数据:")
    print(f"  BTC 价格: ${result['market_data']['btc_price']:,.0f}")
    print(f"  全网难度: {result['market_data']['difficulty']:,.0f}")
    
    print(f"\n每日收益:")
    print(f"  挖矿产出: {result['daily_mining']['btc_after_fee']:.8f} BTC")
    print(f"  收入: ${result['daily_mining']['revenue_usd']:.2f}")
    print(f"  电费: ${result['daily_mining']['electricity_cost']:.2f}")
    print(f"  利润: ${result['daily_mining']['profit_usd']:.2f}")
    
    print(f"\n关机币价: ${result['breakeven']['shutdown_price']:,.0f}")
