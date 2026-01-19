"""
不可能三角模拟器 (Trilemma Simulator)
演示区块链的去中心化/安全性/扩展性三难困境
"""
from typing import Dict
from dataclasses import dataclass
import math


@dataclass
class TrilemmaParams:
    """三难困境参数"""
    block_size_kb: int = 1000        # 区块大小 (KB)
    block_time_seconds: int = 600    # 出块时间 (秒)
    node_count: int = 10000          # 全节点数量
    avg_tx_size_bytes: int = 250     # 平均交易大小 (字节)
    network_latency_ms: int = 200    # 网络传播延迟 (毫秒)
    min_hardware_cost_usd: int = 500 # 运行全节点的最低硬件成本


def simulate_trilemma(params: TrilemmaParams = None) -> Dict:
    """
    模拟区块链不可能三角
    
    核心逻辑：
    1. 扩展性 (TPS) 与区块大小/出块时间正相关
    2. 去中心化与节点数量/硬件门槛相关
    3. 安全性与分叉风险/51%攻击成本相关
    """
    if params is None:
        params = TrilemmaParams()
    
    # ===== 扩展性计算 =====
    # TPS = 区块容量 / 平均交易大小 / 出块时间
    block_capacity_bytes = params.block_size_kb * 1024
    txs_per_block = block_capacity_bytes / params.avg_tx_size_bytes
    tps = txs_per_block / params.block_time_seconds
    
    # 与传统系统对比
    visa_tps = 24000
    scalability_ratio = tps / visa_tps
    
    # ===== 去中心化计算 =====
    # 大区块需要更多带宽和存储，减少能运行节点的人
    bandwidth_requirement_mbps = (params.block_size_kb * 8) / params.block_time_seconds
    storage_per_year_gb = (params.block_size_kb * (365 * 24 * 3600 / params.block_time_seconds)) / (1024 * 1024)
    
    # 硬件门槛评分 (0-100, 越高越去中心化)
    if bandwidth_requirement_mbps < 1:
        bandwidth_score = 100
    elif bandwidth_requirement_mbps < 10:
        bandwidth_score = 80
    elif bandwidth_requirement_mbps < 100:
        bandwidth_score = 50
    else:
        bandwidth_score = 20
    
    # 节点数量评分
    if params.node_count > 10000:
        node_score = 100
    elif params.node_count > 1000:
        node_score = 70
    elif params.node_count > 100:
        node_score = 40
    else:
        node_score = 10
    
    decentralization_score = (bandwidth_score + node_score) / 2
    
    # ===== 安全性计算 =====
    # 分叉风险：出块时间短 + 区块大 = 更多孤块
    propagation_time_ms = params.block_size_kb * 0.1  # 简化模型：每KB 0.1ms
    total_latency_ms = params.network_latency_ms + propagation_time_ms
    
    # 孤块率估算
    orphan_probability = min(0.5, total_latency_ms / (params.block_time_seconds * 1000))
    
    # 51%攻击成本与节点数量相关
    attack_difficulty_score = min(100, params.node_count / 100)
    
    security_score = 100 - (orphan_probability * 100) + (attack_difficulty_score * 0.3)
    security_score = max(0, min(100, security_score))
    
    # ===== 综合评估 =====
    # 检测不平衡
    scores = [scalability_ratio * 100, decentralization_score, security_score]
    balance = 100 - (max(scores) - min(scores))  # 越平衡越好
    
    return {
        "params": {
            "block_size_kb": params.block_size_kb,
            "block_time_seconds": params.block_time_seconds,
            "node_count": params.node_count
        },
        "scalability": {
            "tps": round(tps, 2),
            "txs_per_block": int(txs_per_block),
            "visa_comparison": f"{scalability_ratio * 100:.2f}%",
            "score": min(100, scalability_ratio * 100)
        },
        "decentralization": {
            "bandwidth_required_mbps": round(bandwidth_requirement_mbps, 2),
            "storage_per_year_gb": round(storage_per_year_gb, 1),
            "node_count": params.node_count,
            "score": round(decentralization_score, 1)
        },
        "security": {
            "orphan_probability": f"{orphan_probability * 100:.2f}%",
            "propagation_time_ms": round(total_latency_ms, 1),
            "score": round(security_score, 1)
        },
        "balance_score": round(balance, 1),
        "trade_off_warning": get_trade_off_warning(params)
    }


def get_trade_off_warning(params: TrilemmaParams) -> str:
    """生成权衡警告"""
    warnings = []
    
    if params.block_size_kb > 8000:
        warnings.append("⚠️ 超大区块会导致网络分区风险增加，小节点被挤出")
    
    if params.block_time_seconds < 10:
        warnings.append("⚠️ 极短出块时间会产生大量孤块，降低安全性")
    
    if params.node_count < 100:
        warnings.append("⚠️ 节点数量过少，容易被少数实体控制")
    
    if not warnings:
        return "✅ 当前参数较为平衡"
    
    return " ".join(warnings)


def get_trilemma_explanation() -> Dict:
    """获取不可能三角解释"""
    return {
        "title": "区块链不可能三角 (Vitalik's Trilemma)",
        "description": "区块链很难同时实现去中心化、安全性和扩展性三个目标。",
        "vertices": {
            "decentralization": {
                "name": "去中心化",
                "description": "任何人都能运行节点、验证交易",
                "trade_off": "需要保持低硬件门槛，限制区块大小"
            },
            "security": {
                "name": "安全性",
                "description": "抵抗攻击、防止双花和分叉",
                "trade_off": "需要足够的出块时间让网络同步"
            },
            "scalability": {
                "name": "扩展性",
                "description": "处理大量交易，接近Visa级别TPS",
                "trade_off": "需要更大区块或更快出块"
            }
        },
        "examples": [
            {"name": "Bitcoin", "focus": "去中心化 + 安全性", "sacrifice": "扩展性 (~7 TPS)"},
            {"name": "Solana", "focus": "扩展性 + 安全性", "sacrifice": "去中心化 (高硬件要求)"},
            {"name": "BSC", "focus": "扩展性", "sacrifice": "去中心化 (少数验证者)"}
        ]
    }


if __name__ == "__main__":
    print("=" * 60)
    print("不可能三角模拟器 (Trilemma Simulator)")
    print("=" * 60)
    
    # 比特币参数
    btc_params = TrilemmaParams(
        block_size_kb=1000,
        block_time_seconds=600,
        node_count=15000
    )
    
    result = simulate_trilemma(btc_params)
    
    print(f"\n📊 比特币模拟结果:")
    print(f"  TPS: {result['scalability']['tps']}")
    print(f"  去中心化评分: {result['decentralization']['score']}")
    print(f"  安全性评分: {result['security']['score']}")
    print(f"  {result['trade_off_warning']}")
