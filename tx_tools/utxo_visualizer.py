"""
UTXO 模型可视化工具 (UTXO Visualizer)
理解比特币的未花费交易输出模型
"""
import requests
import time
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class UTXO:
    """未花费交易输出"""
    tx_hash: str
    output_index: int
    value_satoshi: int
    value_btc: float
    confirmations: int
    script_type: str = "P2PKH"


SATOSHI_PER_BTC = 100_000_000


def get_address_utxos(address: str) -> Dict:
    """
    获取指定地址的所有 UTXO
    """
    utxos = []
    total_value = 0
    
    try:
        # 使用 Blockchain.info API
        resp = requests.get(
            f'https://blockchain.info/unspent?active={address}',
            timeout=15
        )
        
        if resp.status_code == 200:
            data = resp.json()
            for u in data.get('unspent_outputs', []):
                value_sat = u.get('value', 0)
                utxo = {
                    'tx_hash': u.get('tx_hash_big_endian', ''),
                    'output_index': u.get('tx_output_n', 0),
                    'value_satoshi': value_sat,
                    'value_btc': value_sat / SATOSHI_PER_BTC,
                    'confirmations': u.get('confirmations', 0),
                    'script': u.get('script', '')
                }
                utxos.append(utxo)
                total_value += value_sat
            
            return {
                'success': True,
                'address': address,
                'utxo_count': len(utxos),
                'total_satoshi': total_value,
                'total_btc': total_value / SATOSHI_PER_BTC,
                'utxos': utxos
            }
        elif resp.status_code == 500:
            # 地址没有 UTXO
            return {
                'success': True,
                'address': address,
                'utxo_count': 0,
                'total_satoshi': 0,
                'total_btc': 0,
                'utxos': [],
                'message': '该地址没有未花费输出'
            }
    
    except Exception as e:
        pass
    
    # 返回模拟数据用于演示
    mock_utxos = [
        {'tx_hash': 'a1b2c3' + '0' * 58, 'output_index': 0, 
         'value_satoshi': 50000000, 'value_btc': 0.5, 'confirmations': 100},
        {'tx_hash': 'd4e5f6' + '0' * 58, 'output_index': 1, 
         'value_satoshi': 200000000, 'value_btc': 2.0, 'confirmations': 50},
        {'tx_hash': 'g7h8i9' + '0' * 58, 'output_index': 0, 
         'value_satoshi': 10000000, 'value_btc': 0.1, 'confirmations': 200},
        {'tx_hash': 'j0k1l2' + '0' * 58, 'output_index': 2, 
         'value_satoshi': 5000, 'value_btc': 0.00005, 'confirmations': 300},
    ]
    
    return {
        'success': True,
        'address': address or '演示地址',
        'utxo_count': len(mock_utxos),
        'total_satoshi': sum(u['value_satoshi'] for u in mock_utxos),
        'total_btc': sum(u['value_btc'] for u in mock_utxos),
        'utxos': mock_utxos,
        'is_mock': True
    }


def visualize_utxos(utxos: List[Dict]) -> List[Dict]:
    """
    将 UTXO 可视化为"硬币"
    """
    coins = []
    for i, utxo in enumerate(utxos):
        value_btc = utxo.get('value_btc', 0)
        
        # 根据金额确定硬币大小
        if value_btc >= 1.0:
            size = 'large'
            emoji = '🪙'
        elif value_btc >= 0.1:
            size = 'medium'
            emoji = '🔵'
        elif value_btc >= 0.01:
            size = 'small'
            emoji = '🟡'
        else:
            size = 'dust'
            emoji = '💨'
        
        coins.append({
            'index': i + 1,
            'emoji': emoji,
            'size': size,
            'value_btc': value_btc,
            'value_satoshi': utxo.get('value_satoshi', 0),
            'tx_hash_short': utxo.get('tx_hash', '')[:8] + '...',
            'confirmations': utxo.get('confirmations', 0)
        })
    
    # 按金额排序
    coins.sort(key=lambda x: x['value_btc'], reverse=True)
    return coins


