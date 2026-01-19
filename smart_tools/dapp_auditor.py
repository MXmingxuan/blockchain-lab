"""
DApp 活跃度分析仪 (DApp Activity Auditor)
识别"空城计"项目，分析真实用户活跃度
"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DAppData:
    """DApp 数据"""
    name: str
    category: str
    market_cap: float  # 百万美元
    daily_users: int   # 日活跃用户
    daily_transactions: int  # 日交易数
    token_volume: float  # 日交易量（百万美元）
    contract_calls: int  # 日合约调用数
    description: str


# 模拟历史和当前 DApp 数据
SAMPLE_DAPPS = [
    DAppData(
        name="CryptoKitties",
        category="NFT/收藏品",
        market_cap=50.0,
        daily_users=350,
        daily_transactions=1200,
        token_volume=0.5,
        contract_calls=2400,
        description="2017年爆火的加密猫游戏，曾导致以太坊网络拥堵"
    ),
    DAppData(
        name="FomoGame",
        category="赌博/游戏",
        market_cap=120.0,
        daily_users=1500,
        daily_transactions=8500,
        token_volume=15.0,
        contract_calls=12000,
        description="典型的庞氏游戏，高交易量的赌博应用"
    ),
    DAppData(
        name="HypeToken",
        category="DeFi",
        market_cap=500.0,
        daily_users=200,
        daily_transactions=50000,
        token_volume=80.0,
        contract_calls=500,
        description="代币交易量巨大但实际用户极少的项目"
    ),
    DAppData(
        name="RealYield",
        category="DeFi",
        market_cap=80.0,
        daily_users=5000,
        daily_transactions=15000,
        token_volume=10.0,
        contract_calls=25000,
        description="真实收益协议，用户活跃且合约调用频繁"
    ),
    DAppData(
        name="GhostSwap",
        category="DEX",
        market_cap=300.0,
        daily_users=50,
        daily_transactions=200,
        token_volume=100.0,
        contract_calls=100,
        description="交易量巨大但几乎没有真实用户"
    ),
    DAppData(
        name="SocialFi",
        category="社交",
        market_cap=25.0,
        daily_users=8000,
        daily_transactions=20000,
        token_volume=0.2,
        contract_calls=30000,
        description="社交应用，高用户活跃但市值较低"
    ),
]


def calculate_health_score(dapp: DAppData) -> Dict:
    """
    计算 DApp 健康度评分
    
    关键指标：
    1. 市值/日活用户 (越低越好)
    2. 合约调用/交易量比率 (越高说明真实使用越多)
    3. 用户/交易量比率 (越高说明用户越真实)
    """
    # 市值每用户 (单位：美元)
    cap_per_user = (dapp.market_cap * 1_000_000) / max(dapp.daily_users, 1)
    
    # 合约使用率
    contract_usage_ratio = dapp.contract_calls / max(dapp.daily_transactions, 1)
    
    # 用户真实度指标
    user_tx_ratio = dapp.daily_users / max(dapp.daily_transactions / 100, 1)
    
    # 综合评分 (0-100)
    score = 50  # 基础分
    
    # 市值/用户：< $10000 好，> $100000 差
    if cap_per_user < 10000:
        score += 20
    elif cap_per_user > 100000:
        score -= 20
    elif cap_per_user > 500000:
        score -= 30
    
    # 合约使用率：> 1 好（真实使用），< 0.1 差
    if contract_usage_ratio > 1:
        score += 15
    elif contract_usage_ratio < 0.1:
        score -= 15
    
    # 用户/交易比
    if user_tx_ratio > 5:
        score += 15
    elif user_tx_ratio < 0.5:
        score -= 15
    
    # 限制在 0-100
    score = max(0, min(100, score))
    
    # 风险等级
    if score >= 70:
        risk_level = "🟢 健康"
        risk_description = "用户活跃度与市值相匹配，真实使用场景"
    elif score >= 50:
        risk_level = "🟡 关注"
        risk_description = "部分指标异常，需要进一步调查"
    elif score >= 30:
        risk_level = "🟠 警告"
        risk_description = "可能存在刷量或过度投机"
    else:
        risk_level = "🔴 高风险"
        risk_description = "极可能是'空城计'：代币炒作但无真实用户"
    
    # 具体警告
    warnings = []
    if cap_per_user > 500000:
        warnings.append(f"⚠️ 市值/用户比过高 (${cap_per_user:,.0f}/用户)")
    if contract_usage_ratio < 0.1:
        warnings.append("⚠️ 合约调用率极低，可能只是代币交易")
    if dapp.token_volume > dapp.market_cap * 0.5 and dapp.daily_users < 500:
        warnings.append("⚠️ 高交易量低用户数，可能存在刷量")
    
    return {
        "name": dapp.name,
        "category": dapp.category,
        "score": score,
        "risk_level": risk_level,
        "risk_description": risk_description,
        "metrics": {
            "market_cap": f"${dapp.market_cap}M",
            "daily_users": f"{dapp.daily_users:,}",
            "cap_per_user": f"${cap_per_user:,.0f}",
            "contract_usage_ratio": f"{contract_usage_ratio:.2f}",
            "token_volume": f"${dapp.token_volume}M"
        },
        "warnings": warnings
    }


def analyze_dapp(dapp_name: str) -> Dict:
    """分析指定 DApp"""
    dapp = next((d for d in SAMPLE_DAPPS if d.name.lower() == dapp_name.lower()), None)
    
    if not dapp:
        return {
            "found": False,
            "error": f"未找到 DApp: {dapp_name}"
        }
    
    return {
        "found": True,
        "analysis": calculate_health_score(dapp),
        "raw_data": {
            "name": dapp.name,
            "category": dapp.category,
            "market_cap": dapp.market_cap,
            "daily_users": dapp.daily_users,
            "daily_transactions": dapp.daily_transactions,
            "token_volume": dapp.token_volume,
            "contract_calls": dapp.contract_calls,
            "description": dapp.description
        }
    }


def get_sample_dapps() -> List[Dict]:
    """获取所有示例 DApp 及其评分"""
    results = []
    for dapp in SAMPLE_DAPPS:
        analysis = calculate_health_score(dapp)
        results.append({
            "name": dapp.name,
            "category": dapp.category,
            "score": analysis["score"],
            "risk_level": analysis["risk_level"],
            "market_cap": f"${dapp.market_cap}M",
            "daily_users": dapp.daily_users,
            "description": dapp.description
        })
    
    # 按评分排序
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def get_investment_insights() -> Dict:
    """获取投资洞察"""
    return {
        "gensler_warning": {
            "title": "Gensler 教授的警告",
            "quote": "最活跃的 DApp 日活仅 1500 人，但市值却高达数十亿美元",
            "lesson": "关注真实用户数，而非代币价格或交易量"
        },
        "key_metrics": [
            {
                "name": "市值/日活用户比",
                "description": "每个活跃用户对应的市值",
                "healthy_range": "< $50,000",
                "warning_sign": "> $500,000"
            },
            {
                "name": "合约调用/交易量",
                "description": "真实使用 vs 纯代币交易",
                "healthy_range": "> 1.0",
                "warning_sign": "< 0.1"
            },
            {
                "name": "用户增长 vs 价格增长",
                "description": "用户增长应与价格增长匹配",
                "healthy_range": "同步增长",
                "warning_sign": "价格暴涨但用户不增"
            }
        ],
        "red_flags": [
            "代币频繁交易但合约几乎无调用",
            "高市值但社区讨论冷清",
            "团队匿名且无法验证技术能力",
            "白皮书充斥 buzzwords 但无具体实现"
        ]
    }


if __name__ == "__main__":
    print("=" * 60)
    print("DApp 活跃度分析仪 (DApp Activity Auditor)")
    print("=" * 60)
    
    print("\n📊 示例 DApp 健康度排名:")
    print("-" * 50)
    
    for dapp in get_sample_dapps():
        print(f"{dapp['risk_level']} {dapp['name']:<15} | 评分: {dapp['score']:>3} | 日活: {dapp['daily_users']:>6} | 市值: {dapp['market_cap']}")
    
    print("\n" + "-" * 50)
    print("🔍 详细分析: HypeToken")
    
    result = analyze_dapp("HypeToken")
    if result["found"]:
        analysis = result["analysis"]
        print(f"  评分: {analysis['score']}")
        print(f"  风险: {analysis['risk_level']}")
        print(f"  说明: {analysis['risk_description']}")
        if analysis["warnings"]:
            print("  警告:")
            for w in analysis["warnings"]:
                print(f"    {w}")
