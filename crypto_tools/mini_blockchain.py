"""
迷你区块链构建器 (Mini-Blockchain Builder)
演示区块如何通过哈希指针链接，以及篡改检测
"""
import hashlib
import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Block:
    """区块类"""
    index: int
    timestamp: float
    data: str
    previous_hash: str
    nonce: int = 0
    hash: str = field(default="", init=False)
    
    def __post_init__(self):
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """计算区块哈希"""
        content = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }


class Blockchain:
    """区块链类"""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.create_genesis_block()
    
    def create_genesis_block(self) -> Block:
        """创建创世区块"""
        genesis = Block(
            index=0,
            timestamp=time.time(),
            data="Genesis Block - 创世区块",
            previous_hash="0" * 64
        )
        self.chain.append(genesis)
        return genesis
    
    def get_latest_block(self) -> Block:
        """获取最新区块"""
        return self.chain[-1]
    
    def add_block(self, data: str) -> Block:
        """添加新区块"""
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=data,
            previous_hash=self.get_latest_block().hash
        )
        self.chain.append(new_block)
        return new_block
    
    def is_chain_valid(self) -> dict:
        """验证区块链完整性"""
        result = {
            'valid': True,
            'errors': [],
            'checked_blocks': len(self.chain)
        }
        
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # 检查当前区块哈希是否正确
            if current.hash != current.calculate_hash():
                result['valid'] = False
                result['errors'].append(f"区块 {i}: 哈希不匹配（数据可能被篡改）")
            
            # 检查哈希指针是否正确链接
            if current.previous_hash != previous.hash:
                result['valid'] = False
                result['errors'].append(f"区块 {i}: 前块哈希不匹配（链断裂）")
        
        return result
    
    def tamper_block(self, index: int, new_data: str) -> dict:
        """
        模拟篡改区块（不重新计算哈希）
        用于演示篡改检测
        """
        if index < 0 or index >= len(self.chain):
            return {'success': False, 'error': '无效的区块索引'}
        
        old_data = self.chain[index].data
        self.chain[index].data = new_data
        # 故意不重新计算哈希，模拟篡改
        
        return {
            'success': True,
            'block_index': index,
            'old_data': old_data,
            'new_data': new_data,
            'message': '数据已修改，但哈希未更新（模拟篡改）'
        }
    
    def get_chain_data(self) -> List[dict]:
        """获取整个链的数据"""
        return [block.to_dict() for block in self.chain]
    
    def visualize(self) -> str:
        """可视化区块链"""
        lines = ["=" * 70, "区块链可视化", "=" * 70]
        
        for i, block in enumerate(self.chain):
            lines.append(f"\n┌{'─' * 68}┐")
            lines.append(f"│ 区块 #{block.index:<60} │")
            lines.append(f"├{'─' * 68}┤")
            lines.append(f"│ 时间戳: {block.timestamp:<57} │")
            lines.append(f"│ 数据: {block.data[:58]:<60} │")
            lines.append(f"│ 前块哈希: {block.previous_hash[:54]}... │")
            lines.append(f"│ 当前哈希: {block.hash[:54]}... │")
            lines.append(f"│ Nonce: {block.nonce:<59} │")
            lines.append(f"└{'─' * 68}┘")
            
            if i < len(self.chain) - 1:
                lines.append("           │")
                lines.append("           ▼")
        
        return '\n'.join(lines)


if __name__ == '__main__':
    # 演示
    bc = Blockchain()
    bc.add_block("Alice pays Bob 1 BTC")
    bc.add_block("Bob pays Charlie 0.5 BTC")
    bc.add_block("Charlie pays David 0.3 BTC")
    
    print(bc.visualize())
    print("\n验证区块链:", bc.is_chain_valid())
    
    print("\n--- 尝试篡改区块 1 ---")
    bc.tamper_block(1, "Alice pays Bob 100 BTC")
    print("篡改后验证:", bc.is_chain_valid())
