"""
Layer 2 支付通道演示器 (Lightning Channel Demo)
模拟闪电网络的链下交易与链上结算
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random


@dataclass
class Transaction:
    """交易记录"""
    from_party: str
    to_party: str
    amount: float
    timestamp: str
    tx_type: str  # "on_chain" or "off_chain"


class PaymentChannel:
    """
    支付通道模拟
    
    核心概念：
    1. 链上开通通道（锁定资金）
    2. 链下进行无限次交易（仅更新本地状态）
    3. 链上关闭通道（广播最终状态）
    """
    
    def __init__(self, alice_deposit: float, bob_deposit: float):
        self.alice_balance = alice_deposit
        self.bob_balance = bob_deposit
        self.initial_alice = alice_deposit
        self.initial_bob = bob_deposit
        self.is_open = False
        self.off_chain_tx_count = 0
        self.transaction_log: List[Transaction] = []
        self.channel_id = f"CH_{random.randint(1000, 9999)}"
    
    def open_channel(self) -> Dict:
        """
        链上交易1：开通通道
        锁定双方资金到多签地址
        """
        if self.is_open:
            return {"success": False, "error": "通道已开通"}
        
        self.is_open = True
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 记录链上交易
        self.transaction_log.append(Transaction(
            from_party="Alice",
            to_party="Channel",
            amount=self.alice_balance,
            timestamp=timestamp,
            tx_type="on_chain"
        ))
        self.transaction_log.append(Transaction(
            from_party="Bob",
            to_party="Channel",
            amount=self.bob_balance,
            timestamp=timestamp,
            tx_type="on_chain"
        ))
        
        return {
            "success": True,
            "channel_id": self.channel_id,
            "alice_locked": self.alice_balance,
            "bob_locked": self.bob_balance,
            "on_chain_txs": 2,
            "message": f"✅ 通道 {self.channel_id} 已开通，资金已锁定到多签地址"
        }
    
    def transfer(self, from_party: str, amount: float) -> Dict:
        """
        链下交易：仅更新本地状态
        不广播到区块链，即时完成
        """
        if not self.is_open:
            return {"success": False, "error": "通道未开通"}
        
        from_party = from_party.lower()
        
        if from_party == "alice":
            if self.alice_balance < amount:
                return {"success": False, "error": "Alice 余额不足"}
            self.alice_balance -= amount
            self.bob_balance += amount
            to_party = "Bob"
        elif from_party == "bob":
            if self.bob_balance < amount:
                return {"success": False, "error": "Bob 余额不足"}
            self.bob_balance -= amount
            self.alice_balance += amount
            to_party = "Alice"
        else:
            return {"success": False, "error": "无效的发送方"}
        
        self.off_chain_tx_count += 1
        
        # 不记录每笔链下交易到日志（太多了），只更新计数
        
        return {
            "success": True,
            "tx_number": self.off_chain_tx_count,
            "from": from_party.capitalize(),
            "to": to_party,
            "amount": amount,
            "alice_balance": self.alice_balance,
            "bob_balance": self.bob_balance,
            "on_chain": False  # 链下交易
        }
    
    def close_channel(self) -> Dict:
        """
        链上交易2：关闭通道
        广播最终状态到区块链
        """
        if not self.is_open:
            return {"success": False, "error": "通道未开通"}
        
        self.is_open = False
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 记录链上交易
        self.transaction_log.append(Transaction(
            from_party="Channel",
            to_party="Alice",
            amount=self.alice_balance,
            timestamp=timestamp,
            tx_type="on_chain"
        ))
        self.transaction_log.append(Transaction(
            from_party="Channel",
            to_party="Bob",
            amount=self.bob_balance,
            timestamp=timestamp,
            tx_type="on_chain"
        ))
        
        return {
            "success": True,
            "channel_id": self.channel_id,
            "final_alice": self.alice_balance,
            "final_bob": self.bob_balance,
            "off_chain_txs": self.off_chain_tx_count,
            "on_chain_txs": 2,  # 仅关闭的2笔
            "total_on_chain": 4,  # 开通2笔 + 关闭2笔
            "message": f"✅ 通道已关闭，最终余额已结算到链上"
        }
    
    def get_status(self) -> Dict:
        """获取通道状态"""
        return {
            "channel_id": self.channel_id,
            "is_open": self.is_open,
            "alice_balance": self.alice_balance,
            "bob_balance": self.bob_balance,
            "off_chain_tx_count": self.off_chain_tx_count,
            "on_chain_tx_count": len([t for t in self.transaction_log if t.tx_type == "on_chain"])
        }


def simulate_channel_transactions(tx_count: int = 10000) -> Dict:
    """
    模拟大量链下交易
    """
    channel = PaymentChannel(alice_deposit=5.0, bob_deposit=5.0)
    channel.open_channel()
    
    # 模拟随机交易
    for i in range(tx_count):
        # 随机选择发送方和金额
        if random.random() > 0.5:
            amount = random.uniform(0.001, 0.01)
            if channel.alice_balance >= amount:
                channel.transfer("alice", amount)
        else:
            amount = random.uniform(0.001, 0.01)
            if channel.bob_balance >= amount:
                channel.transfer("bob", amount)
    
    result = channel.close_channel()
    
    return {
        "simulation": {
            "requested_txs": tx_count,
            "actual_off_chain_txs": channel.off_chain_tx_count,
            "on_chain_txs": result["total_on_chain"]
        },
        "final_state": {
            "alice_balance": channel.alice_balance,
            "bob_balance": channel.bob_balance,
            "net_flow": channel.alice_balance - channel.initial_alice
        }
    }


def compare_layer1_vs_layer2(tx_count: int = 10000) -> Dict:
    """
    对比 Layer 1 vs Layer 2 的成本
    """
    # Layer 1 假设
    avg_gas_fee_usd = 2.0  # 平均每笔交易 Gas 费
    avg_confirmation_time_min = 10  # 平均确认时间
    
    # Layer 2 模拟
    l2_result = simulate_channel_transactions(tx_count)
    
    # Layer 1 成本计算
    l1_total_gas = tx_count * avg_gas_fee_usd
    l1_total_time_hours = (tx_count * avg_confirmation_time_min) / 60
    
    # Layer 2 成本计算 (仅4笔链上交易)
    l2_on_chain_txs = l2_result["simulation"]["on_chain_txs"]
    l2_total_gas = l2_on_chain_txs * avg_gas_fee_usd
    l2_total_time_min = l2_on_chain_txs * avg_confirmation_time_min
    
    return {
        "transaction_count": tx_count,
        "layer1": {
            "on_chain_txs": tx_count,
            "total_gas_usd": l1_total_gas,
            "total_time_hours": round(l1_total_time_hours, 1),
            "avg_cost_per_tx": avg_gas_fee_usd
        },
        "layer2": {
            "on_chain_txs": l2_on_chain_txs,
            "off_chain_txs": l2_result["simulation"]["actual_off_chain_txs"],
            "total_gas_usd": l2_total_gas,
            "total_time_min": l2_total_time_min,
            "avg_cost_per_tx": round(l2_total_gas / tx_count, 6)
        },
        "savings": {
            "gas_saved_usd": l1_total_gas - l2_total_gas,
            "gas_saved_percent": f"{((l1_total_gas - l2_total_gas) / l1_total_gas) * 100:.2f}%",
            "time_saved_hours": round(l1_total_time_hours - (l2_total_time_min / 60), 1)
        },
        "conclusion": f"Layer 2 将 {tx_count} 笔交易压缩为 {l2_on_chain_txs} 笔链上交易，节省 {((l1_total_gas - l2_total_gas) / l1_total_gas) * 100:.1f}% 费用"
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Layer 2 支付通道演示器")
    print("=" * 60)
    
    result = compare_layer1_vs_layer2(10000)
    
    print(f"\n📊 10,000 笔交易对比:")
    print(f"\n  Layer 1 (全部上链):")
    print(f"    链上交易: {result['layer1']['on_chain_txs']}")
    print(f"    总 Gas 费: ${result['layer1']['total_gas_usd']}")
    print(f"    总时间: {result['layer1']['total_time_hours']} 小时")
    
    print(f"\n  Layer 2 (支付通道):")
    print(f"    链上交易: {result['layer2']['on_chain_txs']}")
    print(f"    链下交易: {result['layer2']['off_chain_txs']}")
    print(f"    总 Gas 费: ${result['layer2']['total_gas_usd']}")
    
    print(f"\n  💰 节省:")
    print(f"    费用: ${result['savings']['gas_saved_usd']} ({result['savings']['gas_saved_percent']})")
    print(f"    时间: {result['savings']['time_saved_hours']} 小时")
