"""
预言机原型 (Oracle Demo)
演示外部数据如何触发智能合约执行
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random


@dataclass
class Flight:
    """航班信息"""
    flight_number: str
    departure: str
    arrival: str
    scheduled_time: str
    actual_time: Optional[str]
    status: str  # on_time, delayed, cancelled
    delay_minutes: int


class FlightOracle:
    """
    航班预言机
    
    在真实场景中，预言机从外部 API 获取数据
    这里使用模拟数据来演示概念
    """
    
    def __init__(self):
        self.flights: Dict[str, Flight] = {}
        self._generate_sample_flights()
    
    def _generate_sample_flights(self):
        """生成示例航班数据"""
        flights_data = [
            ("CA123", "北京", "上海", "14:00", "14:00", "on_time", 0),
            ("MU456", "上海", "广州", "16:30", "17:45", "delayed", 75),
            ("CZ789", "深圳", "成都", "09:00", "09:15", "delayed", 15),
            ("HU321", "杭州", "北京", "11:00", "13:30", "delayed", 150),
            ("3U888", "成都", "拉萨", "08:00", None, "cancelled", 0),
            ("CA999", "北京", "东京", "10:00", "10:05", "on_time", 5),
        ]
        
        for fn, dep, arr, sched, actual, status, delay in flights_data:
            self.flights[fn] = Flight(
                flight_number=fn,
                departure=dep,
                arrival=arr,
                scheduled_time=sched,
                actual_time=actual,
                status=status,
                delay_minutes=delay
            )
    
    def get_flight_status(self, flight_number: str) -> Dict:
        """
        查询航班状态
        这模拟了预言机从外部源获取数据的过程
        """
        if flight_number not in self.flights:
            return {
                "found": False,
                "error": f"航班 {flight_number} 不存在"
            }
        
        flight = self.flights[flight_number]
        return {
            "found": True,
            "flight_number": flight.flight_number,
            "route": f"{flight.departure} → {flight.arrival}",
            "scheduled": flight.scheduled_time,
            "actual": flight.actual_time or "未起飞",
            "status": flight.status,
            "delay_minutes": flight.delay_minutes,
            "status_emoji": self._get_status_emoji(flight.status),
            "oracle_timestamp": datetime.now().isoformat()
        }
    
    def _get_status_emoji(self, status: str) -> str:
        return {
            "on_time": "✅",
            "delayed": "⏰",
            "cancelled": "❌"
        }.get(status, "❓")
    
    def list_flights(self) -> List[Dict]:
        """列出所有航班"""
        return [self.get_flight_status(fn) for fn in self.flights]


class InsuranceContract:
    """
    航班延误保险智能合约
    
    核心逻辑：
    - 用户购买保险（锁定资金）
    - 预言机提供航班状态
    - 如果延误 > 阈值，自动赔付
    """
    
    def __init__(self, oracle: FlightOracle):
        self.oracle = oracle
        self.policies: Dict[str, Dict] = {}
        self.contract_balance = 10.0  # 合约初始资金池
        self.premium_rate = 0.01  # 保费（赔付金额的1%）
        self.delay_threshold = 60  # 延误阈值（分钟）
        self.payout_amount = 0.1  # 赔付金额
    
    def purchase_policy(self, policy_id: str, flight_number: str, buyer: str) -> Dict:
        """
        购买保险
        """
        premium = self.premium_rate * self.payout_amount
        
        # 检查航班是否存在
        flight_info = self.oracle.get_flight_status(flight_number)
        if not flight_info.get("found"):
            return {
                "success": False,
                "error": "INVALID_FLIGHT",
                "message": f"航班 {flight_number} 不存在"
            }
        
        # 检查是否已购买
        if policy_id in self.policies:
            return {
                "success": False,
                "error": "DUPLICATE_POLICY",
                "message": "保单已存在"
            }
        
        # 创建保单
        self.policies[policy_id] = {
            "id": policy_id,
            "flight_number": flight_number,
            "buyer": buyer,
            "premium_paid": premium,
            "potential_payout": self.payout_amount,
            "status": "active",
            "purchased_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "policy": self.policies[policy_id],
            "message": f"保险购买成功！保费: {premium} ETH"
        }
    
    def check_and_claim(self, policy_id: str) -> Dict:
        """
        检查并理赔
        
        这是智能合约与预言机交互的核心：
        1. 合约查询预言机获取航班状态
        2. 根据状态决定是否触发赔付
        """
        if policy_id not in self.policies:
            return {
                "success": False,
                "error": "POLICY_NOT_FOUND",
                "message": "保单不存在"
            }
        
        policy = self.policies[policy_id]
        
        if policy["status"] == "claimed":
            return {
                "success": False,
                "error": "ALREADY_CLAIMED",
                "message": "保单已理赔"
            }
        
        # 🔮 关键步骤：查询预言机
        flight_info = self.oracle.get_flight_status(policy["flight_number"])
        
        result = {
            "policy_id": policy_id,
            "flight_number": policy["flight_number"],
            "oracle_data": flight_info,
            "delay_threshold": self.delay_threshold,
            "steps": []
        }
        
        result["steps"].append({
            "step": 1,
            "action": "查询预言机",
            "detail": f"获取航班 {policy['flight_number']} 状态"
        })
        
        result["steps"].append({
            "step": 2,
            "action": "获取延误时间",
            "detail": f"延误 {flight_info['delay_minutes']} 分钟"
        })
        
        # 判断是否满足理赔条件
        if flight_info["delay_minutes"] >= self.delay_threshold:
            # 触发自动赔付
            policy["status"] = "claimed"
            policy["claimed_at"] = datetime.now().isoformat()
            policy["payout"] = self.payout_amount
            
            self.contract_balance -= self.payout_amount
            
            result["steps"].append({
                "step": 3,
                "action": "条件检查",
                "detail": f"{flight_info['delay_minutes']} >= {self.delay_threshold} ✅ 符合理赔条件"
            })
            
            result["steps"].append({
                "step": 4,
                "action": "自动转账",
                "detail": f"向 {policy['buyer']} 转账 {self.payout_amount} ETH"
            })
            
            result["success"] = True
            result["claimed"] = True
            result["payout"] = self.payout_amount
            result["message"] = f"🎉 理赔成功！已自动转账 {self.payout_amount} ETH"
        else:
            result["steps"].append({
                "step": 3,
                "action": "条件检查",
                "detail": f"{flight_info['delay_minutes']} < {self.delay_threshold} ❌ 不符合理赔条件"
            })
            
            result["success"] = True
            result["claimed"] = False
            result["message"] = f"航班延误 {flight_info['delay_minutes']} 分钟，未达到 {self.delay_threshold} 分钟阈值"
        
        return result
    
    def get_policy(self, policy_id: str) -> Optional[Dict]:
        """获取保单信息"""
        return self.policies.get(policy_id)
    
    def get_all_policies(self) -> List[Dict]:
        """获取所有保单"""
        return list(self.policies.values())


def demo_oracle_flow() -> Dict:
    """
    演示完整的预言机工作流程
    """
    oracle = FlightOracle()
    contract = InsuranceContract(oracle)
    
    # 场景1：购买延误航班的保险
    delayed_flight = "MU456"  # 延误75分钟
    policy1 = contract.purchase_policy("POL001", delayed_flight, "Alice")
    claim1 = contract.check_and_claim("POL001")
    
    # 场景2：购买准点航班的保险
    ontime_flight = "CA123"  # 准点
    policy2 = contract.purchase_policy("POL002", ontime_flight, "Bob")
    claim2 = contract.check_and_claim("POL002")
    
    return {
        "oracle_concept": {
            "title": "什么是预言机 (Oracle)？",
            "explanation": "区块链是封闭系统，无法直接获取外部数据。预言机是连接区块链与现实世界的桥梁。",
            "challenge": "如何确保预言机提供的数据是真实可信的？这是一个核心难题。",
            "solutions": ["去中心化预言机网络 (Chainlink)", "多重签名验证", "经济激励机制"]
        },
        "demo_scenarios": [
            {
                "title": "场景1: 航班延误理赔",
                "flight": delayed_flight,
                "policy": policy1,
                "claim_result": claim1
            },
            {
                "title": "场景2: 航班准点",
                "flight": ontime_flight,
                "policy": policy2,
                "claim_result": claim2
            }
        ],
        "available_flights": oracle.list_flights()
    }


if __name__ == "__main__":
    print("=" * 60)
    print("预言机演示 (Oracle Demo)")
    print("=" * 60)
    
    result = demo_oracle_flow()
    
    print("\n📚 核心概念:")
    print(f"  {result['oracle_concept']['title']}")
    print(f"  {result['oracle_concept']['explanation']}")
    
    print("\n✈️ 可用航班:")
    for f in result['available_flights']:
        if f.get('found'):
            print(f"  {f['status_emoji']} {f['flight_number']}: {f['route']} - 延误 {f['delay_minutes']} 分钟")
    
    print("\n" + "-" * 60)
    for scenario in result['demo_scenarios']:
        print(f"\n{scenario['title']}")
        claim = scenario['claim_result']
        if claim.get('steps'):
            for step in claim['steps']:
                print(f"  步骤{step['step']}: {step['action']} - {step['detail']}")
        print(f"  结果: {claim.get('message', '')}")
