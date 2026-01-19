"""
第6章：智能合约与 DApps 工具模块
"""

from .vending_machine import (
    VendingMachine,
    create_demo_machine,
    get_machine_status
)

from .oracle_demo import (
    FlightOracle,
    InsuranceContract,
    demo_oracle_flow
)

from .state_tracker import (
    BitcoinLedger,
    EthereumLedger,
    GasSimulator,
    compare_models
)

from .dapp_auditor import (
    analyze_dapp,
    get_sample_dapps,
    calculate_health_score
)

from .ambiguity_tree import (
    generate_decision_tree,
    get_contract_scenarios,
    count_edge_cases
)
