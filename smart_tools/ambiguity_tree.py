"""
法律模糊性决策树 (Ambiguity Visualizer)
展示代码精确性与法律模糊性的冲突
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class DecisionNode:
    """决策树节点"""
    condition: str
    true_branch: Optional['DecisionNode'] = None
    false_branch: Optional['DecisionNode'] = None
    action: Optional[str] = None
    probability: str = ""  # 发生概率


# 预定义的合约场景及其边缘案例
CONTRACT_SCENARIOS = {
    "buy_house": {
        "name": "🏠 房屋买卖合约",
        "base_logic": "IF 买方支付全款 THEN 卖方转让房产",
        "edge_cases": [
            {"condition": "房屋在交易期间着火", "probability": "0.1%", "complexity": 3},
            {"condition": "卖方在签约后去世", "probability": "0.01%", "complexity": 4},
            {"condition": "发现房屋有隐藏的法律纠纷", "probability": "1%", "complexity": 5},
            {"condition": "银行贷款审批延迟", "probability": "10%", "complexity": 2},
            {"condition": "房屋检查发现重大缺陷", "probability": "5%", "complexity": 3},
            {"condition": "买方失业无法支付", "probability": "3%", "complexity": 2},
            {"condition": "自然灾害导致房屋损毁", "probability": "0.05%", "complexity": 4},
            {"condition": "政府征地", "probability": "0.5%", "complexity": 5},
            {"condition": "邻居提出边界纠纷", "probability": "2%", "complexity": 3},
            {"condition": "卖方反悔", "probability": "5%", "complexity": 2},
        ]
    },
    "flight_insurance": {
        "name": "✈️ 航班延误保险",
        "base_logic": "IF 航班延误 > 60分钟 THEN 自动赔付",
        "edge_cases": [
            {"condition": "航班取消后重新安排", "probability": "5%", "complexity": 2},
            {"condition": "延误原因是乘客自身", "probability": "1%", "complexity": 3},
            {"condition": "航空公司破产", "probability": "0.01%", "complexity": 5},
            {"condition": "天气原因反复延误", "probability": "3%", "complexity": 3},
            {"condition": "航班编号变更", "probability": "2%", "complexity": 2},
            {"condition": "预言机数据延迟", "probability": "1%", "complexity": 4},
            {"condition": "多段航班部分延误", "probability": "8%", "complexity": 3},
            {"condition": "机场关闭", "probability": "0.5%", "complexity": 4},
        ]
    },
    "nft_sale": {
        "name": "🎨 NFT 销售合约",
        "base_logic": "IF 买方支付 ETH THEN 转移 NFT 所有权",
        "edge_cases": [
            {"condition": "NFT 被证明是抄袭作品", "probability": "5%", "complexity": 4},
            {"condition": "原创作者要求版税", "probability": "10%", "complexity": 3},
            {"condition": "智能合约被黑客攻击", "probability": "1%", "complexity": 5},
            {"condition": "Gas 费用超过 NFT 价值", "probability": "3%", "complexity": 2},
            {"condition": "买方地址输入错误", "probability": "0.5%", "complexity": 3},
            {"condition": "区块链网络拥堵", "probability": "5%", "complexity": 2},
            {"condition": "卖方私钥丢失", "probability": "0.1%", "complexity": 5},
        ]
    },
    "rental": {
        "name": "🏢 租赁合约",
        "base_logic": "IF 租户每月支付租金 THEN 保留居住权",
        "edge_cases": [
            {"condition": "房屋需要紧急维修", "probability": "10%", "complexity": 2},
            {"condition": "租户转租给他人", "probability": "5%", "complexity": 3},
            {"condition": "房东出售房产", "probability": "3%", "complexity": 4},
            {"condition": "租户收入中断", "probability": "8%", "complexity": 2},
            {"condition": "邻居投诉噪音", "probability": "15%", "complexity": 2},
            {"condition": "宠物问题", "probability": "10%", "complexity": 2},
            {"condition": "租户擅自装修", "probability": "5%", "complexity": 3},
            {"condition": "疫情导致无法支付", "probability": "1%", "complexity": 4},
            {"condition": "房屋发现安全隐患", "probability": "2%", "complexity": 3},
        ]
    }
}


def generate_decision_tree(scenario_id: str, max_depth: int = 3) -> Dict:
    """
    生成决策树
    展示处理所有边缘案例需要多少条件判断
    """
    if scenario_id not in CONTRACT_SCENARIOS:
        return {
            "error": f"场景不存在: {scenario_id}",
            "available": list(CONTRACT_SCENARIOS.keys())
        }
    
    scenario = CONTRACT_SCENARIOS[scenario_id]
    edge_cases = scenario["edge_cases"]
    
    # 构建树形结构（简化为列表形式便于前端渲染）
    tree_nodes = []
    
    # 根节点
    tree_nodes.append({
        "level": 0,
        "id": "root",
        "type": "condition",
        "content": scenario["base_logic"],
        "children": ["e1", "success"]
    })
    
    tree_nodes.append({
        "level": 1,
        "id": "success",
        "type": "action",
        "content": "✅ 执行合约",
        "children": []
    })
    
    # 添加边缘案例节点
    for i, edge in enumerate(edge_cases[:max_depth * 3]):  # 限制显示数量
        level = (i // 2) + 1
        node_id = f"e{i+1}"
        
        tree_nodes.append({
            "level": level,
            "id": node_id,
            "type": "edge_case",
            "content": f"如果 {edge['condition']}？",
            "probability": edge["probability"],
            "complexity": edge["complexity"],
            "children": [f"e{i+2}"] if i < len(edge_cases) - 1 else []
        })
    
    # 统计
    total_conditions = len(edge_cases)
    total_complexity = sum(e["complexity"] for e in edge_cases)
    low_prob_cases = sum(1 for e in edge_cases if float(e["probability"].rstrip("%")) < 1)
    
    return {
        "scenario": {
            "id": scenario_id,
            "name": scenario["name"],
            "base_logic": scenario["base_logic"]
        },
        "tree": tree_nodes,
        "statistics": {
            "total_edge_cases": total_conditions,
            "total_complexity": total_complexity,
            "low_probability_cases": low_prob_cases,
            "estimated_code_lines": total_conditions * 10,  # 估计代码行数
            "impossibility_note": f"要穷尽所有边缘案例，需要 {total_conditions * 5} 以上的条件判断"
        },
        "lessig_insight": {
            "title": "Lessig 教授的洞见",
            "quote": "法律允许模糊性以降低谈判成本，但代码要求绝对精确。",
            "explanation": f"这个 '{scenario['name']}' 看似简单，但要用代码覆盖所有情况，需要处理 {total_conditions} 个边缘案例。"
        }
    }


def get_contract_scenarios() -> List[Dict]:
    """获取所有合约场景"""
    return [
        {
            "id": key,
            "name": val["name"],
            "base_logic": val["base_logic"],
            "edge_case_count": len(val["edge_cases"])
        }
        for key, val in CONTRACT_SCENARIOS.items()
    ]


def count_edge_cases(scenario_id: str) -> Dict:
    """统计边缘案例"""
    if scenario_id not in CONTRACT_SCENARIOS:
        return {"error": "场景不存在"}
    
    scenario = CONTRACT_SCENARIOS[scenario_id]
    edge_cases = scenario["edge_cases"]
    
    # 按复杂度分组
    by_complexity = {}
    for e in edge_cases:
        c = e["complexity"]
        if c not in by_complexity:
            by_complexity[c] = []
        by_complexity[c].append(e["condition"])
    
    # 按概率分组
    high_prob = [e for e in edge_cases if float(e["probability"].rstrip("%")) >= 5]
    medium_prob = [e for e in edge_cases if 1 <= float(e["probability"].rstrip("%")) < 5]
    low_prob = [e for e in edge_cases if float(e["probability"].rstrip("%")) < 1]
    
    return {
        "scenario": scenario["name"],
        "total": len(edge_cases),
        "by_complexity": {
            k: {"count": len(v), "examples": v[:2]}
            for k, v in sorted(by_complexity.items())
        },
        "by_probability": {
            "high (>=5%)": [e["condition"] for e in high_prob],
            "medium (1-5%)": [e["condition"] for e in medium_prob],
            "low (<1%)": [e["condition"] for e in low_prob]
        },
        "conclusion": {
            "problem": "法律可以说'按合理方式处理'，但代码必须为每种情况写明确处理逻辑",
            "why_smart_contracts_limited": "这就是为什么智能合约目前主要用于简单、参数清晰的场景"
        }
    }


def visualize_tree_ascii(scenario_id: str) -> str:
    """生成 ASCII 决策树"""
    result = generate_decision_tree(scenario_id, max_depth=2)
    
    if "error" in result:
        return f"错误: {result['error']}"
    
    lines = []
    lines.append(f"┌─ {result['scenario']['name']}")
    lines.append(f"│  基础逻辑: {result['scenario']['base_logic']}")
    lines.append("│")
    lines.append("├─ 边缘案例:")
    
    scenario = CONTRACT_SCENARIOS[scenario_id]
    for i, edge in enumerate(scenario["edge_cases"][:6]):
        prefix = "│  ├─" if i < 5 else "│  └─"
        lines.append(f"{prefix} [{edge['probability']}] {edge['condition']}")
    
    if len(scenario["edge_cases"]) > 6:
        lines.append(f"│     ... 还有 {len(scenario['edge_cases']) - 6} 个边缘案例")
    
    lines.append("│")
    stats = result["statistics"]
    lines.append(f"└─ 统计: {stats['total_edge_cases']} 个边缘案例, 估计需要 {stats['estimated_code_lines']}+ 行代码")
    
    return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 60)
    print("法律模糊性决策树 (Ambiguity Visualizer)")
    print("=" * 60)
    
    print("\n📋 可用场景:")
    for s in get_contract_scenarios():
        print(f"  • {s['name']} ({s['edge_case_count']} 个边缘案例)")
    
    print("\n" + "-" * 60)
    print(visualize_tree_ascii("buy_house"))
    
    print("\n" + "-" * 60)
    print("\n💡 核心洞见:")
    result = generate_decision_tree("buy_house")
    print(f"  {result['lessig_insight']['quote']}")
    print(f"  {result['lessig_insight']['explanation']}")
