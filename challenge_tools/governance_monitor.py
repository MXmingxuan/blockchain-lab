"""
治理与硬分叉监控器 (Governance Monitor)
追踪历史分叉事件，分析治理失败案例
"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ForkEvent:
    """硬分叉事件"""
    name: str
    original_chain: str
    fork_chain: str
    date: str
    block_height: int
    cause: str
    outcome: str
    lesson: str


# 历史硬分叉数据库
FORK_HISTORY = [
    ForkEvent(
        name="The DAO Hack / ETH-ETC Split",
        original_chain="Ethereum",
        fork_chain="Ethereum Classic (ETC)",
        date="2016-07-20",
        block_height=1920000,
        cause="DAO 智能合约漏洞被黑客利用，损失 360 万 ETH。社区对是否回滚交易产生分歧。",
        outcome="ETH 选择回滚（违反'代码即法律'），ETC 坚持不可篡改原则。两条链并存至今。",
        lesson="治理争议可能导致社区永久分裂。'代码即法律' vs '社区利益' 的哲学冲突。"
    ),
    ForkEvent(
        name="Bitcoin Cash Fork",
        original_chain="Bitcoin",
        fork_chain="Bitcoin Cash (BCH)",
        date="2017-08-01",
        block_height=478558,
        cause="区块大小之争。Core 派坚持 1MB + SegWit，大区块派要求直接扩容到 8MB。",
        outcome="BCH 分叉出去，后来又多次分裂（BSV 等）。BTC 通过 SegWit 和 Lightning 扩容。",
        lesson="扩容路线之争反映了去中心化治理的困难性。没有中央权威来做决定。"
    ),
    ForkEvent(
        name="Bitcoin SV Fork",
        original_chain="Bitcoin Cash",
        fork_chain="Bitcoin SV (BSV)",
        date="2018-11-15",
        block_height=556766,
        cause="BCH 内部对区块大小再次产生分歧。Craig Wright 派要求 128MB 区块。",
        outcome="BCH 和 BSV 分裂。BSV 后来声称要恢复'中本聪愿景'。",
        lesson="分叉可以无限递归。缺乏权威治理机制导致不断分裂。"
    ),
    ForkEvent(
        name="Constantinople Delay",
        original_chain="Ethereum",
        fork_chain="N/A (Upgrade)",
        date="2019-01-16",
        block_height=7080000,
        cause="计划升级前发现安全漏洞，紧急推迟。",
        outcome="成功协调推迟，避免了潜在攻击。展示了有效的紧急治理能力。",
        lesson="即使去中心化系统也需要某种形式的协调机制来应对紧急情况。"
    ),
    ForkEvent(
        name="Ethereum Merge",
        original_chain="Ethereum (PoW)",
        fork_chain="Ethereum (PoS)",
        date="2022-09-15",
        block_height=15537393,
        cause="从工作量证明 (PoW) 转向权益证明 (PoS)，减少能源消耗 99.95%。",
        outcome="成功合并。部分矿工创建 ETHW (PoW 分叉) 但影响有限。",
        lesson="重大技术升级需要多年准备和社区共识。成功的治理案例。"
    )
]


def get_fork_history() -> List[Dict]:
    """获取所有历史分叉事件"""
    return [
        {
            "name": f.name,
            "original": f.original_chain,
            "fork": f.fork_chain,
            "date": f.date,
            "block": f.block_height,
            "cause": f.cause,
            "outcome": f.outcome,
            "lesson": f.lesson
        }
        for f in FORK_HISTORY
    ]


def analyze_fork_risk(metrics: Dict) -> Dict:
    """
    分析当前分叉风险
    
    输入指标：
    - miner_signaling: 矿工信号支持率 (0-100)
    - community_sentiment: 社区情绪分裂度 (0-100, 100=完全分裂)
    - code_change_size: 代码变更规模 (small/medium/large)
    - upgrade_timeline: 升级时间线 (weeks)
    """
    miner_support = metrics.get("miner_signaling", 95)
    community_split = metrics.get("community_sentiment", 10)
    code_change = metrics.get("code_change_size", "small")
    timeline_weeks = metrics.get("upgrade_timeline", 12)
    
    # 计算风险分数
    risk_score = 0
    risk_factors = []
    
    # 矿工支持率
    if miner_support < 50:
        risk_score += 40
        risk_factors.append("⚠️ 矿工支持率低于 50%，可能产生竞争链")
    elif miner_support < 75:
        risk_score += 20
        risk_factors.append("⚡ 矿工支持率偏低，需要更多协调")
    
    # 社区分裂度
    if community_split > 50:
        risk_score += 30
        risk_factors.append("⚠️ 社区严重分裂，可能导致永久性分叉")
    elif community_split > 25:
        risk_score += 15
        risk_factors.append("⚡ 社区存在明显分歧")
    
    # 代码变更规模
    code_risk = {"small": 5, "medium": 15, "large": 30}
    risk_score += code_risk.get(code_change, 15)
    if code_change == "large":
        risk_factors.append("⚠️ 大规模代码变更增加技术风险")
    
    # 时间线
    if timeline_weeks < 4:
        risk_score += 20
        risk_factors.append("⚠️ 升级时间过短，社区可能准备不足")
    
    # 风险等级
    if risk_score >= 60:
        risk_level = "🔴 高风险"
        recommendation = "建议延迟升级，寻求更广泛共识"
    elif risk_score >= 30:
        risk_level = "🟡 中等风险"
        recommendation = "密切监控社区动态，准备应急方案"
    else:
        risk_level = "🟢 低风险"
        recommendation = "升级条件良好，按计划进行"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "recommendation": recommendation,
        "metrics": {
            "miner_support": f"{miner_support}%",
            "community_split": f"{community_split}%",
            "code_change": code_change,
            "timeline": f"{timeline_weeks} weeks"
        }
    }


def get_governance_lessons() -> Dict:
    """获取治理经验教训"""
    return {
        "core_challenge": {
            "title": "治理是区块链最难的挑战",
            "gensler_quote": "软件升级如果无法达成共识，会导致硬分叉，产生两条链。",
            "coase_theorem": "去中心化的代价是协调成本和集体行动难题。"
        },
        "key_lessons": [
            {
                "lesson": "没有最终仲裁者",
                "description": "传统公司有董事会，国家有最高法院。区块链没有。",
                "implication": "分歧可能永远无法解决，只能分家"
            },
            {
                "lesson": "代码即法律 vs 社区即法律",
                "description": "ETH/ETC 分叉的核心哲学争议",
                "implication": "需要预先定义在极端情况下如何决策"
            },
            {
                "lesson": "矿工 vs 开发者 vs 用户",
                "description": "三方利益不一定一致",
                "implication": "权力制衡很重要，但也增加协调难度"
            },
            {
                "lesson": "分叉是退出机制",
                "description": "与传统公司不同，不满者可以带走代码分叉",
                "implication": "这既是自由，也可能导致碎片化"
            }
        ],
        "investment_implications": {
            "fork_arbitrage": "分叉前持有可以获得两条链的代币",
            "governance_premium": "治理良好的项目应该享有估值溢价",
            "risk_discount": "频繁争议的项目应该折价"
        }
    }


if __name__ == "__main__":
    print("=" * 60)
    print("治理与硬分叉监控器")
    print("=" * 60)
    
    print("\n📜 历史硬分叉事件:")
    for fork in get_fork_history():
        print(f"\n  {fork['name']}")
        print(f"    {fork['original']} → {fork['fork']}")
        print(f"    日期: {fork['date']}")
        print(f"    教训: {fork['lesson'][:50]}...")
    
    print("\n" + "-" * 60)
    print("\n📊 风险分析示例:")
    
    risky_metrics = {
        "miner_signaling": 55,
        "community_sentiment": 60,
        "code_change_size": "large",
        "upgrade_timeline": 3
    }
    
    result = analyze_fork_risk(risky_metrics)
    print(f"  风险等级: {result['risk_level']}")
    print(f"  风险分数: {result['risk_score']}")
    for factor in result['risk_factors']:
        print(f"    {factor}")
