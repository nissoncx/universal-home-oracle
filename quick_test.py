"""
Universal Home Oracle - Quick Test
快速测试脚本，验证系统是否正确配置
"""

import sys


def test_imports():
    """测试导入是否正常"""
    print("🔍 测试 1: 检查依赖导入...")
    try:
        from langgraph.graph import StateGraph
        from langchain_core.messages import HumanMessage, AIMessage
        from langchain_openai import ChatOpenAI
        print("   ✅ 所有依赖导入成功")
        return True
    except ImportError as e:
        print(f"   ❌ 导入失败: {e}")
        print("\n请运行: pip install -r requirements.txt")
        return False


def test_project_structure():
    """测试项目结构"""
    print("\n🔍 测试 2: 检查项目结构...")
    try:
        from home_oracle.graph.state import AgentState
        from home_oracle.config import Config
        from home_oracle.agents.nodes import home_chief
        from home_oracle.graph.workflow import create_workflow
        print("   ✅ 项目结构正确")
        return True
    except Exception as e:
        print(f"   ❌ 项目结构错误: {e}")
        return False


def test_state_definition():
    """测试状态定义"""
    print("\n🔍 测试 3: 检查 AgentState 定义...")
    try:
        from home_oracle.graph.state import AgentState

        # 创建一个测试状态
        test_state: AgentState = {
            "user_request": "测试需求",
            "user_profile": {"budget": "medium"},
            "messages": [],
            "sub_plans": {},
            "conflict_detected": False,
            "budget_status": "OK",
            "final_proposal": "",
            "iteration_count": 0
        }

        print("   ✅ AgentState 定义正确")
        print(f"   - 字段数量: {len(test_state)}")
        return True
    except Exception as e:
        print(f"   ❌ AgentState 定义错误: {e}")
        return False


def test_workflow_creation():
    """测试工作流创建（不需要 API Key）"""
    print("\n🔍 测试 4: 检查工作流构建...")
    try:
        from home_oracle.graph.workflow import create_workflow

        # 创建工作流（不需要 API Key 就可以构建图）
        workflow = create_workflow()

        print("   ✅ 工作流构建成功")
        print(f"   - 节点数量: {len(workflow.nodes)}")
        print(f"   - 节点列表: {list(workflow.nodes)}")
        return True
    except Exception as e:
        print(f"   ❌ 工作流构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """测试配置"""
    print("\n🔍 测试 5: 检查配置...")
    try:
        from home_oracle.config import Config

        print(f"   ✅ 配置模块加载成功")
        print(f"   - QWEN_MODEL: {Config.QWEN_MODEL}")
        print(f"   - QWEN_BASE_URL: {Config.QWEN_BASE_URL}")
        print(f"   - MAX_ITERATIONS: {Config.MAX_ITERATIONS}")

        # 检查 API Key
        if Config.QWEN_API_KEY:
            print(f"   - QWEN_API_KEY: {Config.QWEN_API_KEY[:10]}... (已设置)")
        else:
            print(f"   - QWEN_API_KEY: 未设置 (运行时需要)")

        return True
    except Exception as e:
        print(f"   ❌ 配置检查失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🧪 Universal Home Oracle - 快速测试")
    print("="*60 + "\n")

    results = []

    # 运行所有测试
    results.append(("依赖导入", test_imports()))
    results.append(("项目结构", test_project_structure()))
    results.append(("状态定义", test_state_definition()))
    results.append(("工作流构建", test_workflow_creation()))
    results.append(("配置检查", test_config()))

    # 打印测试结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！系统已就绪。")
        print("\n下一步:")
        print("1. 设置通义千问 API Key:")
        print("   export QWEN_API_KEY='your-api-key'")
        print("\n2. 运行完整模拟:")
        print("   python simulation.py")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查依赖安装。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
