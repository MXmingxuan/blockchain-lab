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
from mining_tools.whale_alert import scan_recent_blocks, get_latest_block

# 第五章：交易与脚本
from tx_tools.utxo_visualizer import get_address_utxos, visualize_utxos, select_utxos_for_transfer
from tx_tools.dust_analyzer import analyze_dust, get_effective_balance, simulate_fee_scenarios
from tx_tools.script_simulator import demo_p2pkh_execution, get_opcode_reference
from tx_tools.coinbase_decoder import decode_genesis_block, get_famous_messages, get_block_by_height, get_coinbase_data
from tx_tools.locktime_builder import create_locktime_demo, get_locktime_use_cases

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


# 工具6: 巨鲸警报
@app.route('/whale')
def whale_page():
    return render_template('whale_alert.html')


@app.route('/api/whale/scan', methods=['POST'])
def api_whale_scan():
    data = request.json
    threshold_btc = data.get('threshold_btc', 100)
    block_count = data.get('block_count', 1)
    result = scan_recent_blocks(block_count=block_count, threshold_btc=threshold_btc)
    return jsonify(result)


@app.route('/api/whale/latest')
def api_whale_latest():
    result = get_latest_block()
    return jsonify(result)


# ===== 第五章工具 =====

# 工具1: UTXO 可视化
@app.route('/utxo')
def utxo_page():
    return render_template('utxo.html')


@app.route('/api/utxo/query', methods=['POST'])
def api_utxo_query():
    data = request.json
    address = data.get('address', '')
    result = get_address_utxos(address)
    if result.get('success'):
        result['coins'] = visualize_utxos(result.get('utxos', []))
    return jsonify(result)


@app.route('/api/utxo/select', methods=['POST'])
def api_utxo_select():
    data = request.json
    utxos = data.get('utxos', [])
    amount_btc = data.get('amount_btc', 0)
    result = select_utxos_for_transfer(utxos, amount_btc)
    return jsonify(result)


# 工具2: 粉尘分析
@app.route('/dust')
def dust_page():
    return render_template('dust.html')


@app.route('/api/dust/analyze', methods=['POST'])
def api_dust_analyze():
    data = request.json
    fee_rate = data.get('fee_rate', 20)
    
    # 使用模拟 UTXO 数据
    mock_utxos = [
        {'value_satoshi': 50000000, 'value_btc': 0.5},
        {'value_satoshi': 200000000, 'value_btc': 2.0},
        {'value_satoshi': 10000000, 'value_btc': 0.1},
        {'value_satoshi': 5000, 'value_btc': 0.00005},
        {'value_satoshi': 1000, 'value_btc': 0.00001},
        {'value_satoshi': 50000, 'value_btc': 0.0005},
    ]
    
    analysis = analyze_dust(mock_utxos, fee_rate)
    balance = get_effective_balance(mock_utxos, fee_rate)
    scenarios = simulate_fee_scenarios(mock_utxos)
    
    return jsonify({
        **analysis,
        **balance,
        'scenarios': scenarios
    })


# 工具3: 脚本模拟器
@app.route('/script')
def script_page():
    return render_template('script.html')


@app.route('/api/script/run', methods=['POST'])
def api_script_run():
    data = request.json
    valid_sig = data.get('valid_sig', True)
    result = demo_p2pkh_execution()
    # 根据 valid_sig 调整结果
    if not valid_sig:
        result['execution']['success'] = False
        result['execution']['final_stack'] = ['00']
    return jsonify(result['execution'])


@app.route('/api/script/opcodes')
def api_script_opcodes():
    return jsonify(get_opcode_reference())


# 工具4: Coinbase 解码
@app.route('/coinbase')
def coinbase_page():
    return render_template('coinbase.html')


@app.route('/api/coinbase/genesis')
def api_coinbase_genesis():
    return jsonify(decode_genesis_block())


@app.route('/api/coinbase/famous')
def api_coinbase_famous():
    return jsonify(get_famous_messages())


@app.route('/api/coinbase/decode', methods=['POST'])
def api_coinbase_decode():
    data = request.json
    height = data.get('height', 0)
    block_hash = get_block_by_height(height)
    if block_hash:
        result = get_coinbase_data(block_hash)
        return jsonify(result)
    return jsonify({'success': False, 'error': '获取区块失败'})


