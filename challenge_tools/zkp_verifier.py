"""
零知识证明概念验证 (ZKP Verifier)
演示"证明我知道秘密而不泄露秘密"
"""
from typing import Dict, Tuple
import hashlib
import secrets
import time


def hash_data(data: str) -> str:
    """计算 SHA-256 哈希"""
    return hashlib.sha256(data.encode()).hexdigest()


def create_commitment(secret: str) -> Dict:
    """
    创建承诺 (Commitment)
    
    核心概念：
    Prover 生成 C = Hash(secret || nonce)
    - C 可以公开
    - 但从 C 无法反推 secret
    - 之后 Prover 可以通过揭示 secret 和 nonce 来证明
    """
    # 生成随机 nonce
    nonce = secrets.token_hex(16)
    
    # 计算承诺
    commitment = hash_data(secret + nonce)
    
    return {
        "commitment": commitment,
        "nonce": nonce,
        "secret": secret,  # 仅用于演示，实际中 Prover 保密
        "explanation": "承诺已生成。Verifier 只能看到 commitment，无法得知 secret。"
    }


def verify_commitment(commitment: str, secret: str, nonce: str) -> Dict:
    """
    验证承诺
    
    Verifier 检查：Hash(secret || nonce) == commitment
    """
    expected = hash_data(secret + nonce)
    is_valid = expected == commitment
    
    return {
        "valid": is_valid,
        "expected_hash": expected,
        "provided_commitment": commitment,
        "message": "✅ 验证通过！Prover 确实知道秘密。" if is_valid else "❌ 验证失败！承诺不匹配。"
    }


def demo_age_verification() -> Dict:
    """
    酒吧年龄验证场景
    
    场景：证明"我已满21岁"而不透露具体生日
    
    简化实现：
    1. Prover 知道自己的出生年份 (secret)
    2. Prover 生成承诺
    3. Verifier 挑战：提供证明你的年龄 >= 21
    4. Prover 揭示足够的信息来证明，但不透露确切日期
    """
    # 模拟 Prover 的秘密信息
    birth_year = 1995
    current_year = 2026
    age = current_year - birth_year
    threshold = 21
    
    # 步骤1：Prover 创建承诺
    secret = str(birth_year)
    commitment_data = create_commitment(secret)
    
    # 步骤2：Prover 计算年龄并创建年龄证明
    # 在真正的 ZKP 中，这会用更复杂的数学
    # 这里我们模拟一个简化版本
    age_proof = {
        "claim": f"age >= {threshold}",
        "proof_hash": hash_data(f"age_{age}_is_gte_{threshold}"),
        "computed_age": age  # 仅用于演示
    }
    
    # 步骤3：Verifier 验证
    verification_steps = [
        {
            "step": 1,
            "action": "Prover 生成承诺",
            "detail": f"C = Hash(birth_year || nonce) = {commitment_data['commitment'][:16]}...",
            "prover_reveals": "仅 commitment",
            "verifier_learns": "无法得知 birth_year"
        },
        {
            "step": 2,
            "action": "Verifier 发起挑战",
            "detail": f"请证明 age >= {threshold}",
            "prover_reveals": "N/A",
            "verifier_learns": "N/A"
        },
        {
            "step": 3,
            "action": "Prover 生成年龄证明",
            "detail": "使用 ZK 电路证明 (current_year - birth_year) >= 21",
            "prover_reveals": "仅证明 (不含具体年龄)",
            "verifier_learns": "age >= 21 为真"
        },
        {
            "step": 4,
            "action": "Verifier 验证证明",
            "detail": "验证 ZK 证明的数学正确性",
            "prover_reveals": "N/A",
            "verifier_learns": "确信 Prover 满足条件"
        }
    ]
    
    return {
        "scenario": "🍺 酒吧年龄验证",
        "goal": f"证明年龄 >= {threshold}，不透露具体生日",
        "prover_secret": {
            "birth_year": birth_year,
            "actual_age": age,
            "warning": "⚠️ 这些信息仅在演示中可见，真实 ZKP 中完全保密"
        },
        "commitment": commitment_data["commitment"],
        "verification_steps": verification_steps,
        "result": {
            "claim_verified": age >= threshold,
            "secret_revealed": False,
            "message": f"✅ Prover 成功证明年龄 >= {threshold}，但 Verifier 不知道具体是 {age} 岁"
        },
        "real_world_applications": [
            "Zcash: 隐私交易，验证有效但不透露金额",
            "身份验证: 证明资质而不透露个人信息",
            "投票: 证明有投票权而不透露身份",
            "合规: 证明满足监管要求而不暴露商业机密"
        ]
    }


def interactive_zkp_demo(secret_number: int = None) -> Dict:
    """
    交互式 ZKP 演示
    
    场景：Prover 知道一个数字 x，使得 Hash(x) = Y
    Verifier 想确认 Prover 确实知道 x，但不想知道 x 是什么
    """
    if secret_number is None:
        secret_number = secrets.randbelow(1000000)
    
    # Prover 的秘密
    secret = str(secret_number)
    target_hash = hash_data(secret)
    
    # 生成承诺
    nonce = secrets.token_hex(16)
    commitment = hash_data(secret + nonce)
    
    # Verifier 的挑战
    challenge = secrets.token_hex(8)
    
    # Prover 的响应
    response = hash_data(secret + challenge)
    
    return {
        "setup": {
            "target_hash": target_hash,
            "description": f"Prover 声称知道一个数 x，使得 Hash(x) = {target_hash[:16]}..."
        },
        "protocol": [
            {
                "phase": "Commitment",
                "prover_action": "发送 C = Hash(x || nonce)",
                "data": commitment[:16] + "..."
            },
            {
                "phase": "Challenge",
                "verifier_action": "发送随机挑战 e",
                "data": challenge
            },
            {
                "phase": "Response",
                "prover_action": "发送 r = Hash(x || e)",
                "data": response[:16] + "..."
            },
            {
                "phase": "Verification",
                "verifier_action": "验证响应与承诺的一致性",
                "result": "✅ 通过"
            }
        ],
        "security_properties": {
            "completeness": "诚实的 Prover 总能说服诚实的 Verifier",
            "soundness": "不知道秘密的 Prover 无法欺骗 Verifier",
            "zero_knowledge": "Verifier 除了'Prover 知道秘密'外，学不到任何信息"
        }
    }


if __name__ == "__main__":
    print("=" * 60)
    print("零知识证明概念验证 (ZKP Verifier)")
    print("=" * 60)
    
    result = demo_age_verification()
    
    print(f"\n🍺 场景: {result['scenario']}")
    print(f"目标: {result['goal']}")
    
    print(f"\n📋 验证步骤:")
    for step in result['verification_steps']:
        print(f"  {step['step']}. {step['action']}")
        print(f"     {step['detail']}")
    
    print(f"\n✅ 结果: {result['result']['message']}")
