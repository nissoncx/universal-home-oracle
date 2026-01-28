# Universal Home Oracle - 架构文档

## 系统概述

这是一个基于 **LangGraph** 构建的多智能体协作系统，包含 9 个专家 Agent，通过并行执行、条件路由和反馈循环实现智能家庭生活规划。

## 核心架构

### 1. State Management (共享状态)

**文件**: [home_oracle/graph/state.py](home_oracle/graph/state.py)

```python
class AgentState(TypedDict):
    user_request: str              # 用户需求
    user_profile: Dict[str, Any]   # 用户画像
    messages: List[BaseMessage]    # 消息历史
    sub_plans: Dict[str, str]      # 专家方案
    conflict_detected: bool        # 冲突标记
    budget_status: str             # 预算状态
    final_proposal: str            # 最终提案
    iteration_count: int           # 迭代计数
```

**关键特性**:
- 使用 `Annotated[List[BaseMessage], operator.add]` 实现消息自动追加
- `budget_status` 作为条件路由的判断依据
- `iteration_count` 防止无限循环

---

### 2. Agent Nodes (智能体节点)

**文件**: [home_oracle/agents/nodes.py](home_oracle/agents/nodes.py)

#### 节点职责

| 节点 | 类型 | 功能 |
|------|------|------|
| `home_chief` | 协调器 | 解析需求，分配任务 |
| `health_nutrition` | 执行层 | 制定健康饮食方案 |
| `social_travel` | 执行层 | 规划社交出行（**可被修正**）|
| `smart_home_admin` | 执行层 | 管理智能家居 |
| `psychology_coach` | 执行层 | 心理健康辅导 |
| `knowledge_curator` | 执行层 | 推荐学习资源 |
| `financial_advisor` | 审核层 | 审核预算，设置 `budget_status` |
| `fact_checker` | 审核层 | 事实核查 |
| `proposal_synthesizer` | 合成器 | 生成最终提案 |

#### LLM 集成

使用通义千问 API (通过 ChatOpenAI 兼容接口):

```python
def create_llm():
    return ChatOpenAI(
        model=Config.QWEN_MODEL,        # "qwen-max"
        api_key=Config.QWEN_API_KEY,
        base_url=Config.QWEN_BASE_URL,  # "https://dashscope.aliyuncs.com/compatible-mode/v1"
        temperature=0.7,
    )
```

---

### 3. Graph Workflow (图结构)

**文件**: [home_oracle/graph/workflow.py](home_oracle/graph/workflow.py)

#### 图拓扑

```
                   Entry
                    ↓
            ┌───────────────────────┐
            │    Home_Chief         │
            └───────────────────────┘
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
[并行执行层 - Execution Layer]
    │
    ├─ Health_Nutrition ────────┐
    │                          │
    ├─ Social_Travel ───────────┤
    │                          │
    ├─ Smart_Home_Admin ───────┤
    │                          ↓
    ├─ Psychology_Coach ───────┤
    │                          │
    └─ Knowledge_Curator ──────┘
                               ↓
              [同步点 - Synchronization]
                               ↓
    ┌──────────────────────────────────┐
    │                                  │
    ↓                                  ↓
┌──────────────────┐        ┌──────────────────┐
│Financial_Advisor │        │  Fact_Checker    │
└──────────────────┘        └──────────────────┘
    ↓                                  ↓
    └────────────┬─────────────────────┘
                 ↓
        [条件边 - Conditional Edge]
                 ↓
    ┌────────────┴────────────┐
    ↓                         ↓
budget_status            budget_status
 == 'OVERRUN'              == 'OK'
    ↓                         ↓
返回 Social_Travel      Proposal_Synthesizer
(修正预算)                     ↓
                              END
```

#### 关键代码片段

**1. 添加节点**

```python
workflow.add_node("Home_Chief", home_chief)
workflow.add_node("Health_Nutrition", health_nutrition)
# ... 添加所有 9 个节点
```

**2. 并行执行**

```python
# Home_Chief 完成后，并行触发所有执行层节点
execution_layer = [
    "Health_Nutrition",
    "Social_Travel",
    "Smart_Home_Admin",
    "Psychology_Coach",
    "Knowledge_Curator",
]

for node in execution_layer:
    workflow.add_edge("Home_Chief", node)
```

**3. 同步点**

```python
# 所有执行层节点完成后，进入审核层
# LangGraph 自动等待所有传入边完成
review_layer = ["Financial_Advisor", "Fact_Checker"]

for exec_node in execution_layer:
    for review_node in review_layer:
        workflow.add_edge(exec_node, review_node)
```

**4. 条件边 (反馈循环)**

```python
workflow.add_conditional_edges(
    source="Financial_Advisor",
    path=should_revise_budget,
    path_map={
        "revise": "Social_Travel",         # 预算超支 → 返回修正
        "approve": "Proposal_Synthesizer",  # 预算通过 → 继续
    }
)
```

**路由函数**:

```python
def should_revise_budget(state: AgentState) -> str:
    budget_status = state.get("budget_status", "OK")
    iteration_count = state.get("iteration_count", 0)

    if budget_status == "OVERRUN" and iteration_count < Config.MAX_ITERATIONS:
        return "revise"    # 返回 Social_Travel
    else:
        return "approve"   # 继续
```

---

### 4. Human-in-the-Loop (人类介入)

