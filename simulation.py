"""
Universal Home Oracle - Simulation Script
模拟运行完整的多智能体协作流程
"""

import os
from langchain_core.messages import HumanMessage

from home_oracle.graph.state import AgentState
from home_oracle.graph.workflow import create_workflow
from home_oracle.config import Config


def setup_api_key():
    """
    设置通义千问 API Key

    请从以下方式之一设置：
    1. 环境变量: export QWEN_API_KEY='your-api-key'
    2. 在这里直接输入
    """
    api_key = os.getenv("QWEN_API_KEY")

    if not api_key:
        print("\n" + "="*60)
        print("🔑 通义千问 API Key 配置")
        print("="*60)
        print("请输入你的通义千问 API Key:")
        print("(获取地址: https://dashscope.aliyuncs.com/apiKey)")
        print("="*60)

        api_key = input("\nAPI Key: ").strip()

        if not api_key:
            print("\n❌ 未提供 API Key，程序退出")
            exit(1)

        Config.set_api_key(api_key)
        print("\n✅ API Key 已设置")
    else:
        Config.QWEN_API_KEY = api_key
        print(f"\n✅ 从环境变量读取 API Key: {api_key[:10]}...")


def simulate_scenario_1():
    """
    场景 1: 预算冲突场景
    用户要求高消费活动，但预算等级为 low
    预期：触发预算超支 → 自动修正 → 再次审核 → 通过
    """
    print("\n" + "🎬 "*20)
    print("场景 1: 预算冲突与自动修正")
    print("🎬 "*20 + "\n")

    initial_state: AgentState = {
        "user_request": """
我想要一个完美的周计划！具体需求如下：
1. 每天去高档餐厅用餐
2. 周末安排一次豪华旅行
3. 请营养师设计健康饮食
4. 智能家居需要全面检查
5. 我最近压力有点大，需要心理辅导
""",
        "user_profile": {
            "health": "healthy",
            "budget": "low",  # 低预算
            "location": "Beijing",
            "family_size": 2,
            "preferences": ["fine_dining", "travel", "health"]
        },
        "messages": [HumanMessage(content="我想制定一个完美的周计划")],
        "sub_plans": {},
        "conflict_detected": False,
        "budget_status": "OK",
        "final_proposal": "",
        "iteration_count": 0
    }

    return initial_state


def simulate_scenario_2():
    """
    场景 2: 正常场景
    用户需求合理，预算充足
    预期：一次性通过所有审核
    """
    print("\n" + "🎬 "*20)
    print("场景 2: 正常规划场景")
    print("🎬 "*20 + "\n")

    initial_state: AgentState = {
        "user_request": """
帮我规划一个健康的一周生活：
1. 制定运动计划
2. 推荐一些免费的文化活动
3. 家电维护提醒
4. 学习资源推荐
5. 心理健康建议
""",
        "user_profile": {
            "health": "diabetic",
            "budget": "high",  # 高预算
            "location": "Shanghai",
            "family_size": 1,
            "preferences": ["sports", "culture", "learning"]
        },
        "messages": [HumanMessage(content="帮我规划健康的一周")],
        "sub_plans": {},
        "conflict_detected": False,
        "budget_status": "OK",
        "final_proposal": "",
        "iteration_count": 0
    }

    return initial_state


def run_simulation(initial_state: AgentState, scenario_name: str = "Simulation"):
    """
    运行完整的多智能体协作流程

    Args:
        initial_state: 初始状态
        scenario_name: 场景名称
    """
    print("\n" + "="*60)
    print(f"🚀 启动 {scenario_name}")
    print("="*60)

    # 创建工作流
    app = create_workflow()

    # 配置线程 ID（用于 checkpoint）
    config = {"configurable": {"thread_id": f"simulation_{scenario_name}"}}

    print("\n⏳ 开始执行多智能体协作...")
    print("-"*60)

    try:
        # 执行工作流
        # stream_mode="values" 会返回每个步骤后的完整状态
        for event in app.stream(initial_state, config, stream_mode="values"):

            # 打印当前状态的关键信息
            if "messages" in event and len(event["messages"]) > 0:
                last_message = event["messages"][-1]
                # 可以选择性打印消息内容
                pass

            # 检查是否有预算状态变化
            if "budget_status" in event:
                budget = event["budget_status"]
                if budget == "OVERRUN":
                    print(f"\n⚠️ 检测到预算超支！准备触发修正流程...")

        print("\n" + "-"*60)
        print("✅ 多智能体协作完成！")

        # 获取最终状态
        final_state = event

        print("\n" + "="*60)
        print("📊 执行摘要")
        print("="*60)
        print(f"✓ 总迭代次数: {final_state.get('iteration_count', 0)}")
        print(f"✓ 最终预算状态: {final_state.get('budget_status', 'OK')}")
        print(f"✓ 冲突检测: {'是' if final_state.get('conflict_detected') else '否'}")
        print(f"✓ 专家方案数量: {len(final_state.get('sub_plans', {}))}")

        print("\n" + "="*60)
        print("📋 专家方案列表:")
        print("="*60)
        for role, plan in final_state.get("sub_plans", {}).items():
            print(f"\n【{role}】")
            print(f"{plan[:150]}..." if len(plan) > 150 else plan)

        # 打印最终提案
        if final_state.get("final_proposal"):
            print("\n" + "="*60)
            print("🎁 最终提案:")
            print("="*60)
            print(final_state["final_proposal"])

        return final_state

    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🏠 Universal Home Oracle - 多智能体协作系统")
    print("="*60)

    # 设置 API Key
    setup_api_key()

    # 验证配置
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n❌ 配置错误: {e}")
        return

    print("\n" + "="*60)
    print("请选择模拟场景:")
    print("="*60)
    print("1. 预算冲突场景（低预算 + 高消费需求）")
    print("2. 正常规划场景（高预算 + 合理需求）")
    print("="*60)

    choice = input("\n请输入选项 (1 或 2): ").strip()

    if choice == "1":
        initial_state = simulate_scenario_1()
        run_simulation(initial_state, "Budget_Conflict_Scenario")
    elif choice == "2":
        initial_state = simulate_scenario_2()
        run_simulation(initial_state, "Normal_Scenario")
    else:
        print("\n⚠️ 无效选项，运行默认场景...")
        initial_state = simulate_scenario_1()
        run_simulation(initial_state, "Default_Scenario")

    print("\n" + "="*60)
    print("🎉 模拟运行完成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
