"""
粉尘过滤器与清洗成本计算器 (Dust Analyzer)
识别和分析粉尘 UTXO
"""
from typing import List, Dict
from dataclasses import dataclass


# 比特币交易大小估算常量
P2PKH_INPUT_SIZE = 148  # 字节
P2PKH_OUTPUT_SIZE = 34  # 字节
TX_OVERHEAD = 10  # 交易头部开销

SATOSHI_PER_BTC = 100_000_000


@dataclass
class DustAnalysis:
    """粉尘分析结果"""
    is_dust: bool
    value_satoshi: int
    spend_cost_satoshi: int
    net_value_satoshi: int


def calculate_spend_cost(utxo_value: int, fee_rate: float) -> Dict:
    """
    计算花费单个 UTXO 的成本
    
    Args:
        utxo_value: UTXO 金额（聪）
        fee_rate: 每字节费率（聪/字节）
    
    Returns:
        花费成本分析
    """
    # 花费一个 UTXO 需要的最小交易大小
    # 1 输入 + 1 输出 + 开销
    min_tx_size = P2PKH_INPUT_SIZE + P2PKH_OUTPUT_SIZE + TX_OVERHEAD
    
    spend_cost = int(min_tx_size * fee_rate)
    net_value = utxo_value - spend_cost
    is_dust = net_value <= 0
    
    return {
        'utxo_value_satoshi': utxo_value,
        'utxo_value_btc': utxo_value / SATOSHI_PER_BTC,
        'tx_size_bytes': min_tx_size,
        'fee_rate': fee_rate,
        'spend_cost_satoshi': spend_cost,
        'spend_cost_btc': spend_cost / SATOSHI_PER_BTC,
        'net_value_satoshi': max(0, net_value),
        'net_value_btc': max(0, net_value) / SATOSHI_PER_BTC,
        'is_dust': is_dust,
        'dust_reason': '手续费超过 UTXO 价值' if is_dust else None
    }


def analyze_dust(utxos: List[Dict], fee_rate: float) -> Dict:
    """
    分析 UTXO 列表中的粉尘
    
    Args:
        utxos: UTXO 列表
        fee_rate: 每字节费率（聪/字节）
    """
    dust_utxos = []
    usable_utxos = []
    total_dust_value = 0
    total_usable_value = 0
    
    for utxo in utxos:
        value = utxo.get('value_satoshi', 0)
        analysis = calculate_spend_cost(value, fee_rate)
        
        utxo_info = {
            **utxo,
            'analysis': analysis
        }
        
        if analysis['is_dust']:
            dust_utxos.append(utxo_info)
            total_dust_value += value
        else:
            usable_utxos.append(utxo_info)
            total_usable_value += analysis['net_value_satoshi']
    
    return {
        'fee_rate': fee_rate,
        'total_utxos': len(utxos),
        'dust_count': len(dust_utxos),
        'usable_count': len(usable_utxos),
        'dust_percentage': (len(dust_utxos) / len(utxos) * 100) if utxos else 0,
        'total_dust_value_satoshi': total_dust_value,
        'total_dust_value_btc': total_dust_value / SATOSHI_PER_BTC,
        'total_usable_value_satoshi': total_usable_value,
        'total_usable_value_btc': total_usable_value / SATOSHI_PER_BTC,
        'dust_utxos': dust_utxos,
        'usable_utxos': usable_utxos
    }


def get_effective_balance(utxos: List[Dict], fee_rate: float) -> Dict:
    """
    计算真实可用余额（扣除粉尘后）
    """
    analysis = analyze_dust(utxos, fee_rate)
    
    total_nominal = sum(u.get('value_satoshi', 0) for u in utxos)
    effective = analysis['total_usable_value_satoshi']
    locked_in_dust = analysis['total_dust_value_satoshi']
    
    return {
        'nominal_balance_btc': total_nominal / SATOSHI_PER_BTC,
        'effective_balance_btc': effective / SATOSHI_PER_BTC,
        'locked_in_dust_btc': locked_in_dust / SATOSHI_PER_BTC,
        'dust_ratio': (locked_in_dust / total_nominal * 100) if total_nominal > 0 else 0,
        'fee_rate': fee_rate,
        'recommendation': get_recommendation(analysis)
    }


def get_recommendation(analysis: Dict) -> str:
    """根据分析结果给出建议"""
    dust_pct = analysis['dust_percentage']
    
    if dust_pct == 0:
        return "✅ 钱包干净，没有粉尘 UTXO"
    elif dust_pct < 20:
        return "🟢 少量粉尘，影响不大"
    elif dust_pct < 50:
        return "🟡 粉尘较多，建议在低费率时合并 UTXO"
    else:
        return "🔴 粉尘过多！大部分余额实际不可用，强烈建议清理"


