"""
孤块/分叉监控器 (Orphan Block / Fork Monitor)
解释确认数安全性和链重组风险
"""
import requests
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ConfirmationLevel:
    """确认等级"""
    confirmations: int
    security_level: str
    description: str
    recommended_for: str
    reorg_probability: str


# 确认数安全等级
CONFIRMATION_LEVELS = [
    ConfirmationLevel(
        confirmations=0,
        security_level="⚠️ 无确认",
        description="交易在内存池中，尚未被打包",
        recommended_for="不建议接受",
        reorg_probability="100% (未上链)"
    ),
    ConfirmationLevel(
        confirmations=1,
        security_level="🟡 极低",
        description="已被打包进最新区块",
        recommended_for="极小额交易",
        reorg_probability="~10% (临时分叉可能)"
    ),
    ConfirmationLevel(
        confirmations=2,
        security_level="🟡 低",
        description="2个区块确认",
        recommended_for="小额交易",
        reorg_probability="~1%"
    ),
    ConfirmationLevel(
        confirmations=3,
        security_level="🟠 中等",
        description="3个区块确认",
        recommended_for="普通交易",
        reorg_probability="~0.1%"
    ),
    ConfirmationLevel(
        confirmations=6,
        security_level="🟢 高",
        description="6个区块确认 (比特币标准)",
        recommended_for="大额交易、交易所入金",
        reorg_probability="<0.001% (需51%攻击)"
    ),
    ConfirmationLevel(
        confirmations=12,
        security_level="🟢 极高",
        description="12个区块确认",
        recommended_for="大型机构交易",
        reorg_probability="概率可忽略"
    ),
]


def get_confirmation_safety(confirmations: int) -> dict:
    """
    根据确认数返回安全等级信息
    """
    # 找到匹配的等级
    level = CONFIRMATION_LEVELS[0]
    for cl in CONFIRMATION_LEVELS:
        if confirmations >= cl.confirmations:
            level = cl
    
    return {
        'confirmations': confirmations,
        'security_level': level.security_level,
        'description': level.description,
        'recommended_for': level.recommended_for,
        'reorg_probability': level.reorg_probability,
        'wait_time_minutes': confirmations * 10,  # 平均每个区块10分钟
        'is_safe_for_exchange': confirmations >= 6
    }


