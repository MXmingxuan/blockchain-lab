"""
时间锁交易生成器 (LockTime Transaction Builder)
演示 nLockTime 时间锁机制
"""
import time
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta


def get_current_block_height() -> int:
    """
    获取当前区块高度
    """
    try:
        resp = requests.get(
            'https://blockchain.info/latestblock',
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json().get('height', 0)
    except:
        pass
    
    # 估算值（2024年初约为）
    return 878000


def explain_locktime(locktime: int) -> Dict:
    """
    解释 nLockTime 值的含义
    """
    if locktime == 0:
        return {
            'type': 'disabled',
            'description': '无时间锁，交易立即有效',
            'emoji': '🟢'
        }
    elif locktime < 500000000:
        # 区块高度
        current_height = get_current_block_height()
        blocks_remaining = locktime - current_height
        
        if blocks_remaining <= 0:
            return {
                'type': 'block_height',
                'value': locktime,
                'description': f'区块高度锁 (已解锁)',
                'blocks_remaining': 0,
                'estimated_time': '已可广播',
                'emoji': '🟢'
            }
        else:
            # 估算时间（每区块约10分钟）
            minutes = blocks_remaining * 10
            unlock_time = datetime.now() + timedelta(minutes=minutes)
            
            return {
                'type': 'block_height',
                'value': locktime,
                'description': f'区块高度锁',
                'current_height': current_height,
                'target_height': locktime,
                'blocks_remaining': blocks_remaining,
                'estimated_time': unlock_time.strftime('%Y-%m-%d %H:%M'),
                'estimated_minutes': minutes,
                'emoji': '🔒'
            }
    else:
        # Unix 时间戳
        unlock_datetime = datetime.fromtimestamp(locktime)
        now = datetime.now()
        
        if unlock_datetime <= now:
            return {
                'type': 'unix_timestamp',
                'value': locktime,
                'description': f'时间戳锁 (已解锁)',
                'unlock_time': unlock_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'emoji': '🟢'
            }
        else:
            remaining = unlock_datetime - now
            
            return {
                'type': 'unix_timestamp',
                'value': locktime,
                'description': f'时间戳锁',
                'unlock_time': unlock_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'time_remaining': str(remaining).split('.')[0],
                'emoji': '🔒'
            }


def create_locktime_demo(lock_type: str = 'blocks', lock_value: int = 100) -> Dict:
    """
    创建时间锁交易演示
    
    Args:
        lock_type: 'blocks' 或 'time'
        lock_value: 区块数或小时数
    """
    current_height = get_current_block_height()
    current_time = int(time.time())
    
    if lock_type == 'blocks':
        locktime = current_height + lock_value
        lock_description = f"当前高度 + {lock_value} 区块"
    else:  # time
        locktime = current_time + (lock_value * 3600)  # 小时转秒
        lock_description = f"当前时间 + {lock_value} 小时"
    
    explanation = explain_locktime(locktime)
    
    # 构建模拟交易
    mock_tx = {
        'version': 2,
        'inputs': [
            {
                'txid': 'a1b2c3d4' + '0' * 56,
                'vout': 0,
                'sequence': 0xFFFFFFFE  # 必须小于 0xFFFFFFFF 才能启用 locktime
            }
        ],
        'outputs': [
            {
                'value': 0.5,
                'address': '1ReceiveAddress...'
            }
        ],
        'locktime': locktime
    }
    
    return {
        'success': True,
        'transaction': mock_tx,
        'locktime_value': locktime,
        'lock_description': lock_description,
        'explanation': explanation,
        'current_block': current_height,
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sequence_note': 'sequence 必须 < 0xFFFFFFFF 才能启用 nLockTime',
        'broadcast_status': '🚫 交易被拒绝' if explanation['emoji'] == '🔒' else '✅ 可以广播'
    }


def get_locktime_use_cases() -> list:
    """
    获取时间锁的应用场景
    """
    return [
        {
            'name': '遗产继承 (Dead Man\'s Switch)',
            'description': '设置一笔交易在未来某时间将资金转给继承人。如果本人还活着，可以在到期前花费这笔 UTXO 来"刷新"锁定。',
            'lock_type': 'time',
            'typical_period': '6个月 - 1年',
            'emoji': '🏛️'
        },
        {
            'name': '托管服务',
            'description': '买卖双方创建一笔锁定交易。在锁定期内，任何一方都无法单独动用资金，需要等待确认或双方签名。',
            'lock_type': 'blocks',
            'typical_period': '144 区块 (约1天)',
            'emoji': '🤝'
        },
        {
            'name': '定投/储蓄',
            'description': '创建多笔锁定交易，每隔一段时间解锁一笔，实现"强制储蓄"。',
            'lock_type': 'time',
            'typical_period': '每月/每季度',
            'emoji': '💰'
        },
        {
            'name': '支付通道',
            'description': '闪电网络使用时间锁来保证通道关闭时的资金安全。',
            'lock_type': 'blocks',
            'typical_period': '根据通道配置',
            'emoji': '⚡'
        },
        {
            'name': '原子交换',
            'description': '跨链交易中，时间锁确保如果交换未完成，资金会自动退回。',
            'lock_type': 'blocks',
            'typical_period': '24-48小时',
            'emoji': '🔄'
        }
    ]


def simulate_locktime_rejection() -> Dict:
    """
    模拟时间锁交易被拒绝的场景
    """
    current_height = get_current_block_height()
    future_height = current_height + 100
    
    return {
        'scenario': '尝试广播一笔锁定到未来区块的交易',
        'transaction': {
            'locktime': future_height,
            'value': '0.5 BTC'
        },
        'current_state': {
            'current_block': current_height,
            'target_block': future_height,
            'blocks_remaining': 100
        },
        'node_response': {
            'accepted': False,
            'error': 'non-final',
            'message': f'交易 locktime ({future_height}) 大于当前区块高度 ({current_height})'
        },
        'explanation': [
            '1. 节点收到交易请求',
            '2. 检查 nLockTime 字段',
            f'3. 发现 locktime={future_height} > 当前高度={current_height}',
            '4. 判定交易为 "non-final"',
            '5. 拒绝将交易加入内存池',
            f'6. 需等待区块到达 {future_height} 后才能广播'
        ]
    }


if __name__ == '__main__':
    print("=" * 60)
    print("时间锁交易生成器 (LockTime Builder)")
    print("=" * 60)
    
    # 演示区块高度锁
    print("\n🔒 区块高度锁演示 (+100 区块):")
    demo = create_locktime_demo('blocks', 100)
    print(f"   当前区块: #{demo['current_block']}")
    print(f"   锁定值: {demo['locktime_value']}")
    print(f"   状态: {demo['explanation']['emoji']} {demo['explanation']['description']}")
    if 'blocks_remaining' in demo['explanation']:
        print(f"   剩余区块: {demo['explanation']['blocks_remaining']}")
        print(f"   预计解锁: {demo['explanation'].get('estimated_time', '')}")
    
    # 演示时间戳锁
    print("\n⏰ 时间戳锁演示 (+24 小时):")
    demo2 = create_locktime_demo('time', 24)
    print(f"   当前时间: {demo2['current_time']}")
    print(f"   锁定值: {demo2['locktime_value']}")
    print(f"   解锁时间: {demo2['explanation'].get('unlock_time', '')}")
    
    # 应用场景
    print("\n" + "=" * 60)
    print("📚 时间锁应用场景:")
    for case in get_locktime_use_cases():
        print(f"\n  {case['emoji']} {case['name']}")
        print(f"     {case['description'][:50]}...")
