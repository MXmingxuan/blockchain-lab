"""
Coinbase 秘密信息解码器 (Coinbase Message Decoder)
解码矿工在 Coinbase 交易中留下的信息
"""
import requests
import re
from typing import Dict, List, Optional


def hex_to_ascii(hex_string: str) -> str:
    """
    将十六进制字符串转换为 ASCII（过滤不可打印字符）
    """
    try:
        # 移除可能的 0x 前缀
        hex_clean = hex_string.replace('0x', '').replace(' ', '')
        
        # 转换为字节
        raw_bytes = bytes.fromhex(hex_clean)
        
        # 提取可打印 ASCII 字符
        printable = []
        for byte in raw_bytes:
            if 32 <= byte <= 126:  # 可打印 ASCII 范围
                printable.append(chr(byte))
            elif byte in (9, 10, 13):  # Tab, LF, CR
                printable.append(' ')
        
        text = ''.join(printable).strip()
        # 合并多个空格
        text = re.sub(r'\s+', ' ', text)
        return text
    
    except Exception:
        return ''


def get_coinbase_data(block_hash: str) -> Dict:
    """
    获取指定区块的 Coinbase 交易数据
    """
    try:
        resp = requests.get(
            f'https://blockchain.info/rawblock/{block_hash}',
            timeout=15
        )
        
        if resp.status_code == 200:
            block = resp.json()
            
            # Coinbase 交易是第一笔交易
            coinbase_tx = block.get('tx', [{}])[0]
            
            # Coinbase 输入的 script 包含任意数据
            coinbase_input = coinbase_tx.get('inputs', [{}])[0]
            script_hex = coinbase_input.get('script', '')
            
            # 解码消息
            message = hex_to_ascii(script_hex)
            
            return {
                'success': True,
                'block_height': block.get('height'),
                'block_hash': block_hash[:16] + '...',
                'block_time': block.get('time'),
                'coinbase_tx_hash': coinbase_tx.get('hash', '')[:16] + '...',
                'script_hex': script_hex[:100] + '...' if len(script_hex) > 100 else script_hex,
                'decoded_message': message,
                'miner': extract_miner_name(message)
            }
    
    except Exception as e:
        pass
    
    return {
        'success': False,
        'error': '获取区块数据失败'
    }


def extract_miner_name(message: str) -> str:
    """
    尝试从 Coinbase 消息中识别矿池名称
    """
    known_pools = [
        'AntPool', 'F2Pool', 'ViaBTC', 'Foundry', 'Binance',
        'SlushPool', 'Poolin', 'BTC.com', 'MARA Pool', 'Luxor',
        'SBI Crypto', 'BitFury', 'Huobi', 'EMCD', 'SpiderPool'
    ]
    
    for pool in known_pools:
        if pool.lower() in message.lower():
            return pool
    
    return '未知矿池'


def get_famous_messages() -> List[Dict]:
    """
    获取历史著名的 Coinbase 消息
    """
    return [
        {
            'block_height': 0,
            'name': '创世区块',
            'message': 'The Times 03/Jan/2009 Chancellor on brink of second bailout for banks',
            'significance': '中本聪留下的《泰晤士报》标题，证明区块创建于2009年1月3日',
            'date': '2009-01-03'
        },
        {
            'block_height': 210000,
            'name': '第一次减半',
            'message': '区块奖励从 50 BTC 减至 25 BTC',
            'significance': '比特币首次经历减半事件',
            'date': '2012-11-28'
        },
        {
            'block_height': 420000,
            'name': '第二次减半',
            'message': '区块奖励从 25 BTC 减至 12.5 BTC',
            'significance': '第二次减半，确认比特币货币政策的可靠性',
            'date': '2016-07-09'
        },
        {
            'block_height': 630000,
            'name': '第三次减半',
            'message': 'NYTimes 09/Apr/2020 With $2.3T Injection, Fed\'s Plan Far Exceeds 2008 Rescue',
            'significance': '矿工 F2Pool 致敬创世区块，记录美联储大放水',
            'date': '2020-05-11'
        },
        {
            'block_height': 840000,
            'name': '第四次减半',
            'message': '区块奖励从 6.25 BTC 减至 3.125 BTC',
            'significance': '2024年减半，预计发生于4月',
            'date': '2024-04-20'
        },
        {
            'block_height': 528333,
            'name': '中国矿工留言',
            'message': '永别了，最后在中国的日子',
            'significance': '中国禁止挖矿前，矿工的告别',
            'date': '2021-06-27'
        }
    ]


def get_block_by_height(height: int) -> Optional[str]:
    """
    根据区块高度获取区块哈希
    """
    try:
        resp = requests.get(
            f'https://blockchain.info/block-height/{height}?format=json',
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            blocks = data.get('blocks', [])
            if blocks:
                return blocks[0].get('hash')
    except:
        pass
    return None


def scan_blocks_for_messages(start_height: int, count: int = 5) -> Dict:
    """
    扫描多个区块的 Coinbase 消息
    """
    results = []
    
    for i in range(count):
        height = start_height + i
        block_hash = get_block_by_height(height)
        
        if block_hash:
            data = get_coinbase_data(block_hash)
            if data.get('success'):
                results.append({
                    'height': height,
                    'message': data.get('decoded_message', ''),
                    'miner': data.get('miner', '')
                })
    
    return {
        'success': True,
        'scanned_count': len(results),
        'start_height': start_height,
        'blocks': results
    }


def decode_genesis_block() -> Dict:
    """
    解码创世区块（特殊处理）
    """
    # 创世区块 Coinbase 数据
    genesis_coinbase_hex = (
        "04ffff001d0104455468652054696d65732030332f4a616e2f"
        "32303039204368616e63656c6c6f72206f6e206272696e6b20"
        "6f66207365636f6e64206261696c6f757420666f722062616e6b73"
    )
    
    message = hex_to_ascii(genesis_coinbase_hex)
    
    return {
        'block_height': 0,
        'block_hash': '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f',
        'coinbase_hex': genesis_coinbase_hex,
        'decoded_message': message,
        'significance': '中本聪在创世区块留下的消息，引用了2009年1月3日《泰晤士报》的头条',
        'historical_context': '这条消息不仅证明了区块的创建日期，也暗示了比特币诞生的时代背景——金融危机和银行救助'
    }


if __name__ == '__main__':
    print("=" * 60)
    print("Coinbase 秘密信息解码器")
    print("=" * 60)
    
    # 解码创世区块
    genesis = decode_genesis_block()
    print("\n🏛️ 创世区块 (Block #0):")
    print(f"   消息: \"{genesis['decoded_message']}\"")
    print(f"   意义: {genesis['significance']}")
    
    print("\n" + "-" * 60)
    print("📜 历史著名 Coinbase 消息:")
    
    for msg in get_famous_messages():
        print(f"\n  区块 #{msg['block_height']} ({msg['name']}):")
        print(f"    日期: {msg['date']}")
        print(f"    消息: {msg['message']}")
        print(f"    意义: {msg['significance']}")