def select_utxos_for_transfer(utxos: List[Dict], amount_btc: float, fee_btc: float = 0.0001) -> Dict:
    """
    自动选择 UTXO 用于转账（简单策略：优先使用大额）
    
    返回：选中的 UTXO、总输入、找零金额
    """
    target = amount_btc + fee_btc
    target_satoshi = int(target * SATOSHI_PER_BTC)
    
    # 按金额降序排序
    sorted_utxos = sorted(utxos, key=lambda x: x.get('value_satoshi', 0), reverse=True)
    
    selected = []
    total_input = 0
    
    for utxo in sorted_utxos:
        if total_input >= target_satoshi:
            break
        selected.append(utxo)
        total_input += utxo.get('value_satoshi', 0)
    
    if total_input < target_satoshi:
        return {
            'success': False,
            'error': '余额不足',
            'required': target,
            'available': total_input / SATOSHI_PER_BTC
        }
    
    change_satoshi = total_input - target_satoshi
    
    return {
        'success': True,
        'selected_utxos': selected,
        'selected_count': len(selected),
        'total_input_satoshi': total_input,
        'total_input_btc': total_input / SATOSHI_PER_BTC,
        'amount_btc': amount_btc,
        'fee_btc': fee_btc,
        'change_satoshi': change_satoshi,
        'change_btc': change_satoshi / SATOSHI_PER_BTC,
        'outputs': [
            {'type': 'payment', 'amount_btc': amount_btc},
            {'type': 'change', 'amount_btc': change_satoshi / SATOSHI_PER_BTC}
        ] if change_satoshi > 0 else [
            {'type': 'payment', 'amount_btc': amount_btc}
        ]
    }


def simulate_transaction(address: str, to_address: str, amount_btc: float) -> Dict:
    """
    模拟完整的交易过程
    """
    # 获取 UTXO
    utxo_result = get_address_utxos(address)
    if not utxo_result.get('success'):
        return {'success': False, 'error': '获取 UTXO 失败'}
    
    utxos = utxo_result.get('utxos', [])
    if not utxos:
        return {'success': False, 'error': '没有可用的 UTXO'}
    
    # 选择 UTXO
    selection = select_utxos_for_transfer(utxos, amount_btc)
    if not selection.get('success'):
        return selection
    
    # 构建模拟交易
    return {
        'success': True,
        'transaction': {
            'inputs': [
                {
                    'tx_hash': u.get('tx_hash', '')[:16] + '...',
                    'output_index': u.get('output_index', 0),
                    'value_btc': u.get('value_btc', 0)
                }
                for u in selection['selected_utxos']
            ],
            'outputs': [
                {'address': to_address[:16] + '...', 'value_btc': amount_btc, 'type': 'payment'},
                {'address': address[:16] + '... (找零)', 'value_btc': selection['change_btc'], 'type': 'change'}
            ] if selection['change_btc'] > 0 else [
                {'address': to_address[:16] + '...', 'value_btc': amount_btc, 'type': 'payment'}
            ],
            'fee_btc': selection['fee_btc'],
            'total_input_btc': selection['total_input_btc'],
            'total_output_btc': amount_btc + selection['change_btc']
        },
        'explanation': {
            'step1': f"从 {len(selection['selected_utxos'])} 个 UTXO 中选择了总计 {selection['total_input_btc']:.8f} BTC",
            'step2': f"支付 {amount_btc:.8f} BTC 到目标地址",
            'step3': f"找零 {selection['change_btc']:.8f} BTC 回到自己的新地址",
            'step4': f"支付矿工费 {selection['fee_btc']:.8f} BTC"
        },
        'is_mock': utxo_result.get('is_mock', False)
    }


if __name__ == '__main__':
    print("=" * 60)
    print("UTXO 模型可视化工具")
    print("=" * 60)
    
    # 演示
    result = get_address_utxos("")
    print(f"\n地址: {result['address']}")
    print(f"UTXO 数量: {result['utxo_count']}")
    print(f"总余额: {result['total_btc']:.8f} BTC")
    
    print("\n📦 UTXO 硬币视图:")
    coins = visualize_utxos(result['utxos'])
    for coin in coins:
        print(f"  {coin['emoji']} 硬币 #{coin['index']}: {coin['value_btc']:.8f} BTC ({coin['size']})")
    
    print("\n💸 模拟转账 1.5 BTC:")
    selection = select_utxos_for_transfer(result['utxos'], 1.5)
    if selection['success']:
        print(f"  选中 {selection['selected_count']} 个 UTXO")
        print(f"  总输入: {selection['total_input_btc']:.8f} BTC")
        print(f"  找零: {selection['change_btc']:.8f} BTC")
