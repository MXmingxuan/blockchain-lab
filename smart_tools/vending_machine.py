"""
自动售货机模拟器 (Vending Machine Simulator)
演示智能合约的"履约换履约"本质
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Transaction:
    """交易记录"""
    timestamp: str
    action: str
    amount: float
    result: str
    details: str


@dataclass
class Product:
    """商品"""
    name: str
    price: float
    stock: int
    emoji: str = "📦"


class VendingMachine:
    """
    智能合约模拟：自动售货机
    
    核心概念：
    - 状态变量：balance, inventory
    - 条件判断：金额检查、库存检查
    - 状态转换：原子性操作
    - Revert：条件不满足时回滚
    """
    
    def __init__(self, owner: str = "Contract Owner"):
        self.owner = owner
        self.balance = 0.0  # 合约余额（收到的代币）
        self.products: Dict[str, Product] = {}
        self.transaction_log: List[Transaction] = []
        self.created_at = datetime.now().isoformat()
    
    def add_product(self, product_id: str, name: str, price: float, stock: int, emoji: str = "📦"):
        """添加商品到售货机"""
        self.products[product_id] = Product(
            name=name,
            price=price,
            stock=stock,
            emoji=emoji
        )
    
    def get_status(self) -> Dict:
        """获取售货机状态"""
        return {
            "owner": self.owner,
            "balance": self.balance,
            "products": {
                pid: {
                    "name": p.name,
                    "price": p.price,
                    "stock": p.stock,
                    "emoji": p.emoji
                }
                for pid, p in self.products.items()
            },
            "transaction_count": len(self.transaction_log),
            "created_at": self.created_at
        }
    
    def deposit_and_dispense(self, product_id: str, amount: float, buyer: str = "User") -> Dict:
        """
        核心函数：投币并获取商品
        
        这是智能合约的核心逻辑：
        1. 检查条件
        2. 如果条件不满足 -> Revert（退款）
        3. 如果条件满足 -> 更新状态 + 返回商品
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 检查1：商品是否存在
        if product_id not in self.products:
            tx = Transaction(
                timestamp=timestamp,
                action="REVERT",
                amount=amount,
                result="❌ 失败",
                details=f"商品 '{product_id}' 不存在，退款 {amount} ETH"
            )
            self.transaction_log.append(tx)
            return {
                "success": False,
                "error": "PRODUCT_NOT_FOUND",
                "message": f"商品 '{product_id}' 不存在",
                "refund": amount,
                "transaction": tx.__dict__
            }
        
        product = self.products[product_id]
        
        # 检查2：金额是否足够
        if amount < product.price:
            tx = Transaction(
                timestamp=timestamp,
                action="REVERT",
                amount=amount,
                result="❌ 失败",
                details=f"金额不足 ({amount} < {product.price})，退款 {amount} ETH"
            )
            self.transaction_log.append(tx)
            return {
                "success": False,
                "error": "INSUFFICIENT_FUNDS",
                "message": f"金额不足：需要 {product.price} ETH，收到 {amount} ETH",
                "refund": amount,
                "transaction": tx.__dict__
            }
        
        # 检查3：库存是否充足
        if product.stock <= 0:
            tx = Transaction(
                timestamp=timestamp,
                action="REVERT",
                amount=amount,
                result="❌ 失败",
                details=f"'{product.name}' 已售罄，退款 {amount} ETH"
            )
            self.transaction_log.append(tx)
            return {
                "success": False,
                "error": "OUT_OF_STOCK",
                "message": f"商品 '{product.name}' 已售罄",
                "refund": amount,
                "transaction": tx.__dict__
            }
        
        # ✅ 所有检查通过 - 执行状态转换
        change = amount - product.price
        
        # 原子操作：更新状态
        self.balance += product.price
        product.stock -= 1
        
        tx = Transaction(
            timestamp=timestamp,
            action="SUCCESS",
            amount=product.price,
            result="✅ 成功",
            details=f"购买 {product.emoji} {product.name}，找零 {change:.4f} ETH"
        )
        self.transaction_log.append(tx)
        
        return {
            "success": True,
            "product": {
                "id": product_id,
                "name": product.name,
                "emoji": product.emoji
            },
            "paid": product.price,
            "change": change,
            "remaining_stock": product.stock,
            "contract_balance": self.balance,
            "transaction": tx.__dict__
        }
    
    def get_transaction_log(self) -> List[Dict]:
        """获取交易日志"""
        return [tx.__dict__ for tx in self.transaction_log]
    
    def withdraw(self, amount: float, caller: str) -> Dict:
        """提取合约余额（仅合约所有者可调用）"""
        if caller != self.owner:
            return {
                "success": False,
                "error": "UNAUTHORIZED",
                "message": "只有合约所有者可以提取余额"
            }
        
        if amount > self.balance:
            return {
                "success": False,
                "error": "INSUFFICIENT_BALANCE",
                "message": f"合约余额不足：{self.balance} ETH"
            }
        
        self.balance -= amount
        return {
            "success": True,
            "withdrawn": amount,
            "remaining_balance": self.balance
        }


def create_demo_machine() -> VendingMachine:
    """创建演示用售货机"""
    machine = VendingMachine(owner="BlockchainLab")
    
    # 添加商品
    machine.add_product("cola", "可乐", 0.001, 10, "🥤")
    machine.add_product("coffee", "咖啡", 0.002, 5, "☕")
    machine.add_product("water", "矿泉水", 0.0005, 20, "💧")
    machine.add_product("snack", "薯片", 0.0015, 8, "🍿")
    machine.add_product("nft", "限量 NFT", 0.1, 1, "🎨")
    
    return machine


def get_machine_status(machine: VendingMachine) -> Dict:
    """获取格式化的机器状态"""
    status = machine.get_status()
    return {
        "machine": status,
        "explanation": {
            "balance": "合约累计收到的 ETH",
            "products": "可购买的商品列表",
            "revert": "当条件不满足时，交易回滚，资金退回",
            "atomic": "状态更新是原子的：要么全部成功，要么全部失败"
        }
    }


if __name__ == "__main__":
    print("=" * 60)
    print("自动售货机模拟器 (Smart Contract Demo)")
    print("=" * 60)
    
    machine = create_demo_machine()
    print("\n📦 售货机已部署！")
    print(f"所有者: {machine.owner}")
    print("\n商品列表:")
    for pid, product in machine.products.items():
        print(f"  {product.emoji} {product.name}: {product.price} ETH (库存: {product.stock})")
    
    # 测试交易
    print("\n" + "-" * 60)
    print("测试交易:")
    
    # 成功购买
    result = machine.deposit_and_dispense("cola", 0.002)
    print(f"\n1. 购买可乐 (0.002 ETH): {result['transaction']['result']}")
    if result['success']:
        print(f"   找零: {result['change']} ETH")
    
    # 金额不足
    result = machine.deposit_and_dispense("coffee", 0.001)
    print(f"\n2. 购买咖啡 (0.001 ETH): {result['transaction']['result']}")
    print(f"   原因: {result.get('message', '')}")
    
    # 商品不存在
    result = machine.deposit_and_dispense("pizza", 1.0)
    print(f"\n3. 购买披萨 (1.0 ETH): {result['transaction']['result']}")
    print(f"   原因: {result.get('message', '')}")
    
    print(f"\n合约余额: {machine.balance} ETH")
