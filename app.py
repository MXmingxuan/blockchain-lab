"""
区块链密码学工具 Web 应用
Flask 服务器提供交互式界面
"""
from flask import Flask, render_template, request, jsonify
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 第三章：密码学原语
from crypto_tools.avalanche import compare_hashes
from crypto_tools.mini_blockchain import Blockchain
from crypto_tools.merkle_tree import build_merkle_tree, get_tree_structure, build_tree_levels, get_merkle_root
from crypto_tools.digital_signature import generate_keypair, sign_message, verify_signature, check_ecdsa
from crypto_tools.bitcoin_address import generate_bitcoin_address

# 第四章：共识与挖矿
from mining_tools.pow_simulator import mine_block, estimate_mining_time
from mining_tools.mining_calc import calculate_mining_profit, get_breakeven_price
from mining_tools.difficulty import predict_difficulty_adjustment, get_current_difficulty
from mining_tools.fork_monitor import get_confirmation_safety, explain_why_6_confirmations
from mining_tools.inflation import get_inflation_stats, get_halving_countdown

app = Flask(__name__)

# 全局区块链实例（用于演示）
blockchain = Blockchain()


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


# ===== 第三章工具 =====

# 工具1: 雪崩效应
@app.route('/avalanche')
def avalanche_page():
    return render_template('avalanche.html')


@app.route('/api/avalanche', methods=['POST'])
def api_avalanche():
    data = request.json
    str_a = data.get('string_a', 'Hello World')
    str_b = data.get('string_b', 'Hello world')
    result = compare_hashes(str_a, str_b)
    return jsonify(result)


# 工具2: 迷你区块链
@app.route('/blockchain')
def blockchain_page():
    return render_template('blockchain.html')


@app.route('/api/blockchain/chain')
def api_blockchain_chain():
    return jsonify({
        'chain': blockchain.get_chain_data(),
        'valid': blockchain.is_chain_valid()
    })


@app.route('/api/blockchain/add', methods=['POST'])
def api_blockchain_add():
    data = request.json
    block_data = data.get('data', 'New Transaction')
    new_block = blockchain.add_block(block_data)
    return jsonify({
        'block': new_block.to_dict(),
        'chain': blockchain.get_chain_data()
    })


@app.route('/api/blockchain/tamper', methods=['POST'])
def api_blockchain_tamper():
    data = request.json
    index = data.get('index', 1)
    new_data = data.get('data', 'Tampered Data')
    result = blockchain.tamper_block(index, new_data)
    return jsonify({
        'tamper_result': result,
        'chain': blockchain.get_chain_data(),
        'valid': blockchain.is_chain_valid()
    })


@app.route('/api/blockchain/reset', methods=['POST'])
def api_blockchain_reset():
    global blockchain
    blockchain = Blockchain()
    return jsonify({
        'message': '区块链已重置',
        'chain': blockchain.get_chain_data()
    })


# 工具3: 默克尔树
@app.route('/merkle')
def merkle_page():
    return render_template('merkle.html')


@app.route('/api/merkle', methods=['POST'])
def api_merkle():
    data = request.json
    transactions = data.get('transactions', [])
    
    if not transactions:
        return jsonify({'error': '请提供交易列表'})
    
    root = build_merkle_tree(transactions)
    tree_structure = get_tree_structure(root) if root else {}
    levels = build_tree_levels(transactions)
    
    return jsonify({
        'merkle_root': root.hash if root else '',
        'tree_structure': tree_structure,
        'levels': levels,
        'transaction_count': len(transactions)
    })


# 工具4: 数字签名
@app.route('/signature')
def signature_page():
    return render_template('signature.html')


@app.route('/api/signature/generate')
def api_signature_generate():
    if not check_ecdsa():
        return jsonify({'error': '请安装 ecdsa 库: pip install ecdsa'})
    
    keypair = generate_keypair()
    return jsonify({
        'private_key': keypair['private_key'],
        'public_key': keypair['public_key']
    })


@app.route('/api/signature/sign', methods=['POST'])
def api_signature_sign():
    data = request.json
    message = data.get('message', '')
    private_key = data.get('private_key', '')
    
    result = sign_message(message, private_key)
    return jsonify(result)


@app.route('/api/signature/verify', methods=['POST'])
def api_signature_verify():
    data = request.json
    message = data.get('message', '')
    signature = data.get('signature', '')
    public_key = data.get('public_key', '')
    
    result = verify_signature(message, signature, public_key)
    return jsonify(result)


# 工具5: 比特币地址
@app.route('/address')
def address_page():
    return render_template('address.html')


@app.route('/api/address/generate')
def api_address_generate():
    result = generate_bitcoin_address()
    return jsonify(result)


# ===== 第四章工具 =====

# 工具1: PoW 挖矿模拟器
@app.route('/pow')
def pow_page():
    return render_template('pow.html')


@app.route('/api/pow/mine', methods=['POST'])
def api_pow_mine():
    data = request.json
    block_data = data.get('data', 'Block Data')
    difficulty = data.get('difficulty', 4)
    
    result = mine_block(block_data, difficulty=difficulty, max_attempts=50000000)
    return jsonify({
        'success': result.success,
        'nonce': result.nonce,
        'hash': result.hash,
        'attempts': result.attempts,
        'time_seconds': result.time_seconds,
        'difficulty': result.difficulty
    })


# 工具2: 挖矿盈亏计算器
@app.route('/mining')
def mining_page():
    return render_template('mining_calc.html')


@app.route('/api/mining/calculate', methods=['POST'])
def api_mining_calculate():
    data = request.json
    result = calculate_mining_profit(
        hashrate_th=data.get('hashrate_th', 110),
        power_watts=data.get('power_watts', 3250),
        electricity_cost=data.get('electricity_cost', 0.05),
        pool_fee_percent=data.get('pool_fee_percent', 2.0)
    )
    return jsonify(result)


# 工具3: 难度调整预测
@app.route('/difficulty')
def difficulty_page():
    return render_template('difficulty.html')


@app.route('/api/difficulty/predict')
def api_difficulty_predict():
    result = predict_difficulty_adjustment()
    return jsonify(result)


# 工具4: 分叉监控
@app.route('/forks')
def forks_page():
    return render_template('forks.html')


@app.route('/api/forks/safety')
def api_forks_safety():
    confirmations = request.args.get('confirmations', 6, type=int)
    result = get_confirmation_safety(confirmations)
    return jsonify(result)


@app.route('/api/forks/explain')
def api_forks_explain():
    result = explain_why_6_confirmations()
    return jsonify(result)


# 工具5: 通胀率仪表盘
@app.route('/inflation')
def inflation_page():
    return render_template('inflation.html')


@app.route('/api/inflation/stats')
def api_inflation_stats():
    result = get_inflation_stats()
    return jsonify(result)


if __name__ == '__main__':
    print("=" * 50)
    print("区块链密码学工具 Web 应用")
    print("访问: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)

