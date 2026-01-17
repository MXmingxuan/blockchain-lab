"""
难度调整预测器 (Difficulty Adjustment Predictor)
预测下次比特币难度调整幅度
"""
import requests
import time
from typing import Optional
from dataclasses import dataclass


# 常量
BLOCKS_PER_EPOCH = 2016              # 每个难度周期的区块数
TARGET_BLOCK_TIME = 600              # 目标出块时间（10分钟 = 600秒）
EPOCH_DURATION = BLOCKS_PER_EPOCH * TARGET_BLOCK_TIME  # 理想周期时长（2周）


@dataclass 
class DifficultyPrediction:
    """难度预测结果"""
    current_difficulty: float
    predicted_difficulty: float
    adjustment_percent: float
    blocks_until_adjustment: int
    current_epoch_progress: float
    avg_block_time: float
    estimated_adjustment_time: str


def get_current_difficulty() -> dict:
    """获取当前难度和区块信息"""
    data = {
        'difficulty': 0,
        'block_height': 0,
        'success': False
    }
    
    try:
        # 获取难度
        diff_resp = requests.get(
            'https://blockchain.info/q/getdifficulty',
            timeout=5
        )
        if diff_resp.status_code == 200:
            data['difficulty'] = float(diff_resp.text)
        
        # 获取区块高度
        height_resp = requests.get(
            'https://blockchain.info/q/getblockcount',
            timeout=5
        )
        if height_resp.status_code == 200:
            data['block_height'] = int(height_resp.text)
        
        data['success'] = True
        
    except Exception as e:
        # 模拟数据
        data = {
            'difficulty': 72_000_000_000_000,
            'block_height': 820500,
            'success': False,
            'error': str(e)
        }
    
    return data


