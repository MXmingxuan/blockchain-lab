"""
默克尔树计算器 (Merkle Tree Calculator)
将多笔交易压缩成单一根哈希
"""
import hashlib
from typing import List, Optional
from dataclasses import dataclass


def sha256_hash(data: str) -> str:
    """计算 SHA-256 哈希"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


@dataclass
class MerkleNode:
    """默克尔树节点"""
    hash: str
    data: Optional[str] = None
    left: Optional['MerkleNode'] = None
    right: Optional['MerkleNode'] = None
    
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


def build_merkle_tree(transactions: List[str]) -> Optional[MerkleNode]:
    """
    构建默克尔树
    输入：交易列表
    输出：默克尔树根节点
    """
    if not transactions:
        return None
    
    # 如果交易数量为奇数，复制最后一个
    if len(transactions) % 2 == 1:
        transactions = transactions + [transactions[-1]]
    
    # 创建叶子节点
    nodes = [
        MerkleNode(hash=sha256_hash(tx), data=tx)
        for tx in transactions
    ]
    
    # 递归构建树
    while len(nodes) > 1:
        next_level = []
        
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]
            
            # 合并两个节点的哈希
            combined_hash = sha256_hash(left.hash + right.hash)
            parent = MerkleNode(
                hash=combined_hash,
                left=left,
                right=right
            )
            next_level.append(parent)
        
        # 如果奇数个节点，复制最后一个
        if len(next_level) > 1 and len(next_level) % 2 == 1:
            next_level.append(next_level[-1])
        
        nodes = next_level
    
    return nodes[0] if nodes else None


def get_merkle_root(transactions: List[str]) -> str:
    """获取默克尔根哈希"""
    root = build_merkle_tree(transactions)
    return root.hash if root else ""


def visualize_tree(root: MerkleNode, level: int = 0, prefix: str = "Root: ") -> str:
    """可视化默克尔树"""
    if root is None:
        return ""
    
    lines = []
    
    if root.is_leaf():
        lines.append(f"{'  ' * level}{prefix}[{root.data}] -> {root.hash[:16]}...")
    else:
        lines.append(f"{'  ' * level}{prefix}{root.hash[:16]}...")
    
    if root.left:
        lines.append(visualize_tree(root.left, level + 1, "L: "))
    if root.right and root.right != root.left:
        lines.append(visualize_tree(root.right, level + 1, "R: "))
    
    return '\n'.join(lines)


def get_tree_structure(root: MerkleNode) -> dict:
    """将默克尔树转换为字典结构（用于JSON）"""
    if root is None:
        return {}
    
    result = {
        'hash': root.hash,
        'short_hash': root.hash[:16] + '...',
    }
    
    if root.is_leaf():
        result['data'] = root.data
        result['type'] = 'leaf'
    else:
        result['type'] = 'node'
        if root.left:
            result['left'] = get_tree_structure(root.left)
        if root.right and root.right != root.left:
            result['right'] = get_tree_structure(root.right)
    
    return result


def build_tree_levels(transactions: List[str]) -> List[List[dict]]:
    """构建树的层级结构（用于可视化）"""
    if not transactions:
        return []
    
    # 如果交易数量为奇数，复制最后一个
    if len(transactions) % 2 == 1:
        transactions = transactions + [transactions[-1]]
    
    levels = []
    
    # 第一层：叶子节点
    current_level = [
        {'hash': sha256_hash(tx), 'data': tx}
        for tx in transactions
    ]
    levels.append(current_level)
    
    # 构建上层
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else current_level[i]
            combined_hash = sha256_hash(left['hash'] + right['hash'])
            next_level.append({
                'hash': combined_hash,
                'left_child': left['hash'][:8],
                'right_child': right['hash'][:8]
            })
        
        if len(next_level) > 1 and len(next_level) % 2 == 1:
            next_level.append(next_level[-1])
        
        levels.append(next_level)
        current_level = next_level
    
    # 反转使根在顶部
    return levels[::-1]


if __name__ == '__main__':
    # 演示
    transactions = [
        "Alice -> Bob: 1 BTC",
        "Bob -> Charlie: 0.5 BTC",
        "Charlie -> David: 0.3 BTC",
        "David -> Eve: 0.1 BTC"
    ]
    
    root = build_merkle_tree(transactions)
    
    print("=" * 60)
    print("默克尔树 (Merkle Tree)")
    print("=" * 60)
    print(f"\n输入交易数: {len(transactions)}")
    print(f"默克尔根: {root.hash}")
    print("\n树结构:")
    print(visualize_tree(root))
