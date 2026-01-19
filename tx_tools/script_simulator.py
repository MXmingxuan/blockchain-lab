"""
堆栈脚本模拟器 (Stack-based Script Simulator)
模拟比特币脚本的执行过程
"""
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ExecutionStep:
    """执行步骤记录"""
    step_num: int
    operation: str
    stack_before: List[str]
    stack_after: List[str]
    description: str


class StackMachine:
    """
    比特币脚本堆栈机模拟器
    """
    
    def __init__(self):
        self.stack: List[bytes] = []
        self.execution_trace: List[Dict] = []
        self.step_count = 0
    
    def reset(self):
        """重置堆栈机"""
        self.stack = []
        self.execution_trace = []
        self.step_count = 0
    
    def push(self, data: bytes):
        """压入数据"""
        self.stack.append(data)
    
    def pop(self) -> Optional[bytes]:
        """弹出数据"""
        if self.stack:
            return self.stack.pop()
        return None
    
    def peek(self) -> Optional[bytes]:
        """查看栈顶"""
        if self.stack:
            return self.stack[-1]
        return None
    
    def get_stack_display(self) -> List[str]:
        """获取堆栈显示（十六进制缩写）"""
        result = []
        for item in self.stack:
            if len(item) > 8:
                result.append(item[:4].hex() + '...' + item[-4:].hex())
            else:
                result.append(item.hex())
        return result
    
    def record_step(self, operation: str, description: str, stack_before: List[str], stack_after: List[str]):
        """记录执行步骤"""
        self.step_count += 1
        self.execution_trace.append({
            'step': self.step_count,
            'operation': operation,
            'description': description,
            'stack_before': stack_before.copy(),
            'stack_after': stack_after.copy()
        })
    
    def op_dup(self) -> bool:
        """OP_DUP: 复制栈顶元素"""
        stack_before = self.get_stack_display()
        
        if not self.stack:
            return False
        top = self.peek()
        self.push(top)
        
        self.record_step(
            'OP_DUP',
            '复制栈顶元素',
            stack_before,
            self.get_stack_display()
        )
        return True
    
    def op_hash160(self) -> bool:
        """OP_HASH160: SHA256 + RIPEMD160"""
        stack_before = self.get_stack_display()
        
        if not self.stack:
            return False
        
        data = self.pop()
        # SHA256 然后 RIPEMD160
        sha256_hash = hashlib.sha256(data).digest()
        ripemd160 = hashlib.new('ripemd160', sha256_hash).digest()
        self.push(ripemd160)
        
        self.record_step(
            'OP_HASH160',
            'SHA256 + RIPEMD160 哈希',
            stack_before,
            self.get_stack_display()
        )
        return True
    
    def op_equal(self) -> bool:
        """OP_EQUAL: 比较栈顶两个元素"""
        stack_before = self.get_stack_display()
        
        if len(self.stack) < 2:
            return False
        
        a = self.pop()
        b = self.pop()
        result = b'\x01' if a == b else b'\x00'
        self.push(result)
        
        self.record_step(
            'OP_EQUAL',
            f'比较两个元素: {"相等 ✓" if a == b else "不等 ✗"}',
            stack_before,
            self.get_stack_display()
        )
        return True
    
    def op_equalverify(self) -> bool:
        """OP_EQUALVERIFY: 比较并验证"""
        stack_before = self.get_stack_display()
        
        if len(self.stack) < 2:
            return False
        
        a = self.pop()
        b = self.pop()
        equal = a == b
        
        self.record_step(
            'OP_EQUALVERIFY',
            f'验证相等: {"通过 ✓" if equal else "失败 ✗"}',
            stack_before,
            self.get_stack_display()
        )
        return equal
    
    def op_verify(self) -> bool:
        """OP_VERIFY: 验证栈顶为真"""
        stack_before = self.get_stack_display()
        
        if not self.stack:
            return False
        
        top = self.pop()
        is_true = top != b'\x00' and len(top) > 0
        
        self.record_step(
            'OP_VERIFY',
            f'验证栈顶: {"真 ✓" if is_true else "假 ✗"}',
            stack_before,
            self.get_stack_display()
        )
        return is_true
    
    def op_checksig(self, valid: bool = True) -> bool:
        """
        OP_CHECKSIG: 验证签名
        注：这里模拟验证，实际需要 ECDSA 验证
        """
        stack_before = self.get_stack_display()
        
        if len(self.stack) < 2:
            return False
        
        pubkey = self.pop()
        signature = self.pop()
        
        # 模拟签名验证（实际需要 ECDSA）
        result = b'\x01' if valid else b'\x00'
        self.push(result)
        
        self.record_step(
            'OP_CHECKSIG',
            f'验证签名: {"有效 ✓" if valid else "无效 ✗"}',
            stack_before,
            self.get_stack_display()
        )
        return True
    
    def get_result(self) -> bool:
        """获取脚本执行结果"""
        if not self.stack:
            return False
        top = self.peek()
        return top != b'\x00' and len(top) > 0