**实现方式**: MemorySaver Checkpointer

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```

**使用场景**:

```python
# 运行到特定节点时暂停
config = {"configurable": {"thread_id": "session_123"}}

# 第一次运行（会暂停）
for event in app.stream(initial_state, config):
    pass

# 人类介入后，继续执行
app_state = app.get_state(config)
# 修改状态...
app.update_state(config, new_state)

# 继续运行
for event in app.stream(None, config):
    pass
```

---

### 5. 预算冲突循环机制

#### 工作流程

1. **初始规划**:
   ```
   Social_Travel → 提出豪华旅行方案（高消费）
   ```

2. **预算审核**:
   ```
   Financial_Advisor → 检测预算超支
   设置 state["budget_status"] = "OVERRUN"
   ```

3. **条件路由**:
   ```
   should_revise_budget() → 返回 "revise"
   ```

4. **反馈修正**:
   ```
   返回 Social_Travel
   在 prompt 中告知预算超支
   Social_Travel 重新规划经济方案
   state["iteration_count"] += 1
   ```

5. **再次审核**:
   ```
   Financial_Advisor → 新方案审核通过
   设置 state["budget_status"] = "OK"
   ```

6. **继续流程**:
   ```
   should_revise_budget() → 返回 "approve"
   进入 Proposal_Synthesizer
   ```

#### 防止无限循环

```python
# config.py
MAX_ITERATIONS: int = 3

# nodes.py
if budget_status == "OVERRUN" and iteration_count < Config.MAX_ITERATIONS:
    return "revise"  # 继续修正
else:
    return "approve"  # 强制通过
```

---

## 关键技术点

### 1. 并行执行

LangGraph 使用 **自动并行机制**:
- 当一个节点有多个传出边时，会并行触发下游节点
- 等待所有传入边完成后才执行当前节点
- 无需手动管理线程或异步

### 2. 状态更新模式

**累加模式** (messages):

```python
messages: Annotated[List[BaseMessage], operator.add]
```

每个节点返回的新消息会**追加**到现有列表，而不是覆盖。

**覆盖模式** (其他字段):

```python
return {"budget_status": "OVERRUN"}
```

直接覆盖现有值。

### 3. 消息格式

使用 LangChain 标准消息类型:

```python
from langchain_core.messages import HumanMessage, AIMessage

# 用户消息
HumanMessage(content="我想制定计划")

# AI 消息
AIMessage(content="[Agent] 这是我的建议")
```

---

## 运行流程示例

### 场景: 预算冲突

```python
# 1. 初始状态
initial_state = {
    "user_request": "我想每天去高档餐厅，周末豪华旅行",
    "user_profile": {"budget": "low"},
    "budget_status": "OK",
    "iteration_count": 0
}

# 2. 执行流程
Home_Chief
    ↓ (并行触发)
Health_Nutrition, Social_Travel, ...
    ↓
Social_Travel 方案: "五星级酒店住宿，米其林餐厅..."
    ↓
Financial_Advisor
    ↓ 检测到低预算 + 高消费
budget_status = "OVERRUN"
    ↓
条件路由 → 返回 "revise"
    ↓
Social_Travel (第2次)
    ↓ 收到 OVERRUN 提示
新方案: "家庭聚会，公园游玩，家常菜..."
    ↓ iteration_count = 1
Financial_Advisor
    ↓ 新方案审核通过
budget_status = "OK"
    ↓
条件路由 → 返回 "approve"
    ↓
Proposal_Synthesizer
    ↓
生成最终提案
```

---

## 扩展建议

### 1. 持久化存储

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string("postgresql://...")
app = workflow.compile(checkpointer=checkpointer)
```

### 2. 添加中断点

```python
from langgraph.types import Command

def proposal_synthesizer(state):
    if Config.ENABLE_HUMAN_CHECK:
        return Command(resume="human_approval_required")

    # ... 生成提案
```

### 3. 可视化

```python
from home_oracle.graph.workflow import create_workflow, visualize_workflow

workflow = create_workflow()
visualize_workflow(workflow, "graph.png")
```

---

## 调试技巧

### 1. 打印图结构

```python
workflow.get_graph().print_ascii()
```

### 2. 查看状态历史

```python
state = app.get_state(config)
print(state.next)      # 下一个节点
print(state.tasks)     # 待执行任务
```

### 3. 流式输出

```python
for event in app.stream(initial_state, config):
    for node_name, node_output in event.items():
        print(f"[{node_name}] 完成")
```

---

## 性能优化

1. **并行执行**: 将独立节点放在执行层，充分利用并行
2. **缓存**: 对 LLM 调用结果进行缓存
3. **批处理**: 合并多个小请求为一个大请求
4. **异步**: 使用异步 LLM 调用 (`ainvoke`)

---

## 故障排查

### 问题 1: 导入错误

```
ModuleNotFoundError: No module named 'langgraph'
```

**解决**:
```bash
pip install -r requirements.txt
```

### 问题 2: API Key 错误

```
ValueError: QWEN_API_KEY 未设置！
```

**解决**:
```bash
export QWEN_API_KEY='your-api-key'
```

### 问题 3: 无限循环

**检查**:
1. `should_revise_budget()` 逻辑
2. `MAX_ITERATIONS` 设置
3. `iteration_count` 是否正确递增

---

## 参考资料

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [通义千问 API 文档](https://help.aliyun.com/zh/dashscope/)
- [LangChain Core API](https://python.langchain.com/)
