# 快速使用指南

## 安装步骤

### 1. 安装依赖

```bash
# 确保使用 Python 3.10+
python3 --version

# 安装依赖包
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 方式 1: 环境变量
export QWEN_API_KEY='sk-your-api-key-here'

# 方式 2: 使用 .env 文件
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 3. 运行测试

```bash
# 快速测试（不需要 API Key）
python3 quick_test.py
```

## 运行模拟

### 完整模拟

```bash
python3 simulation.py
```

按照提示选择场景：
- **场景 1**: 预算冲突场景（低预算 + 高消费需求）
- **场景 2**: 正常规划场景（高预算 + 合理需求）

### 预期输出

```
============================================================
🏠 [Home_Chief] 正在分析用户需求...
============================================================
📋 需求分析完成:
   用户想要豪华体验，但预算有限，需要平衡...

============================================================
✈️ [Social_Travel] 正在规划社交出行...
============================================================
✅ 社交出行方案已生成

============================================================
💰 [Financial_Advisor] 正在审核预算...
============================================================
⚠️ 预算审核结果: 超支！

🔀 [路由决策] 预算状态: OVERRUN, 迭代次数: 0
   → 决策: 预算超支，返回修正 (路由到 Social_Travel)

============================================================
✈️ [Social_Travel] 正在规划社交出行...
============================================================
✅ 社交出行方案已生成（已修正）

============================================================
💰 [Financial_Advisor] 正在审核预算...
============================================================
✅ 预算审核结果: 通过

============================================================
📝 [Proposal_Synthesizer] 正在合成最终方案...
============================================================
🎉 最终方案生成完成！

... (最终提案内容)
```

## 代码示例

### 基础使用

```python
from langchain_core.messages import HumanMessage
from home_oracle.graph.state import AgentState
from home_oracle.graph.workflow import create_workflow

# 创建工作流
app = create_workflow()

# 定义初始状态
initial_state: AgentState = {
    "user_request": "帮我规划一个健康的一周",
    "user_profile": {
        "budget": "medium",
        "health": "healthy"
    },
    "messages": [HumanMessage(content="帮我规划一个健康的一周")],
    "sub_plans": {},
    "conflict_detected": False,
    "budget_status": "OK",
    "final_proposal": "",
    "iteration_count": 0
}

# 配置
config = {"configurable": {"thread_id": "session_001"}}

# 执行
for event in app.stream(initial_state, config):
    # 处理每个事件
    pass

# 获取最终状态
final_state = app.get_state(config)
print(final_state.values.get("final_proposal"))
```

### 自定义用户画像

```python
user_profile = {
    "budget": "low",          # 预算等级: low, medium, high
    "health": "diabetic",     # 健康状况: healthy, diabetic, etc.
    "location": "Beijing",    # 地理位置
    "family_size": 3,         # 家庭人数
    "preferences": [          # 个人偏好
        "sports",
        "reading",
        "cooking"
    ]
}
```

### 人类介入

```python
from langgraph.checkpoint.memory import MemorySaver

# 编译时启用 checkpointer
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# 第一次运行
config = {"configurable": {"thread_id": "session_001"}}
for event in app.stream(initial_state, config, stream_mode="values"):
    # 打印中间状态
    print(event)

# 暂停后查看状态
state = app.get_state(config)
print(state.next)  # 下一个要执行的节点

# 修改状态后继续
app.update_state(config, {"budget_status": "OK"})

# 继续执行
for event in app.stream(None, config):
    pass