# 工具5: 时间锁
@app.route('/locktime')
def locktime_page():
    return render_template('locktime.html')


@app.route('/api/locktime/create', methods=['POST'])
def api_locktime_create():
    data = request.json
    lock_type = data.get('lock_type', 'blocks')
    lock_value = data.get('lock_value', 100)
    result = create_locktime_demo(lock_type, lock_value)
    return jsonify(result)


@app.route('/api/locktime/usecases')
def api_locktime_usecases():
    return jsonify(get_locktime_use_cases())


# ===== 第六章工具 =====

# 导入第6章模块
from smart_tools.vending_machine import VendingMachine, create_demo_machine, get_machine_status
from smart_tools.oracle_demo import FlightOracle, InsuranceContract, demo_oracle_flow
from smart_tools.state_tracker import BitcoinLedger, EthereumLedger, GasSimulator, compare_models
from smart_tools.dapp_auditor import analyze_dapp, get_sample_dapps, calculate_health_score
from smart_tools.ambiguity_tree import generate_decision_tree, get_contract_scenarios, count_edge_cases

# 全局实例
vending_machine = create_demo_machine()
flight_oracle = FlightOracle()
insurance_contract = InsuranceContract(flight_oracle)


# 工具1: 自动售货机
@app.route('/vending')
def vending_page():
    return render_template('vending.html')


@app.route('/api/vending/status')
def api_vending_status():
    return jsonify(get_machine_status(vending_machine))


@app.route('/api/vending/purchase', methods=['POST'])
def api_vending_purchase():
    data = request.json
    product_id = data.get('product_id')
    amount = float(data.get('amount', 0))
    result = vending_machine.deposit_and_dispense(product_id, amount)
    return jsonify(result)


# 工具2: 预言机演示
@app.route('/oracle')
def oracle_page():
    return render_template('oracle.html')


@app.route('/api/oracle/flights')
def api_oracle_flights():
    return jsonify(flight_oracle.list_flights())


@app.route('/api/oracle/check')
def api_oracle_check():
    flight = request.args.get('flight', '')
    return jsonify(flight_oracle.get_flight_status(flight))


@app.route('/api/oracle/purchase', methods=['POST'])
def api_oracle_purchase():
    data = request.json
    flight = data.get('flight')
    policy_id = data.get('policy_id')
    result = insurance_contract.purchase_policy(policy_id, flight, "User")
    return jsonify(result)


@app.route('/api/oracle/claim', methods=['POST'])
def api_oracle_claim():
    data = request.json
    policy_id = data.get('policy_id')
    result = insurance_contract.check_and_claim(policy_id)
    return jsonify(result)


# 工具3: 状态转换追踪器
@app.route('/state')
def state_page():
    return render_template('state.html')


@app.route('/api/state/transfer', methods=['POST'])
def api_state_transfer():
    data = request.json
    sender = data.get('sender', 'Alice')
    receiver = data.get('receiver', 'Bob')
    amount = float(data.get('amount', 5))
    
    # UTXO 模型
    btc = BitcoinLedger()
    btc.create_utxo(sender, 10.0)
    btc.transfer(sender, receiver, amount)
    
    # 账户模型
    eth = EthereumLedger()
    eth.deposit(sender, 10.0)
    eth.transfer(sender, receiver, amount)
    
    return jsonify({
        'utxo': btc.get_state(),
        'account': eth.get_state()
    })


@app.route('/api/state/gas', methods=['POST'])
def api_state_gas():
    data = request.json
    gas_limit = int(data.get('gas_limit', 50))
    iterations = int(data.get('iterations', 100))
    
    gas = GasSimulator(gas_limit=gas_limit)
    result = gas.simulate_loop(iterations)
    return jsonify(result)


# 工具4: DApp 活跃度分析
@app.route('/dapp')
def dapp_page():
    return render_template('dapp.html')


@app.route('/api/dapp/list')
def api_dapp_list():
    return jsonify(get_sample_dapps())


@app.route('/api/dapp/analyze')
def api_dapp_analyze():
    name = request.args.get('name', '')
    return jsonify(analyze_dapp(name))


# 工具5: 法律模糊性决策树
@app.route('/ambiguity')
def ambiguity_page():
    return render_template('ambiguity.html')