def calculate_consolidation_cost(utxos: List[Dict], fee_rate: float) -> Dict:
    """
    计算将所有 UTXO 合并为单个 UTXO 的成本
    """
    if not utxos:
        return {'success': False, 'error': '没有 UTXO'}
    
    # 合并交易大小 = N 个输入 + 1 个输出 + 开销
    n_inputs = len(utxos)
    tx_size = n_inputs * P2PKH_INPUT_SIZE + P2PKH_OUTPUT_SIZE + TX_OVERHEAD
    
    total_fee = int(tx_size * fee_rate)
    total_input = sum(u.get('value_satoshi', 0) for u in utxos)
    output_value = total_input - total_fee
    
    return {
        'success': output_value > 0,
        'input_count': n_inputs,
        'total_input_satoshi': total_input,
        'total_input_btc': total_input / SATOSHI_PER_BTC,
        'tx_size_bytes': tx_size,
        'fee_rate': fee_rate,
        'total_fee_satoshi': total_fee,
        'total_fee_btc': total_fee / SATOSHI_PER_BTC,
        'output_value_satoshi': max(0, output_value),
        'output_value_btc': max(0, output_value) / SATOSHI_PER_BTC,
        'cost_percentage': (total_fee / total_input * 100) if total_input > 0 else 0,
        'worth_consolidating': output_value > 0 and (total_fee / total_input) < 0.1
    }


def simulate_fee_scenarios(utxos: List[Dict]) -> List[Dict]:
    """
    模拟不同费率下的粉尘情况
    """
    scenarios = []
    fee_rates = [1, 5, 10, 20, 50, 100, 200]  # 聪/字节
    
    for rate in fee_rates:
        analysis = analyze_dust(utxos, rate)
        balance = get_effective_balance(utxos, rate)
        
        scenarios.append({
            'fee_rate': rate,
            'fee_level': get_fee_level(rate),
            'dust_count': analysis['dust_count'],
            'dust_percentage': round(analysis['dust_percentage'], 1),
            'effective_balance_btc': balance['effective_balance_btc']
        })
    
    return scenarios


def get_fee_level(rate: float) -> str:
    """获取费率等级描述"""
    if rate <= 5:
        return "极低 💚"
    elif rate <= 20:
        return "低 🟢"
    elif rate <= 50:
        return "中等 🟡"
    elif rate <= 100:
        return "高 🟠"
    else:
        return "极高 🔴"


if __name__ == '__main__':
    print("=" * 60)
    print("粉尘分析器 (Dust Analyzer)")
    print("=" * 60)
    
    # 模拟 UTXO 列表
    mock_utxos = [
        {'value_satoshi': 50000000, 'value_btc': 0.5},      # 0.5 BTC
        {'value_satoshi': 200000000, 'value_btc': 2.0},     # 2.0 BTC
        {'value_satoshi': 10000000, 'value_btc': 0.1},      # 0.1 BTC
        {'value_satoshi': 5000, 'value_btc': 0.00005},      # 5000 聪 (粉尘)
        {'value_satoshi': 1000, 'value_btc': 0.00001},      # 1000 聪 (粉尘)
        {'value_satoshi': 50000, 'value_btc': 0.0005},      # 50000 聪
    ]
    
    print("\n📊 不同费率下的粉尘分析:")
    scenarios = simulate_fee_scenarios(mock_utxos)
    
    for s in scenarios:
        print(f"\n  费率 {s['fee_rate']} sat/B ({s['fee_level']}):")
        print(f"    粉尘 UTXO: {s['dust_count']} 个 ({s['dust_percentage']}%)")
        print(f"    有效余额: {s['effective_balance_btc']:.8f} BTC")
    
    print("\n" + "=" * 60)
    print("💰 合并成本计算 (费率 10 sat/B):")
    consolidation = calculate_consolidation_cost(mock_utxos, 10)
    print(f"  输入: {consolidation['input_count']} 个 UTXO")
    print(f"  总金额: {consolidation['total_input_btc']:.8f} BTC")
    print(f"  交易大小: {consolidation['tx_size_bytes']} 字节")
    print(f"  手续费: {consolidation['total_fee_btc']:.8f} BTC ({consolidation['cost_percentage']:.2f}%)")
    print(f"  合并后: {consolidation['output_value_btc']:.8f} BTC")