```

## 核心概念

### 1. AgentState (共享状态)

所有智能体共享的状态对象：

```python
{
    "user_request": "用户需求",
    "user_profile": {...},
    "messages": [...],           # 消息历史（自动追加）
    "sub_plans": {               # 各专家的方案
        "Health_Nutrition": "...",
        "Social_Travel": "...",
        ...
    },
    "budget_status": "OK",       # 预算状态
    "iteration_count": 0,        # 迭代次数
    ...
}
```

### 2. 节点函数

每个智能体是一个节点函数：

```python
def my_agent(state: AgentState) -> Dict[str, Any]:
    # 1. 读取状态
    user_request = state["user_request"]

    # 2. 调用 LLM
    llm = create_llm()
    response = llm.invoke([HumanMessage(content=user_request)])

    # 3. 返回状态更新
    return {
        "sub_plans": {...},
        "messages": [AIMessage(content="...")]
    }
```

### 3. 条件路由

```python
def should_revise_budget(state: AgentState) -> str:
    if state["budget_status"] == "OVERRUN":
        return "revise"
    else:
        return "approve"

# 添加到图中
workflow.add_conditional_edges(
    source="Financial_Advisor",
    path=should_revise_budget,
    path_map={
        "revise": "Social_Travel",
        "approve": "Proposal_Synthesizer"
    }
)
```

## 调试技巧

### 1. 查看图结构

```python
from home_oracle.graph.workflow import create_workflow

workflow = create_workflow()
print(workflow.get_graph().print_ascii())
```

### 2. 监控执行

```python
for event in app.stream(initial_state, config):
    for node_name, node_output in event.items():
        print(f"✅ [{node_name}] 执行完成")
```

### 3. 检查状态

```python
state = app.get_state(config)
print(f"下一个节点: {state.next}")
print(f"当前状态: {state.values}")
```

## 常见问题

### Q1: 如何更换 LLM 模型？

编辑 [home_oracle/agents/nodes.py](home_oracle/agents/nodes.py):

```python
def create_llm():
    return ChatOpenAI(
        model="qwen-turbo",  # 改为其他模型
        api_key=Config.QWEN_API_KEY,
        base_url=Config.QWEN_BASE_URL,
        temperature=0.7,
    )
```

### Q2: 如何添加新的智能体？

1. 在 [nodes.py](home_oracle/agents/nodes.py) 中定义节点函数
2. 在 [workflow.py](home_oracle/graph/workflow.py) 中添加节点
3. 添加相应的边

```python
# 1. 定义节点
def new_agent(state: AgentState) -> Dict[str, Any]:
    # ... 实现
    return {}

# 2. 添加到图中
workflow.add_node("New_Agent", new_agent)

# 3. 添加边
workflow.add_edge("Home_Chief", "New_Agent")
```

### Q3: 如何调整最大迭代次数？

编辑 [config.py](home_oracle/config.py):

```python
MAX_ITERATIONS: int = 5  # 修改为其他值
```

### Q4: 如何禁用人类介入？

编辑 [config.py](home_oracle/config.py):

```python
ENABLE_HUMAN_CHECK: bool = False
```

## 进阶功能

### 持久化存储

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:password@localhost/db"
)
app = workflow.compile(checkpointer=checkpointer)
```

### 可视化图结构

```python
from home_oracle.graph.workflow import create_workflow, visualize_workflow

workflow = create_workflow()
visualize_workflow(workflow, "graph.png")
```

### 异步执行

```python
async def run_async():
    app = create_workflow()
    async for event in app.astream(initial_state, config):
        print(event)
```

## 性能优化建议

1. **使用更快的模型**: 对于简单任务使用 `qwen-turbo`
2. **缓存结果**: 启用 LangChain 的缓存机制
3. **并行执行**: 充分利用 LangGraph 的并行能力
4. **减少迭代**: 优化 prompt，减少预算冲突次数

## 获取帮助

- 查看 [ARCHITECTURE.md](ARCHITECTURE.md) 了解详细架构
- 查看 [README.md](README.md) 了解项目概述
- 提交 Issue 报告问题

## 下一步

1. ✅ 安装依赖
2. ✅ 配置 API Key
3. ✅ 运行模拟
4. 🎯 自定义用户画像
5. 🎯 添加新的智能体
6. 🎯 构建前端界面
