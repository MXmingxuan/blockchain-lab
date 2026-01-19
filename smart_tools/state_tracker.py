"""
状态转换追踪器 (State Transition Tracker)
对比 UTXO 模型与账户模型，演示 Gas 机制
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UTXO:
    """未花费交易输出"""
    txid: str
    index: int
    owner: str
    amount: float
    spent: bool = False


class BitcoinLedger:
    """
    比特币 UTXO 模型
    
    核心特点：
    - 没有"账户余额"的概念
    - 每笔交易消费旧 UTXO，生成新 UTXO
    - 状态 = 所有未花费的 UTXO 集合
    """
    
    def __init__(self):
        self.utxos: List[UTXO] = []
        self.tx_counter = 0
        self.history: List[Dict] = []
    
    def create_utxo(self, owner: str, amount: float) -> UTXO:
        """创建初始 UTXO（模拟挖矿奖励）"""
        self.tx_counter += 1
        utxo = UTXO(
            txid=f"tx_{self.tx_counter:04d}",
            index=0,
            owner=owner,
            amount=amount
        )
        self.utxos.append(utxo)
        
        self.history.append({
            "action": "CREATE",
            "description": f"创建 UTXO: {owner} +{amount} BTC",
            "utxo": f"{utxo.txid}:{utxo.index}",
            "state_change": f"∅ → UTXO({owner}, {amount})"
        })
        
        return utxo
    
    def transfer(self, from_owner: str, to_owner: str, amount: float) -> Dict:
        """
        UTXO 转账
        
        过程：
        1. 找到 from_owner 的 UTXO
        2. 销毁（标记为已花费）
        3. 生成新的 UTXO 给 to_owner 和找零
        """
        # 收集输入 UTXO
        available = [u for u in self.utxos if u.owner == from_owner and not u.spent]
        total_input = sum(u.amount for u in available)
        
        if total_input < amount:
            return {
                "success": False,
                "error": f"余额不足: 拥有 {total_input} BTC，需要 {amount} BTC"
            }
        
        # 选择足够的 UTXO
        selected = []
        selected_amount = 0
        for utxo in available:
            selected.append(utxo)
            selected_amount += utxo.amount
            if selected_amount >= amount:
                break
        
        # 销毁输入 UTXO
        destroyed = []
        for utxo in selected:
            utxo.spent = True
            destroyed.append(f"{utxo.txid}:{utxo.index}")
        
        self.tx_counter += 1
        new_txid = f"tx_{self.tx_counter:04d}"
        
        # 创建输出 UTXO
        created = []
        
        # 给接收者
        new_utxo = UTXO(txid=new_txid, index=0, owner=to_owner, amount=amount)
        self.utxos.append(new_utxo)
        created.append(f"{new_utxo.txid}:{new_utxo.index} → {to_owner} ({amount})")
        
        # 找零给发送者
        change = selected_amount - amount
        if change > 0:
            change_utxo = UTXO(txid=new_txid, index=1, owner=from_owner, amount=change)
            self.utxos.append(change_utxo)
            created.append(f"{change_utxo.txid}:{change_utxo.index} → {from_owner} ({change})")
        
        self.history.append({
            "action": "TRANSFER",
            "description": f"{from_owner} → {to_owner}: {amount} BTC",
            "inputs_destroyed": destroyed,
            "outputs_created": created,
            "state_change": f"销毁 {len(destroyed)} 个 UTXO，生成 {len(created)} 个新 UTXO"
        })
        
        return {
            "success": True,
            "txid": new_txid,
            "inputs": destroyed,
            "outputs": created,
            "change": change
        }
    
    def get_balance(self, owner: str) -> float:
        """计算余额（= 该地址所有未花费 UTXO 之和）"""
        return sum(u.amount for u in self.utxos if u.owner == owner and not u.spent)
    
    def get_state(self) -> Dict:
        """获取当前状态"""
        active_utxos = [u for u in self.utxos if not u.spent]
        return {
            "model": "UTXO (Bitcoin)",
            "total_utxos": len(active_utxos),
            "utxos": [
                {"id": f"{u.txid}:{u.index}", "owner": u.owner, "amount": u.amount}
                for u in active_utxos
            ],
            "history": self.history[-5:]  # 最近5条
        }


class EthereumLedger:
    """
    以太坊账户模型
    
    核心特点：
    - 直接维护账户余额
    - 转账 = 修改两个账户的余额
    - 状态 = 所有账户余额的映射
    """
    
    def __init__(self):
        self.accounts: Dict[str, float] = {}
        self.nonces: Dict[str, int] = {}  # 交易计数
        self.history: List[Dict] = []
    
    def create_account(self, address: str, balance: float = 0):
        """创建账户"""
        self.accounts[address] = balance
        self.nonces[address] = 0
        
        self.history.append({
            "action": "CREATE",
            "description": f"创建账户: {address} = {balance} ETH",
            "state_change": f"accounts[{address}] = {balance}"
        })
    
    def deposit(self, address: str, amount: float):
        """存款"""
        if address not in self.accounts:
            self.create_account(address)
        
        old_balance = self.accounts[address]
        self.accounts[address] += amount
        
        self.history.append({
            "action": "DEPOSIT",
            "description": f"存款: {address} +{amount} ETH",
            "state_change": f"accounts[{address}]: {old_balance} → {self.accounts[address]}"
        })
    
    def transfer(self, from_addr: str, to_addr: str, amount: float) -> Dict:
        """
        账户模型转账
        
        简单的余额减少/增加操作
        """
        if from_addr not in self.accounts:
            return {"success": False, "error": "发送者账户不存在"}
        
        if self.accounts[from_addr] < amount:
            return {
                "success": False,
                "error": f"余额不足: {self.accounts[from_addr]} < {amount}"
            }
        
        if to_addr not in self.accounts:
            self.create_account(to_addr)
        
        # 直接修改余额
        old_from = self.accounts[from_addr]
        old_to = self.accounts[to_addr]
        
        self.accounts[from_addr] -= amount
        self.accounts[to_addr] += amount
        self.nonces[from_addr] += 1
        
        self.history.append({
            "action": "TRANSFER",
            "description": f"{from_addr} → {to_addr}: {amount} ETH",
            "state_change": f"accounts[{from_addr}]: {old_from} → {self.accounts[from_addr]}, accounts[{to_addr}]: {old_to} → {self.accounts[to_addr]}"
        })
        
        return {
            "success": True,
            "from_balance": self.accounts[from_addr],
            "to_balance": self.accounts[to_addr],
            "nonce": self.nonces[from_addr]
        }
    
    def get_state(self) -> Dict:
        """获取当前状态"""
        return {
            "model": "Account (Ethereum)",
            "accounts": self.accounts.copy(),
            "nonces": self.nonces.copy(),
            "history": self.history[-5:]
        }


class GasSimulator:
    """
    Gas 机制模拟器
    
    演示为什么以太坊需要 Gas：
    - 防止无限循环
    - 为计算资源付费
    """
    
    def __init__(self, gas_limit: int = 100):
        self.gas_limit = gas_limit
        self.gas_used = 0
        self.execution_log: List[Dict] = []
    
    def reset(self, gas_limit: int = None):
        """重置"""
        if gas_limit:
            self.gas_limit = gas_limit
        self.gas_used = 0
        self.execution_log = []
    
    def consume_gas(self, amount: int, operation: str) -> bool:
        """消耗 Gas"""
        if self.gas_used + amount > self.gas_limit:
            self.execution_log.append({
                "operation": operation,
                "gas_cost": amount,
                "status": "❌ OUT_OF_GAS",
                "gas_remaining": self.gas_limit - self.gas_used
            })
            return False
        
        self.gas_used += amount
        self.execution_log.append({
            "operation": operation,
            "gas_cost": amount,
            "status": "✅ OK",
            "gas_remaining": self.gas_limit - self.gas_used
        })
        return True
    
    def simulate_loop(self, iterations: int = 1000) -> Dict:
        """
        模拟循环执行
        每次迭代消耗 1 Gas
        """
        self.reset()
        actual_iterations = 0
        
        for i in range(iterations):
            if not self.consume_gas(1, f"LOOP iteration {i+1}"):
                break
            actual_iterations += 1
        
        return {
            "requested_iterations": iterations,
            "actual_iterations": actual_iterations,
            "gas_limit": self.gas_limit,
            "gas_used": self.gas_used,
            "stopped_reason": "OUT_OF_GAS" if actual_iterations < iterations else "COMPLETED",
            "explanation": "Gas 机制防止了无限循环导致的网络瘫痪"
        }
    
    def simulate_contract_call(self) -> Dict:
        """模拟合约调用的 Gas 消耗"""
        self.reset(gas_limit=50)
        
        operations = [
            (3, "PUSH 数据到栈"),
            (3, "PUSH 数据到栈"),
            (5, "ADD 加法运算"),
            (5, "SSTORE 存储写入"),
            (2, "LOAD 读取数据"),
            (10, "CALL 外部调用"),
            (3, "RETURN 返回结果"),
        ]
        
        for gas_cost, op in operations:
            if not self.consume_gas(gas_cost, op):
                break
        
        return {
            "gas_limit": self.gas_limit,
            "gas_used": self.gas_used,
            "gas_remaining": self.gas_limit - self.gas_used,
            "execution_log": self.execution_log,
            "success": self.gas_used <= self.gas_limit
        }


def compare_models() -> Dict:
    """
    对比 UTXO 模型和账户模型
    """
    # UTXO 模型演示
    btc = BitcoinLedger()
    btc.create_utxo("Alice", 10.0)
    btc.create_utxo("Alice", 5.0)
    btc.transfer("Alice", "Bob", 7.0)
    
    # 账户模型演示
    eth = EthereumLedger()
    eth.deposit("Alice", 15.0)
    eth.transfer("Alice", "Bob", 7.0)
    
    # Gas 演示
    gas = GasSimulator(gas_limit=50)
    gas_result = gas.simulate_loop(100)
    
    return {
        "comparison": {
            "utxo": {
                "name": "UTXO 模型 (Bitcoin)",
                "characteristics": [
                    "没有账户概念，只有 UTXO",
                    "交易 = 消费旧 UTXO + 生成新 UTXO",
                    "更好的隐私性（每次交易可用新地址）",
                    "并行验证能力强"
                ],
                "state": btc.get_state()
            },
            "account": {
                "name": "账户模型 (Ethereum)",
                "characteristics": [
                    "维护账户余额映射",
                    "转账 = 直接修改余额",
                    "支持智能合约状态",
                    "编程模型更简单"
                ],
                "state": eth.get_state()
            }
        },
        "gas_demo": {
            "title": "为什么需要 Gas？",
            "explanation": "以太坊是图灵完备的，可以运行任意代码（包括死循环）。Gas 机制确保每个操作都有成本，无限循环会耗尽 Gas 而停止。",
            "simulation": gas_result
        }
    }


if __name__ == "__main__":
    print("=" * 60)
    print("状态转换追踪器 (State Transition Tracker)")
    print("=" * 60)
    
    result = compare_models()
    
    print("\n📊 UTXO 模型 (Bitcoin)")
    print("-" * 40)
    btc_state = result["comparison"]["utxo"]["state"]
    for h in btc_state["history"]:
        print(f"  [{h['action']}] {h['description']}")
        print(f"       => {h['state_change']}")
    
    print("\n📊 账户模型 (Ethereum)")
    print("-" * 40)
    eth_state = result["comparison"]["account"]["state"]
    for h in eth_state["history"]:
        print(f"  [{h['action']}] {h['description']}")
        print(f"       => {h['state_change']}")
    
    print("\n⛽ Gas 机制演示")
    print("-" * 40)
    gas = result["gas_demo"]["simulation"]
    print(f"  请求迭代: {gas['requested_iterations']}")
    print(f"  实际迭代: {gas['actual_iterations']}")
    print(f"  停止原因: {gas['stopped_reason']}")
