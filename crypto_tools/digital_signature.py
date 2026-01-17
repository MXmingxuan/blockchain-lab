"""
数字签名模拟器 (Digital Signature Simulator)
演示 ECDSA 非对称加密签名与验证
"""
import hashlib
from typing import Tuple, Optional

try:
    from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
    ECDSA_AVAILABLE = True
except ImportError:
    ECDSA_AVAILABLE = False


def check_ecdsa() -> bool:
    """检查 ecdsa 库是否可用"""
    return ECDSA_AVAILABLE


def generate_keypair() -> dict:
    """
    生成 ECDSA 密钥对（使用比特币相同的 SECP256k1 曲线）
    返回：私钥和公钥（十六进制格式）
    """
    if not ECDSA_AVAILABLE:
        return {'error': '请先安装 ecdsa 库: pip install ecdsa'}
    
    # 生成私钥
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.get_verifying_key()
    
    return {
        'private_key': private_key.to_string().hex(),
        'public_key': public_key.to_string().hex(),
        'private_key_obj': private_key,
        'public_key_obj': public_key
    }


def sign_message(message: str, private_key_hex: str) -> dict:
    """
    用私钥签名消息
    """
    if not ECDSA_AVAILABLE:
        return {'error': '请先安装 ecdsa 库: pip install ecdsa'}
    
    try:
        # 将十六进制私钥转换回对象
        private_key = SigningKey.from_string(
            bytes.fromhex(private_key_hex), 
            curve=SECP256k1
        )
        
        # 对消息进行哈希
        message_hash = hashlib.sha256(message.encode('utf-8')).digest()
        
        # 签名
        signature = private_key.sign(message_hash)
        
        return {
            'message': message,
            'message_hash': message_hash.hex(),
            'signature': signature.hex(),
            'success': True
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def verify_signature(message: str, signature_hex: str, public_key_hex: str) -> dict:
    """
    用公钥验证签名
    """
    if not ECDSA_AVAILABLE:
        return {'error': '请先安装 ecdsa 库: pip install ecdsa'}
    
    try:
        # 将十六进制公钥转换回对象
        public_key = VerifyingKey.from_string(
            bytes.fromhex(public_key_hex),
            curve=SECP256k1
        )
        
        # 对消息进行哈希
        message_hash = hashlib.sha256(message.encode('utf-8')).digest()
        
        # 将十六进制签名转换回字节
        signature = bytes.fromhex(signature_hex)
        
        # 验证
        is_valid = public_key.verify(signature, message_hash)
        
        return {
            'message': message,
            'valid': is_valid,
            'success': True
        }
    except BadSignatureError:
        return {
            'message': message,
            'valid': False,
            'success': True,
            'reason': '签名无效'
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def demo_signature_flow() -> dict:
    """完整的签名演示流程"""
    if not ECDSA_AVAILABLE:
        return {'error': '请先安装 ecdsa 库: pip install ecdsa'}
    
    results = {
        'steps': []
    }
    
    # 步骤1: 生成密钥对
    keypair = generate_keypair()
    results['keypair'] = {
        'private_key': keypair['private_key'],
        'public_key': keypair['public_key']
    }
    results['steps'].append({
        'step': 1,
        'action': '生成密钥对',
        'result': '成功'
    })
    
    # 步骤2: 签名消息
    message = "Alice pays Bob 1 BTC"
    sign_result = sign_message(message, keypair['private_key'])
    results['signature'] = sign_result
    results['steps'].append({
        'step': 2,
        'action': f'签名消息: "{message}"',
        'result': '成功' if sign_result.get('success') else '失败'
    })
    
    # 步骤3: 验证签名（正确公钥）
    verify_result = verify_signature(
        message, 
        sign_result['signature'], 
        keypair['public_key']
    )
    results['verify_correct'] = verify_result
    results['steps'].append({
        'step': 3,
        'action': '用正确公钥验证',
        'result': '验证通过' if verify_result.get('valid') else '验证失败'
    })
    
    # 步骤4: 验证签名（错误公钥）
    wrong_keypair = generate_keypair()
    verify_wrong = verify_signature(
        message,
        sign_result['signature'],
        wrong_keypair['public_key']
    )
    results['verify_wrong_key'] = verify_wrong
    results['steps'].append({
        'step': 4,
        'action': '用错误公钥验证',
        'result': '验证通过' if verify_wrong.get('valid') else '验证失败（预期）'
    })
    
    # 步骤5: 验证签名（篡改消息）
    tampered_message = "Alice pays Bob 100 BTC"
    verify_tampered = verify_signature(
        tampered_message,
        sign_result['signature'],
        keypair['public_key']
    )
    results['verify_tampered'] = verify_tampered
    results['steps'].append({
        'step': 5,
        'action': f'验证篡改消息: "{tampered_message}"',
        'result': '验证通过' if verify_tampered.get('valid') else '验证失败（预期）'
    })
    
    return results


if __name__ == '__main__':
    if not ECDSA_AVAILABLE:
        print("请先安装 ecdsa 库: pip install ecdsa")
    else:
        print("=" * 60)
        print("数字签名演示 (Digital Signature Demo)")
        print("=" * 60)
        
        results = demo_signature_flow()
        
        print(f"\n私钥: {results['keypair']['private_key'][:32]}...")
        print(f"公钥: {results['keypair']['public_key'][:32]}...")
        
        print("\n步骤:")
        for step in results['steps']:
            print(f"  {step['step']}. {step['action']} -> {step['result']}")
