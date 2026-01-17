"""
PoW 工作量证明模拟器 (Proof of Work Simulator)
演示挖矿本质：寻找满足难度目标的 Nonce
"""
import hashlib
import time
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class MiningResult:
    """挖矿结果"""
    success: bool
    nonce: int
    hash: str
    attempts: int
    time_seconds: float
    difficulty: int
    data: str


def sha256_hash(data: str) -> str:
    """计算 SHA-256 哈希"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def check_hash_difficulty(hash_hex: str, difficulty: int) -> bool:
    """
    检查哈希是否满足难度目标
    difficulty: 前导零的数量（十六进制位）
    """
    return hash_hex.startswith('0' * difficulty)


def mine_block(data: str, difficulty: int = 4, max_attempts: int = 10000000) -> MiningResult:
    """
    挖矿：寻找满足难度目标的 Nonce
    
    参数:
        data: 区块数据（模拟区块头）
        difficulty: 难度（前导零个数，十六进制）
        max_attempts: 最大尝试次数
    
    返回:
        MiningResult 包含挖矿结果
    """
    start_time = time.time()
    nonce = 0
    
    while nonce < max_attempts:
        # 组合数据和 Nonce
        block_data = f"{data}{nonce}"
        block_hash = sha256_hash(block_data)
        
        # 检查是否满足难度
        if check_hash_difficulty(block_hash, difficulty):
            elapsed = time.time() - start_time
            return MiningResult(
                success=True,
                nonce=nonce,
                hash=block_hash,
                attempts=nonce + 1,
                time_seconds=round(elapsed, 4),
                difficulty=difficulty,
                data=data
            )
        
        nonce += 1
    
    # 达到最大尝试次数
    elapsed = time.time() - start_time
    return MiningResult(
        success=False,
        nonce=nonce,
        hash="",
        attempts=max_attempts,
        time_seconds=round(elapsed, 4),
        difficulty=difficulty,
        data=data
    )


def estimate_mining_time(difficulty: int, hash_rate: int = 100000) -> dict:
    """
    估算不同难度下的预期挖矿时间
    
    参数:
        difficulty: 难度（前导零个数）
        hash_rate: 每秒哈希次数
    
    返回:
        预期的尝试次数和时间
    """
    # 每增加一位前导零，难度增加 16 倍（十六进制）
    expected_attempts = 16 ** difficulty
    expected_seconds = expected_attempts / hash_rate
    
    return {
        'difficulty': difficulty,
        'expected_attempts': expected_attempts,
        'expected_seconds': round(expected_seconds, 2),
        'expected_human': format_time(expected_seconds),
        'hash_rate': hash_rate
    }


def format_time(seconds: float) -> str:
    """格式化时间显示"""
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f} 微秒"
    elif seconds < 1:
        return f"{seconds * 1000:.1f} 毫秒"
    elif seconds < 60:
        return f"{seconds:.2f} 秒"
    elif seconds < 3600:
        return f"{seconds / 60:.1f} 分钟"
    elif seconds < 86400:
        return f"{seconds / 3600:.1f} 小时"
    elif seconds < 86400 * 365:
        return f"{seconds / 86400:.1f} 天"
    else:
        return f"{seconds / (86400 * 365):.1f} 年"


def compare_difficulties(data: str, difficulties: list = [1, 2, 3, 4, 5]) -> list:
    """
    对比不同难度下的挖矿时间
    """
    results = []
    
    for diff in difficulties:
        # 设置合理的最大尝试次数
        max_attempts = min(16 ** (diff + 1), 50000000)
        
        result = mine_block(data, difficulty=diff, max_attempts=max_attempts)
        
        results.append({
            'difficulty': diff,
            'success': result.success,
            'attempts': result.attempts,
            'time_seconds': result.time_seconds,
            'nonce': result.nonce if result.success else None,
            'hash': result.hash[:16] + '...' if result.success else 'N/A'
        })
    
    return results


def visualize_mining(result: MiningResult) -> str:
    """可视化挖矿结果"""
    lines = [
        "=" * 60,
        "工作量证明挖矿结果 (Proof of Work Mining Result)",
        "=" * 60,
        f"区块数据: {result.data}",
        f"难度目标: {result.difficulty} 个前导零",
        "-" * 60,
    ]
    
    if result.success:
        lines.extend([
            f"✅ 挖矿成功！",
            f"找到的 Nonce: {result.nonce}",
            f"符合条件的哈希: {result.hash}",
            f"尝试次数: {result.attempts:,}",
            f"耗时: {result.time_seconds} 秒",
        ])
    else:
        lines.extend([
            f"❌ 未能在 {result.attempts:,} 次尝试内找到有效 Nonce",
            f"耗时: {result.time_seconds} 秒",
        ])
    
    lines.append("=" * 60)
    return '\n'.join(lines)


if __name__ == '__main__':
    # 演示
    print("演示 PoW 挖矿...")
    
    data = "Block #100 | PrevHash: abc123 | Tx: Alice->Bob 1 BTC"
    
    for difficulty in [1, 2, 3, 4]:
        result = mine_block(data, difficulty=difficulty, max_attempts=10000000)
        print(f"\n难度 {difficulty}: ", end="")
        if result.success:
            print(f"找到 Nonce={result.nonce}, 耗时 {result.time_seconds}s, 尝试 {result.attempts:,} 次")
        else:
            print(f"未找到 (尝试了 {result.attempts:,} 次)")