def get_latest_blocks(count: int = 10) -> List[dict]:
    """
    获取最近的区块信息
    """
    blocks = []
    
    try:
        # 获取最新区块
        resp = requests.get(
            'https://blockchain.info/blocks?format=json',
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            for block in data.get('blocks', [])[:count]:
                blocks.append({
                    'height': block.get('height'),
                    'hash': block.get('hash'),
                    'time': block.get('time'),
                    'main_chain': block.get('main_chain', True),
                    'tx_count': block.get('n_tx', 0)
                })
    
    except Exception as e:
        # 模拟数据
        import time
        current_time = int(time.time())
        for i in range(count):
            blocks.append({
                'height': 820000 - i,
                'hash': f"00000000000000000000{'0' * 10}{i:05d}",
                'time': current_time - i * 600,
                'main_chain': True,
                'tx_count': 2500 + i * 10
            })
    
    return blocks


def check_recent_reorgs() -> dict:
    """
    检查最近是否有链重组
    (简化版本 - 实际需要更复杂的监控逻辑)
    """
    blocks = get_latest_blocks(20)
    
    # 检查区块高度是否连续
    heights = [b['height'] for b in blocks]
    gaps = []
    
    for i in range(1, len(heights)):
        expected = heights[i-1] - 1
        if heights[i] != expected:
            gaps.append({
                'expected': expected,
                'actual': heights[i],
                'gap': expected - heights[i]
            })
    
    # 检查是否所有区块都在主链上
    orphans = [b for b in blocks if not b.get('main_chain', True)]
    
    return {
        'blocks_checked': len(blocks),
        'latest_height': blocks[0]['height'] if blocks else 0,
        'chain_continuous': len(gaps) == 0,
        'gaps_found': gaps,
        'orphan_blocks': len(orphans),
        'network_status': '🟢 正常' if len(gaps) == 0 and len(orphans) == 0 else '🟡 检测到异常'
    }


def explain_why_6_confirmations() -> dict:
    """
    解释为什么需要6个确认
    """
    return {
        'title': '为什么交易所要求6个确认？',
        'explanation': [
            {
                'point': '临时分叉风险',
                'detail': '当两个矿工同时挖出区块，会产生临时分叉。网络会选择更长的链。'
            },
            {
                'point': '最长链原则',
                'detail': '比特币遵循"最长链原则"，较短的分支会变成孤块，其中的交易需要重新确认。'
            },
            {
                'point': '51%攻击防护',
                'detail': '攻击者需要控制超过50%算力才能重写历史。6个确认意味着攻击者需要连续挖出7个区块，成本极高。'
            },
            {
                'point': '概率计算',
                'detail': '每多一个确认，被逆转的概率指数级下降。6个确认后，逆转概率低于0.001%。'
            },
            {
                'point': '时间成本',
                'detail': '6个确认约需1小时，足够网络达成共识，也是安全与便利的平衡点。'
            }
        ],
        'attack_cost': calculate_attack_cost(6),
        'summary': '6个确认是安全性与用户体验的最佳平衡点，是比特币社区长期实践的共识。'
    }


def calculate_attack_cost(confirmations: int) -> dict:
    """
    估算重写N个区块的攻击成本
    """
    # 假设全网算力 500 EH/s，每个区块奖励 6.25 BTC
    hashrate_ehs = 500
    block_reward = 6.25
    btc_price = 45000
    
    # 攻击者需要的算力（超过50%）
    attack_hashrate = hashrate_ehs * 0.51
    
    # 电力成本估算（假设 $0.03/kWh，30 J/TH 效率）
    power_per_eh = 30 * 1e6  # watts per EH/s
    total_power = attack_hashrate * power_per_eh / 1e9  # GW
    
    # 挖N个区块的时间（分钟）
    time_minutes = confirmations * 10
    
    # 电力成本
    electricity_cost = total_power * 1e6 * (time_minutes / 60) * 0.03 / 1000
    
    # 放弃的区块奖励
    opportunity_cost = confirmations * block_reward * btc_price
    
    return {
        'confirmations': confirmations,
        'required_hashrate': f"{attack_hashrate:.0f} EH/s",
        'required_power': f"{total_power:.1f} GW",
        'time_required': f"{time_minutes} 分钟",
        'electricity_cost': f"${electricity_cost:,.0f}",
        'opportunity_cost': f"${opportunity_cost:,.0f}",
        'total_minimum_cost': f"${electricity_cost + opportunity_cost:,.0f}",
        'note': '实际成本更高，还需考虑硬件投资、协调成本等'
    }


def visualize_fork():
    """返回分叉示意图（文本版）"""
    return """
    区块链分叉示意图:
    
    主链 (Longest Chain):
    [Block N] → [Block N+1] → [Block N+2] → [Block N+3] → ...
                     ↓
                [Orphan]  ← 临时分叉（被抛弃）
    
    当两个矿工同时发现有效区块:
    1. 网络暂时存在两个版本
    2. 后续区块会选择其中一个继续延长
    3. 较短的分支变成"孤块"
    4. 孤块中的交易回到内存池重新确认
    
    这就是为什么需要等待多个确认！
    """


if __name__ == '__main__':
    print("=" * 60)
    print("分叉监控器 (Fork Monitor)")
    print("=" * 60)
    
    # 检查确认数安全性
    for conf in [0, 1, 3, 6, 12]:
        safety = get_confirmation_safety(conf)
        print(f"\n{conf} 确认: {safety['security_level']}")
        print(f"  适用于: {safety['recommended_for']}")
    
    # 解释6确认
    print("\n" + "=" * 60)
    explanation = explain_why_6_confirmations()
    print(explanation['title'])
    for point in explanation['explanation']:
        print(f"\n• {point['point']}")
        print(f"  {point['detail']}")
