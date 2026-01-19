# Transaction & Script Tools
# MIT Course Chapter 5 - Transactions, UTXO, and Script Code

from .utxo_visualizer import get_address_utxos, select_utxos_for_transfer, simulate_transaction, visualize_utxos
from .dust_analyzer import analyze_dust, get_effective_balance, calculate_consolidation_cost, simulate_fee_scenarios
from .script_simulator import StackMachine, run_p2pkh_script, demo_p2pkh_execution, get_opcode_reference
from .coinbase_decoder import get_coinbase_data, decode_genesis_block, get_famous_messages, get_block_by_height
from .locktime_builder import create_locktime_demo, explain_locktime, get_locktime_use_cases

__all__ = [
    'get_address_utxos', 'select_utxos_for_transfer', 'simulate_transaction', 'visualize_utxos',
    'analyze_dust', 'get_effective_balance', 'calculate_consolidation_cost', 'simulate_fee_scenarios',
    'StackMachine', 'run_p2pkh_script', 'demo_p2pkh_execution', 'get_opcode_reference',
    'get_coinbase_data', 'decode_genesis_block', 'get_famous_messages', 'get_block_by_height',
    'create_locktime_demo', 'explain_locktime', 'get_locktime_use_cases'
]

