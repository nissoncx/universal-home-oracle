"""
Universal Home Oracle - LangGraph Workflow
构建多智能体协作图结构
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict

from ..graph.state import AgentState
from ..agents.nodes import (
    home_chief,
    health_nutrition,
    social_travel,
    smart_home_admin,
    psychology_coach,
    financial_advisor,
    fact_checker,
    knowledge_curator,
    proposal_synthesizer,
    should_revise_budget,
)
from ..config import Config


def create_workflow() -> StateGraph:
    """
    创建 LangGraph 工作流

    图结构：
    Entry → Home_Chief → [并行执行层] → [审核层] → [条件边] → Exit

    详细流程：
    1. Home_Chief（解析需求）
    2. 并行触发：Health_Nutrition, Social_Travel, Smart_Home_Admin,
                 Psychology_Coach, Knowledge_Curator
    3. 同步后进入审核层：Financial_Advisor, Fact_Checker
    4. 条件边：检查 budget_status
       - 如果 'OVERRUN' → 返回 Social_Travel（修正）
       - 如果 'OK' → Proposal_Synthesizer
    5. END
    """

    # 创建状态图
    workflow = StateGraph(AgentState)

    # ========================================================================
    # 添加节点
    # ========================================================================
    print("🔨 正在构建工作流图...")
    print("   添加节点...")

    workflow.add_node("Home_Chief", home_chief)
    workflow.add_node("Health_Nutrition", health_nutrition)
    workflow.add_node("Social_Travel", social_travel)
    workflow.add_node("Smart_Home_Admin", smart_home_admin)
    workflow.add_node("Psychology_Coach", psychology_coach)
    workflow.add_node("Financial_Advisor", financial_advisor)
    workflow.add_node("Fact_Checker", fact_checker)
    workflow.add_node("Knowledge_Curator", knowledge_curator)
    workflow.add_node("Proposal_Synthesizer", proposal_synthesizer)

    print("   ✅ 9 个节点已添加")

    # ========================================================================
    # 设置入口点
    # ========================================================================
    workflow.set_entry_point("Home_Chief")
    print("   ✅ 入口点: Home_Chief")

    # ========================================================================
    # 添加边: Home_Chief → 并行执行层
    # ========================================================================
    # Home_Chief 完成后，并行触发以下节点
    execution_layer = [
        "Health_Nutrition",
        "Social_Travel",
        "Smart_Home_Admin",
        "Psychology_Coach",
        "Knowledge_Curator",
    ]

    for node in execution_layer:
        workflow.add_edge("Home_Chief", node)

    print(f"   ✅ 并行执行层已设置: {', '.join(execution_layer)}")

    # ========================================================================
    # 添加边: 并行执行层 → 审核层
    # ========================================================================
    # 所有执行层节点完成后，进入审核层
    # LangGraph 会自动等待所有传入的边完成
    review_layer = ["Financial_Advisor", "Fact_Checker"]

    for exec_node in execution_layer:
        for review_node in review_layer:
            workflow.add_edge(exec_node, review_node)

    print(f"   ✅ 审核层已设置: {', '.join(review_layer)}")

    # ========================================================================
    # 添加边: 审核层 → 条件路由
    # ========================================================================
    # Financial_Advisor 完成后，进入条件边决策
    # 注意：我们需要等待 Financial_Advisor 和 Fact_Checker 都完成
    # 但条件边只需要从 Financial_Advisor 出发（因为它检查预算）

    # 添加条件边：Financial_Advisor → 路由决策
    workflow.add_conditional_edges(
        source="Financial_Advisor",
        path=should_revise_budget,
        path_map={
            "revise": "Social_Travel",  # 预算超支，返回修正
            "approve": "Proposal_Synthesizer",  # 预算通过，继续
        }
    )

    print("   ✅ 条件边已设置: Financial_Advisor → [revise/approve]")

    # 确保 Fact_Checker 完成后也进入 Proposal_Synthesizer
    workflow.add_edge("Fact_Checker", "Proposal_Synthesizer")

    # ========================================================================
    # 添加边: Proposal_Synthesizer → END
    # ========================================================================
    workflow.add_edge("Proposal_Synthesizer", END)
    print("   ✅ 出口点: Proposal_Synthesizer → END")

    # ========================================================================
    # 编译图（可选：添加 checkpointer）
    # ========================================================================
    print("\n📦 编译图...")

    # 创建 checkpointer（用于 Human-in-the-Loop）
    checkpointer = MemorySaver()

    # 编译图，启用 checkpointer
    app = workflow.compile(checkpointer=checkpointer)

    print("✅ 工作流构建完成！")
    print("\n" + "="*60)
    print("图结构总览:")
    print("  Entry → Home_Chief")
    print("       ↓")
    print("  [并行执行] → Health_Nutrition, Social_Travel, Smart_Home_Admin,")
    print("                Psychology_Coach, Knowledge_Curator")
    print("       ↓")
    print("  [审核] → Financial_Advisor, Fact_Checker")
    print("       ↓")
    print("  [条件判断]")
    print("    ├─ OVERRUN → 返回 Social_Travel (修正)")
    print("    └─ OK → Proposal_Synthesizer")
    print("       ↓")
    print("  END")
    print("="*60 + "\n")

    return app


def visualize_workflow(workflow: StateGraph, output_path: str = "workflow_graph.png"):
    """
    可视化工作流图（需要安装 graphviz 和 pygraphviz）

    使用方法：
    pip install pygraphviz
    brew install graphviz  # macOS
    """
    try:
        from IPython.display import Image, display
        try:
            graph = workflow.get_graph().draw_mermaid_png()
            with open(output_path, "wb") as f:
                f.write(graph)
            print(f"📊 工作流图已保存到: {output_path}")
        except Exception as e:
            print(f"⚠️ 无法生成图像: {e}")
            print("   尝试打印 Mermaid 格式:")
            print(workflow.get_graph().print_ascii())
    except ImportError:
        print("⚠️ 需要安装相关依赖才能可视化:")
        print("   pip install pygraphviz")
        print("   brew install graphviz  # macOS")
        print("\n打印 ASCII 图:")
        print(workflow.get_graph().print_ascii())