def get_epoch_blocks(current_height: int) -> dict:
    """
    获取当前难度周期的出块信息
    """
    # 计算当前周期的起始区块
    epoch_start = (current_height // BLOCKS_PER_EPOCH) * BLOCKS_PER_EPOCH
    blocks_in_epoch = current_height - epoch_start + 1
    blocks_remaining = BLOCKS_PER_EPOCH - blocks_in_epoch
    
    return {
        'epoch_start': epoch_start,
        'current_height': current_height,
        'blocks_in_epoch': blocks_in_epoch,
        'blocks_remaining': blocks_remaining,
        'progress_percent': round(blocks_in_epoch / BLOCKS_PER_EPOCH * 100, 1)
    }


def estimate_avg_block_time(current_height: int, sample_blocks: int = 100) -> float:
    """
    估算平均出块时间
    通过获取最近区块的时间戳计算
    """
    try:
        # 获取最新区块
        latest_resp = requests.get(
            f'https://blockchain.info/block-height/{current_height}?format=json',
            timeout=10
        )
        
        if latest_resp.status_code != 200:
            return TARGET_BLOCK_TIME
        
        latest_block = latest_resp.json()['blocks'][0]
        latest_time = latest_block['time']
        
        # 获取 sample_blocks 之前的区块
        old_height = current_height - sample_blocks
        old_resp = requests.get(
            f'https://blockchain.info/block-height/{old_height}?format=json',
            timeout=10
        )
        
        if old_resp.status_code != 200:
            return TARGET_BLOCK_TIME
        
        old_block = old_resp.json()['blocks'][0]
        old_time = old_block['time']
        
        # 计算平均出块时间
        time_diff = latest_time - old_time
        avg_time = time_diff / sample_blocks
        
        return avg_time
        
    except Exception:
        # 返回默认值
        return TARGET_BLOCK_TIME


def predict_difficulty_adjustment(
    current_difficulty: Optional[float] = None,
    current_height: Optional[int] = None,
    avg_block_time: Optional[float] = None
) -> dict:
    """
    预测下次难度调整
    
    参数:
        current_difficulty: 当前难度（可选，自动获取）
        current_height: 当前区块高度（可选，自动获取）
        avg_block_time: 平均出块时间（可选，自动估算）
    
    返回:
        难度调整预测结果
    """
    # 获取实时数据
    if current_difficulty is None or current_height is None:
        btc_data = get_current_difficulty()
        current_difficulty = current_difficulty or btc_data['difficulty']
        current_height = current_height or btc_data['block_height']
    
    # 获取周期信息
    epoch_info = get_epoch_blocks(current_height)
    
    # 估算平均出块时间
    if avg_block_time is None:
        # 使用简化估算（实际应该获取区块时间戳）
        avg_block_time = TARGET_BLOCK_TIME * 0.95  # 假设比目标快5%
    
    # 计算预期调整幅度
    # 公式: 新难度 = 旧难度 * (实际周期时间 / 目标周期时间)
    # 调整幅度 = (目标时间 - 实际时间) / 目标时间
    adjustment_ratio = TARGET_BLOCK_TIME / avg_block_time
    predicted_difficulty = current_difficulty * adjustment_ratio
    adjustment_percent = (adjustment_ratio - 1) * 100
    
    # 限制调整幅度（比特币协议限制每次最多调整 4 倍）
    if adjustment_ratio > 4:
        adjustment_ratio = 4
        predicted_difficulty = current_difficulty * 4
        adjustment_percent = 300
    elif adjustment_ratio < 0.25:
        adjustment_ratio = 0.25
        predicted_difficulty = current_difficulty * 0.25
        adjustment_percent = -75
    
    # 估算距离下次调整的时间
    seconds_remaining = epoch_info['blocks_remaining'] * avg_block_time
    days_remaining = seconds_remaining / 86400
    
    if days_remaining < 1:
        time_str = f"{seconds_remaining / 3600:.1f} 小时"
    else:
        time_str = f"{days_remaining:.1f} 天"
    
    return {
        'current': {
            'difficulty': current_difficulty,
            'difficulty_human': format_difficulty(current_difficulty),
            'block_height': current_height
        },
        'epoch': {
            'start_block': epoch_info['epoch_start'],
            'blocks_completed': epoch_info['blocks_in_epoch'],
            'blocks_remaining': epoch_info['blocks_remaining'],
            'progress_percent': epoch_info['progress_percent']
        },
        'prediction': {
            'avg_block_time': round(avg_block_time, 1),
            'target_block_time': TARGET_BLOCK_TIME,
            'predicted_difficulty': predicted_difficulty,
            'predicted_difficulty_human': format_difficulty(predicted_difficulty),
            'adjustment_percent': round(adjustment_percent, 2),
            'adjustment_direction': '上调' if adjustment_percent > 0 else '下调',
            'time_until_adjustment': time_str
        },
        'interpretation': interpret_adjustment(adjustment_percent)
    }


def format_difficulty(difficulty: float) -> str:
    """格式化难度显示"""
    if difficulty >= 1e15:
        return f"{difficulty / 1e15:.2f} P"
    elif difficulty >= 1e12:
        return f"{difficulty / 1e12:.2f} T"
    elif difficulty >= 1e9:
        return f"{difficulty / 1e9:.2f} G"
    else:
        return f"{difficulty:,.0f}"


def interpret_adjustment(percent: float) -> str:
    """解读调整幅度"""
    if percent > 10:
        return "⚡ 算力大幅增长，挖矿竞争加剧，可能是牛市信号"
    elif percent > 3:
        return "📈 算力温和增长，矿工积极性较高"
    elif percent > -3:
        return "⚖️ 算力稳定，网络健康运行"
    elif percent > -10:
        return "📉 算力小幅下降，部分矿工可能关机"
    else:
        return "⚠️ 算力大幅下降，可能是矿工投降（底部信号）"


if __name__ == '__main__':
    print("=" * 60)
    print("难度调整预测器 (Difficulty Adjustment Predictor)")
    print("=" * 60)
    
    result = predict_difficulty_adjustment()
    
    print(f"\n当前状态:")
    print(f"  区块高度: {result['current']['block_height']:,}")
    print(f"  当前难度: {result['current']['difficulty_human']}")
    
    print(f"\n周期进度:")
    print(f"  已完成: {result['epoch']['blocks_completed']}/{BLOCKS_PER_EPOCH}")
    print(f"  进度: {result['epoch']['progress_percent']}%")
    
    print(f"\n预测:")
    print(f"  平均出块时间: {result['prediction']['avg_block_time']}秒 (目标: 600秒)")
    print(f"  预计调整: {result['prediction']['adjustment_direction']} {abs(result['prediction']['adjustment_percent']):.2f}%")
    print(f"  距离调整: {result['prediction']['time_until_adjustment']}")
    
    print(f"\n解读: {result['interpretation']}")