@app.route('/api/ambiguity/scenarios')
def api_ambiguity_scenarios():
    return jsonify(get_contract_scenarios())


@app.route('/api/ambiguity/generate')
def api_ambiguity_generate():
    scenario = request.args.get('scenario', 'buy_house')
    depth = int(request.args.get('depth', 3))
    return jsonify(generate_decision_tree(scenario, depth))


# ===== 第七章工具 =====

# 导入第7章模块
from challenge_tools.trilemma_simulator import simulate_trilemma, get_trilemma_explanation, TrilemmaParams
from challenge_tools.layer2_demo import PaymentChannel, simulate_channel_transactions, compare_layer1_vs_layer2
from challenge_tools.zkp_verifier import create_commitment, verify_commitment, demo_age_verification
from challenge_tools.governance_monitor import get_fork_history, analyze_fork_risk, get_governance_lessons
from challenge_tools.coase_analyzer import analyze_project, get_sample_projects, calculate_coase_boundary

# 全局支付通道实例
payment_channel = PaymentChannel(alice_deposit=5.0, bob_deposit=5.0)


# 工具1: 不可能三角模拟器
@app.route('/trilemma')
def trilemma_page():
    return render_template('trilemma.html')


@app.route('/api/trilemma/simulate', methods=['POST'])
def api_trilemma_simulate():
    data = request.json
    params = TrilemmaParams(
        block_size_kb=data.get('block_size_kb', 1000),
        block_time_seconds=data.get('block_time_seconds', 600),
        node_count=data.get('node_count', 10000)
    )
    result = simulate_trilemma(params)
    return jsonify(result)


# 工具2: Layer 2 支付通道
@app.route('/layer2')
def layer2_page():
    return render_template('layer2.html')


@app.route('/api/layer2/open', methods=['POST'])
def api_layer2_open():
    global payment_channel
    payment_channel = PaymentChannel(alice_deposit=5.0, bob_deposit=5.0)
    result = payment_channel.open_channel()
    return jsonify(result)


@app.route('/api/layer2/simulate', methods=['POST'])
def api_layer2_simulate():
    data = request.json
    tx_count = data.get('tx_count', 10000)
    result = simulate_channel_transactions(tx_count)
    return jsonify(result)


@app.route('/api/layer2/compare', methods=['POST'])
def api_layer2_compare():
    data = request.json
    tx_count = data.get('tx_count', 10000)
    result = compare_layer1_vs_layer2(tx_count)
    return jsonify(result)


# 工具3: 零知识证明
@app.route('/zkp')
def zkp_page():
    return render_template('zkp.html')


@app.route('/api/zkp/prove', methods=['POST'])
def api_zkp_prove():
    data = request.json
    birth_year = data.get('birth_year', 1995)
    threshold = data.get('threshold', 21)
    
    # 使用年龄验证演示
    result = demo_age_verification()
    # 覆盖用户输入的参数
    result['prover_secret']['birth_year'] = birth_year
    result['prover_secret']['actual_age'] = 2026 - birth_year
    result['result']['claim_verified'] = (2026 - birth_year) >= threshold
    result['result']['message'] = f"✅ 年龄 {2026 - birth_year} >= {threshold}" if (2026 - birth_year) >= threshold else f"❌ 年龄 {2026 - birth_year} < {threshold}"
    
    return jsonify(result)


# 工具4: 治理与硬分叉监控
@app.route('/governance')
def governance_page():
    return render_template('governance.html')


@app.route('/api/governance/forks')
def api_governance_forks():
    return jsonify(get_fork_history())


@app.route('/api/governance/analyze', methods=['POST'])
def api_governance_analyze():
    data = request.json
    result = analyze_fork_risk(data)
    return jsonify(result)


# 工具5: 科斯定理分析
@app.route('/coase')
def coase_page():
    return render_template('coase.html')


@app.route('/api/coase/list')
def api_coase_list():
    return jsonify(get_sample_projects())


@app.route('/api/coase/analyze')
def api_coase_analyze():
    name = request.args.get('name', '')
    return jsonify(analyze_project(name))


if __name__ == '__main__':
    print("=" * 50)
    print("区块链密码学工具 Web 应用")
    print("访问: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)



