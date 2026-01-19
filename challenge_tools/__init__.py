"""
第7章：技术挑战工具模块
"""

from .trilemma_simulator import (
    simulate_trilemma,
    get_trilemma_explanation
)

from .layer2_demo import (
    PaymentChannel,
    simulate_channel_transactions,
    compare_layer1_vs_layer2
)

from .zkp_verifier import (
    create_commitment,
    verify_commitment,
    demo_age_verification
)

from .governance_monitor import (
    get_fork_history,
    analyze_fork_risk,
    get_governance_lessons
)

from .coase_analyzer import (
    analyze_project,
    get_sample_projects,
    calculate_coase_boundary
)