def run_p2pkh_script(signature: bytes, pubkey: bytes, pubkey_hash: bytes, valid_sig: bool = True) -> Dict:
    """
    运行 P2PKH 脚本
    
    完整脚本: <sig> <pubkey> OP_DUP OP_HASH160 <pubkeyhash> OP_EQUALVERIFY OP_CHECKSIG
    """
    machine = StackMachine()
    
    # 解锁脚本 (ScriptSig)
    stack_before = machine.get_stack_display()
    machine.push(signature)
    machine.record_step('PUSH', '压入签名', stack_before, machine.get_stack_display())
    
    stack_before = machine.get_stack_display()
    machine.push(pubkey)
    machine.record_step('PUSH', '压入公钥', stack_before, machine.get_stack_display())
    
    # 锁定脚本 (ScriptPubKey)
    if not machine.op_dup():
        return {'success': False, 'error': 'OP_DUP 失败', 'trace': machine.execution_trace}
    
    if not machine.op_hash160():
        return {'success': False, 'error': 'OP_HASH160 失败', 'trace': machine.execution_trace}
    
    stack_before = machine.get_stack_display()
    machine.push(pubkey_hash)
    machine.record_step('PUSH', '压入公钥哈希', stack_before, machine.get_stack_display())
    
    if not machine.op_equalverify():
        return {'success': False, 'error': 'OP_EQUALVERIFY 失败：公钥哈希不匹配', 'trace': machine.execution_trace}
    
    if not machine.op_checksig(valid_sig):
        return {'success': False, 'error': 'OP_CHECKSIG 失败', 'trace': machine.execution_trace}
    
    result = machine.get_result()
    
    return {
        'success': result,
        'final_stack': machine.get_stack_display(),
        'trace': machine.execution_trace,
        'total_steps': machine.step_count
    }


def demo_p2pkh_execution() -> Dict:
    """
    演示 P2PKH 脚本执行
    """
    # 模拟数据
    signature = b'\x30\x44\x02\x20' + b'\x11' * 32 + b'\x02\x20' + b'\x22' * 32
    pubkey = b'\x04' + b'\xaa' * 64  # 未压缩公钥
    
    # 计算公钥哈希
    sha256_hash = hashlib.sha256(pubkey).digest()
    pubkey_hash = hashlib.new('ripemd160', sha256_hash).digest()
    
    return {
        'script_type': 'P2PKH',
        'script_description': '支付给公钥哈希 (Pay to Public Key Hash)',
        'unlocking_script': '<Signature> <PublicKey>',
        'locking_script': 'OP_DUP OP_HASH160 <PubKeyHash> OP_EQUALVERIFY OP_CHECKSIG',
        'execution': run_p2pkh_script(signature, pubkey, pubkey_hash, valid_sig=True)
    }


def get_opcode_reference() -> List[Dict]:
    """
    获取支持的操作码参考
    """
    return [
        {'opcode': 'OP_DUP', 'hex': '0x76', 'description': '复制栈顶元素'},
        {'opcode': 'OP_HASH160', 'hex': '0xa9', 'description': 'SHA256 + RIPEMD160'},
        {'opcode': 'OP_EQUAL', 'hex': '0x87', 'description': '比较两个元素，返回 0/1'},
        {'opcode': 'OP_EQUALVERIFY', 'hex': '0x88', 'description': '比较并验证，失败则终止'},
        {'opcode': 'OP_VERIFY', 'hex': '0x69', 'description': '验证栈顶为真'},
        {'opcode': 'OP_CHECKSIG', 'hex': '0xac', 'description': '验证 ECDSA 签名'},
    ]


if __name__ == '__main__':
    print("=" * 60)
    print("堆栈脚本模拟器 (Script Simulator)")
    print("=" * 60)
    
    demo = demo_p2pkh_execution()
    
    print(f"\n脚本类型: {demo['script_type']}")
    print(f"描述: {demo['script_description']}")
    print(f"\n解锁脚本: {demo['unlocking_script']}")
    print(f"锁定脚本: {demo['locking_script']}")
    
    print("\n" + "-" * 60)
    print("执行过程:")
    
    for step in demo['execution']['trace']:
        print(f"\n  步骤 {step['step']}: {step['operation']}")
        print(f"    {step['description']}")
        print(f"    堆栈: [{', '.join(step['stack_after']) or '空'}]")
    
    print("\n" + "-" * 60)
    result = demo['execution']
    print(f"执行结果: {'✅ 成功' if result['success'] else '❌ 失败'}")
    print(f"最终堆栈: [{', '.join(result['final_stack'])}]")
