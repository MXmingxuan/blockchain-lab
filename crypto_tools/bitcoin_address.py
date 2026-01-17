"""
比特币地址生成器 (Bitcoin Address Generator)
完整还原比特币地址生成流程
"""
import hashlib
import os
from typing import Tuple

try:
    from ecdsa import SigningKey, SECP256k1
    ECDSA_AVAILABLE = True
except ImportError:
    ECDSA_AVAILABLE = False


# Base58 字符集（不含 0, O, I, l 避免混淆）
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def base58_encode(data: bytes) -> str:
    """Base58 编码"""
    # 计算前导零字节数
    leading_zeros = len(data) - len(data.lstrip(b'\x00'))
    
    # 转换为整数
    num = int.from_bytes(data, 'big')
    
    # 编码
    result = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        result = BASE58_ALPHABET[remainder] + result
    
    # 添加前导 1（对应前导零字节）
    return '1' * leading_zeros + result


def generate_private_key() -> bytes:
    """生成随机私钥（32字节）"""
    return os.urandom(32)


def private_key_to_public_key(private_key: bytes) -> bytes:
    """
    从私钥推导公钥
    使用 SECP256k1 椭圆曲线
    """
    if not ECDSA_AVAILABLE:
        raise ImportError("请安装 ecdsa 库: pip install ecdsa")
    
    sk = SigningKey.from_string(private_key, curve=SECP256k1)
    vk = sk.get_verifying_key()
    
    # 返回非压缩格式公钥（04 + x + y）
    return b'\x04' + vk.to_string()


def public_key_to_address(public_key: bytes, version: int = 0x00) -> dict:
    """
    从公钥生成比特币地址
    步骤：
    1. SHA-256 哈希公钥
    2. RIPEMD-160 哈希
    3. 添加版本字节
    4. 双重 SHA-256 计算校验和
    5. Base58Check 编码
    """
    steps = {}
    
    # 步骤 1: SHA-256
    sha256_hash = hashlib.sha256(public_key).digest()
    steps['sha256'] = sha256_hash.hex()
    
    # 步骤 2: RIPEMD-160
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    ripemd160_hash = ripemd160.digest()
    steps['ripemd160'] = ripemd160_hash.hex()
    
    # 步骤 3: 添加版本字节
    versioned = bytes([version]) + ripemd160_hash
    steps['versioned'] = versioned.hex()
    
    # 步骤 4: 双重 SHA-256 计算校验和
    checksum_full = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()
    checksum = checksum_full[:4]
    steps['checksum'] = checksum.hex()
    
    # 步骤 5: 拼接并 Base58 编码
    address_bytes = versioned + checksum
    steps['address_bytes'] = address_bytes.hex()
    
    address = base58_encode(address_bytes)
    steps['address'] = address
    
    return steps


def generate_bitcoin_address() -> dict:
    """
    完整生成比特币地址流程
    返回每一步的中间结果
    """
    if not ECDSA_AVAILABLE:
        return {'error': '请先安装 ecdsa 库: pip install ecdsa'}
    
    result = {
        'success': True,
        'steps': []
    }
    
    # 步骤 1: 生成私钥
    private_key = generate_private_key()
    result['private_key'] = private_key.hex()
    result['steps'].append({
        'step': 1,
        'name': '生成私钥',
        'output': private_key.hex(),
        'description': '生成 256 位随机数作为私钥'
    })
    
    # 步骤 2: 推导公钥
    public_key = private_key_to_public_key(private_key)
    result['public_key'] = public_key.hex()
    result['steps'].append({
        'step': 2,
        'name': '推导公钥',
        'output': public_key.hex(),
        'description': '使用 SECP256k1 椭圆曲线从私钥推导公钥'
    })
    
    # 步骤 3-7: 生成地址
    address_steps = public_key_to_address(public_key)
    
    result['steps'].append({
        'step': 3,
        'name': 'SHA-256 哈希',
        'output': address_steps['sha256'],
        'description': '对公钥进行 SHA-256 哈希'
    })
    
    result['steps'].append({
        'step': 4,
        'name': 'RIPEMD-160 哈希',
        'output': address_steps['ripemd160'],
        'description': '对 SHA-256 结果进行 RIPEMD-160 哈希'
    })
    
    result['steps'].append({
        'step': 5,
        'name': '添加版本字节',
        'output': address_steps['versioned'],
        'description': '添加 0x00 版本前缀（主网地址）'
    })
    
    result['steps'].append({
        'step': 6,
        'name': '计算校验和',
        'output': address_steps['checksum'],
        'description': '双重 SHA-256 后取前 4 字节作为校验和'
    })
    
    result['steps'].append({
        'step': 7,
        'name': 'Base58 编码',
        'output': address_steps['address'],
        'description': 'Base58Check 编码生成最终地址'
    })
    
    result['address'] = address_steps['address']
    
    return result


def visualize_generation() -> str:
    """可视化地址生成过程"""
    result = generate_bitcoin_address()
    
    if 'error' in result:
        return result['error']
    
    lines = [
        "=" * 70,
        "比特币地址生成流程 (Bitcoin Address Generation)",
        "=" * 70
    ]
    
    for step in result['steps']:
        lines.append(f"\n步骤 {step['step']}: {step['name']}")
        lines.append(f"  说明: {step['description']}")
        
        output = step['output']
        if len(output) > 64:
            lines.append(f"  输出: {output[:64]}...")
        else:
            lines.append(f"  输出: {output}")
    
    lines.append("\n" + "=" * 70)
    lines.append(f"最终比特币地址: {result['address']}")
    lines.append("=" * 70)
    
    return '\n'.join(lines)


if __name__ == '__main__':
    if not ECDSA_AVAILABLE:
        print("请先安装 ecdsa 库: pip install ecdsa")
    else:
        print(visualize_generation())
