"""
科斯定理投资分析器 (Coase Analyzer)
分析项目的中心化效率 vs 去中心化成本
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ProjectMetrics:
    """项目指标"""
    name: str
    category: str
    
    # 中心化收益指标
    single_point_of_failure: int  # 0-10, 10=严重单点故障
    monopoly_rent: int            # 0-10, 10=高垄断租金
    operational_efficiency: int   # 0-10, 10=高效率
    
    # 去中心化成本指标
    governance_chaos: int         # 0-10, 10=极度混乱
    upgrade_difficulty: int       # 0-10, 10=极难升级
    coordination_cost: int        # 0-10, 10=高协调成本
    
    # 实际去中心化程度
    actual_decentralization: int  # 0-10, 10=完全去中心化
    
    description: str


# 示例项目数据库
SAMPLE_PROJECTS = [
    ProjectMetrics(
        name="Bitcoin",
        category="货币/价值存储",
        single_point_of_failure=1,
        monopoly_rent=0,
        operational_efficiency=3,
        governance_chaos=6,
        upgrade_difficulty=9,
        coordination_cost=8,
        actual_decentralization=9,
        description="最去中心化的区块链，升级极其困难，但作为价值存储这正是优势"
    ),
    ProjectMetrics(
        name="Binance (BNB)",
        category="交易所代币",
        single_point_of_failure=9,
        monopoly_rent=8,
        operational_efficiency=9,
        governance_chaos=1,
        upgrade_difficulty=2,
        coordination_cost=1,
        actual_decentralization=2,
        description="中心化交易所代币，效率极高但存在单点故障风险"
    ),
    ProjectMetrics(
        name="Ethereum",
        category="智能合约平台",
        single_point_of_failure=3,
        monopoly_rent=2,
        operational_efficiency=5,
        governance_chaos=4,
        upgrade_difficulty=5,
        coordination_cost=5,
        actual_decentralization=7,
        description="较为平衡的项目，兼顾去中心化和可升级性"
    ),
    ProjectMetrics(
        name="Solana",
        category="高性能区块链",
        single_point_of_failure=5,
        monopoly_rent=3,
        operational_efficiency=9,
        governance_chaos=3,
        upgrade_difficulty=3,
        coordination_cost=3,
        actual_decentralization=5,
        description="牺牲部分去中心化换取高性能，验证者硬件要求高"
    ),
    ProjectMetrics(
        name="Uniswap",
        category="去中心化交易所",
        single_point_of_failure=2,
        monopoly_rent=1,
        operational_efficiency=6,
        governance_chaos=3,
        upgrade_difficulty=4,
        coordination_cost=4,
        actual_decentralization=7,
        description="DEX 的典型代表，用智能合约实现自动化做市"
    ),
    ProjectMetrics(
        name="Tether (USDT)",
        category="稳定币",
        single_point_of_failure=10,
        monopoly_rent=7,
        operational_efficiency=10,
        governance_chaos=1,
        upgrade_difficulty=1,
        coordination_cost=1,
        actual_decentralization=1,
        description="高度中心化的稳定币，依赖发行方的信用"
    )
]


def analyze_project(project_name: str) -> Dict:
    """
    分析单个项目
    
    基于科斯定理：
    - 当交易成本低时，市场（去中心化）更有效
    - 当交易成本高时，企业（中心化）更有效
    """
    project = next((p for p in SAMPLE_PROJECTS if p.name.lower() == project_name.lower()), None)
    
    if not project:
        return {
            "found": False,
            "error": f"未找到项目: {project_name}",
            "available": [p.name for p in SAMPLE_PROJECTS]
        }
    
    # 计算中心化收益
    centralization_benefit = (
        project.operational_efficiency * 0.4 +
        (10 - project.governance_chaos) * 0.3 +
        (10 - project.upgrade_difficulty) * 0.3
    )
    
    # 计算中心化风险
    centralization_risk = (
        project.single_point_of_failure * 0.5 +
        project.monopoly_rent * 0.5
    )
    
    # 计算去中心化成本
    decentralization_cost = (
        project.governance_chaos * 0.3 +
        project.upgrade_difficulty * 0.3 +
        project.coordination_cost * 0.4
    )
    
    # 计算科斯边界位置
    # 如果 centralization_benefit > decentralization_cost，则偏向中心化更有效
    coase_score = centralization_benefit - decentralization_cost
    
    # 评估
    if coase_score > 3:
        coase_verdict = "中心化可能更高效"
        color = "warning"
    elif coase_score < -3:
        coase_verdict = "去中心化有明确优势"
        color = "success"
    else:
        coase_verdict = "边界区域，取决于具体用例"
        color = "info"
    
    # 匹配度检查
    expected_decentralization = 5 - (coase_score / 2)  # 简化模型
    decentralization_mismatch = abs(project.actual_decentralization - expected_decentralization)
    
    if project.actual_decentralization < 4 and coase_score < -2:
        mismatch_warning = "⚠️ 项目声称需要去中心化，但实际高度中心化"
    elif project.actual_decentralization > 6 and coase_score > 2:
        mismatch_warning = "⚠️ 项目可能过度去中心化，牺牲了效率"
    else:
        mismatch_warning = "✅ 去中心化程度与用例相匹配"
    
    return {
        "found": True,
        "project": {
            "name": project.name,
            "category": project.category,
            "description": project.description
        },
        "metrics": {
            "centralization_benefit": round(centralization_benefit, 1),
            "centralization_risk": round(centralization_risk, 1),
            "decentralization_cost": round(decentralization_cost, 1),
            "actual_decentralization": project.actual_decentralization
        },
        "analysis": {
            "coase_score": round(coase_score, 1),
            "coase_verdict": coase_verdict,
            "verdict_color": color,
            "mismatch_warning": mismatch_warning
        },
        "raw_scores": {
            "single_point_of_failure": project.single_point_of_failure,
            "monopoly_rent": project.monopoly_rent,
            "operational_efficiency": project.operational_efficiency,
            "governance_chaos": project.governance_chaos,
            "upgrade_difficulty": project.upgrade_difficulty,
            "coordination_cost": project.coordination_cost
        }
    }


def get_sample_projects() -> List[Dict]:
    """获取所有示例项目"""
    results = []
    for p in SAMPLE_PROJECTS:
        analysis = analyze_project(p.name)
        results.append({
            "name": p.name,
            "category": p.category,
            "actual_decentralization": p.actual_decentralization,
            "coase_score": analysis["analysis"]["coase_score"],
            "verdict": analysis["analysis"]["coase_verdict"],
            "description": p.description[:60] + "..."
        })
    return results


def calculate_coase_boundary() -> Dict:
    """
    解释科斯边界的概念
    """
    return {
        "theorem": {
            "title": "科斯定理 (Coase Theorem)",
            "statement": "在交易成本为零的情况下，资源配置将达到最优，无论初始产权如何分配。",
            "implication": "企业（中心化）存在的原因是为了降低市场交易成本。"
        },
        "application_to_crypto": {
            "question": "什么决定了一个应用应该去中心化还是中心化？",
            "answer": "取决于协调成本（去中心化）vs 信任成本（中心化）的权衡",
            "examples": [
                {
                    "use_case": "货币/价值存储",
                    "optimal": "高度去中心化",
                    "reason": "信任成本极高（无人愿意信任单一机构发货币）"
                },
                {
                    "use_case": "高频交易",
                    "optimal": "可接受部分中心化",
                    "reason": "协调成本太高，需要快速决策"
                },
                {
                    "use_case": "身份认证",
                    "optimal": "混合模式",
                    "reason": "需要某种可信锚点，但不希望单点控制"
                }
            ]
        },
        "investment_framework": {
            "red_flags": [
                "项目声称去中心化，但实际由少数人控制",
                "用例本身适合中心化，但强行使用区块链",
                "治理极其混乱，无法有效升级"
            ],
            "green_flags": [
                "去中心化程度与用例需求匹配",
                "有效的治理机制（但不失去去中心化本质）",
                "清晰的价值主张（为什么需要区块链）"
            ]
        }
    }


if __name__ == "__main__":
    print("=" * 60)
    print("科斯定理投资分析器")
    print("=" * 60)
    
    print("\n📊 项目分析:")
    for project in get_sample_projects():
        print(f"\n  {project['name']} ({project['category']})")
        print(f"    去中心化: {project['actual_decentralization']}/10")
        print(f"    科斯分数: {project['coase_score']:.1f}")
        print(f"    评估: {project['verdict']}")
    
    print("\n" + "-" * 60)
    
    # 详细分析一个项目
    result = analyze_project("Binance (BNB)")
    if result["found"]:
        print(f"\n🔍 详细分析: {result['project']['name']}")
        print(f"  {result['analysis']['mismatch_warning']}")
        print(f"  中心化收益: {result['metrics']['centralization_benefit']}")
        print(f"  中心化风险: {result['metrics']['centralization_risk']}")
        print(f"  去中心化成本: {result['metrics']['decentralization_cost']}")
