"""
雪崩效应演示器 (Avalanche Effect Visualizer)
展示哈希函数的雪崩效应：输入微小变化导致输出巨大差异
"""
import hashlib


def sha256_hash(data: str) -> str:
    """计算字符串的 SHA-256 哈希值"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def hex_to_binary(hex_str: str) -> str:
    """将十六进制字符串转换为二进制字符串"""
    return bin(int(hex_str, 16))[2:].zfill(256)


def compare_hashes(str_a: str, str_b: str) -> dict:
    """
    比较两个字符串的哈希值
    返回：哈希值、二进制表示、差异位数等信息
    """
    hash_a = sha256_hash(str_a)
    hash_b = sha256_hash(str_b)
    
    bin_a = hex_to_binary(hash_a)
    bin_b = hex_to_binary(hash_b)
    
    # 计算翻转的位数
    flipped_bits = sum(a != b for a, b in zip(bin_a, bin_b))
    flip_percentage = (flipped_bits / 256) * 100
    
    # 生成差异可视化
    diff_visual = ''.join('█' if a != b else '░' for a, b in zip(bin_a, bin_b))
    
    return {
        'input_a': str_a,
        'input_b': str_b,
        'hash_a': hash_a,
        'hash_b': hash_b,
        'binary_a': bin_a,
        'binary_b': bin_b,
        'flipped_bits': flipped_bits,
        'total_bits': 256,
        'flip_percentage': round(flip_percentage, 2),
        'diff_visual': diff_visual
    }


def visualize_bit_diff(result: dict) -> str:
    """生成位差异的文本可视化"""
    lines = [
        "=" * 60,
        "雪崩效应分析 (Avalanche Effect Analysis)",
        "=" * 60,
        f"输入 A: \"{result['input_a']}\"",
        f"输入 B: \"{result['input_b']}\"",
        "-" * 60,
        f"哈希 A: {result['hash_a']}",
        f"哈希 B: {result['hash_b']}",
        "-" * 60,
        f"翻转位数: {result['flipped_bits']} / {result['total_bits']} ({result['flip_percentage']}%)",
        "-" * 60,
        "位差异可视化 (█=不同, ░=相同):",
        result['diff_visual'][:64],
        result['diff_visual'][64:128],
        result['diff_visual'][128:192],
        result['diff_visual'][192:256],
        "=" * 60
    ]
    return '\n'.join(lines)


if __name__ == '__main__':
    # 演示
    result = compare_hashes("Hello World", "Hello world")
    print(visualize_bit_diff(result))
