# Universal Home Oracle (全能家庭管家)

一个基于 **LangGraph** 的多智能体协作系统，模拟家庭办公室的运作。用户输入模糊的生活需求，系统通过并行处理、冲突检测和多轮迭代，输出一份完美的《周生活提案》。

## 🏗️ 系统架构

### 核心特性

- **9 个专家智能体**：各司其职，协同工作
- **并行执行**：多个 Agent 同时处理任务，提高效率
- **条件路由**：基于预算状态的反馈循环
- **Human-in-the-Loop**：支持人类介入确认
- **状态共享**：通过 `AgentState` 实现智能体间通信

### 智能体角色

| 角色 | 职责 |
|------|------|
| **Home_Chief** | 总监节点，解析需求，分配任务 |
| **Health_Nutrition** | 健康营养专家，制定饮食和运动计划 |
| **Social_Travel** | 社交出行专家，规划娱乐和出行 |
| **Smart_Home_Admin** | 智能家居管理员，安排家电维护和家政 |
| **Psychology_Coach** | 心理健康教练，提供压力管理建议 |
| **Knowledge_Curator** | 知识策展人，推荐学习资源 |
| **Financial_Advisor** | 财务顾问，审核预算 |
| **Fact_Checker** | 事实核查员，验证方案合理性 |
| **Proposal_Synthesizer** | 方案合成器，生成最终提案 |

### 工作流程

```
Entry → Home_Chief
       ↓
[并行执行] → Health_Nutrition, Social_Travel, Smart_Home_Admin,
             Psychology_Coach, Knowledge_Curator
       ↓
[审核] → Financial_Advisor, Fact_Checker
       ↓
[条件判断]
  ├─ OVERRUN → 返回 Social_Travel (修正)
  └─ OK → Proposal_Synthesizer
       ↓
END
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- 通义千问 API Key ([获取地址](https://dashscope.aliyuncs.com/apiKey))

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

方式一：环境变量
```bash
export QWEN_API_KEY='your-api-key'
```

方式二：复制配置文件
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 4. 运行模拟

```bash
python simulation.py
```

## 📁 项目结构

```
Universal-Home-Oracle/
├── home_oracle/
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py           # AgentState 定义
│   │   └── workflow.py        # LangGraph 工作流
│   └── agents/
│       ├── __init__.py
│       └── nodes.py           # 9 个智能体节点实现
├── simulation.py              # 模拟运行脚本
├── requirements.txt           # Python 依赖
├── .env.example              # 环境变量示例
└── README.md
```

## 💡 使用示例

### 场景 1：预算冲突

```python
initial_state = {
    "user_request": "我想要每天去高档餐厅，周末安排豪华旅行！",
    "user_profile": {"budget": "low"},  # 低预算
    ...
}
```

**预期行为**：
1. Social_Travel 制定高消费方案
2. Financial_Advisor 检测到预算超支
3. 触发反馈循环，返回 Social_Travel
4. Social_Travel 重新规划经济方案
5. 预算审核通过，生成最终提案

### 场景 2：正常规划

```python
initial_state = {
    "user_request": "帮我规划健康的一周生活",
    "user_profile": {"budget": "high"},
    ...
}
```

**预期行为**：
1. 各专家并行生成方案
2. 审核通过
3. 一次性生成最终提案

## 🔧 核心技术

### State Definition

使用 `TypedDict` 定义共享状态：

```python
class AgentState(TypedDict):
    user_request: str
    user_profile: Dict[str, Any]
    messages: Annotated[List[BaseMessage], operator.add]
    sub_plans: Dict[str, str]
    conflict_detected: bool
    budget_status: str  # 'OK' or 'OVERRUN'
    final_proposal: str
    iteration_count: int
```

### Conditional Edges

预算冲突反馈循环：

```python
workflow.add_conditional_edges(
    source="Financial_Advisor",
    path=should_revise_budget,
    path_map={
        "revise": "Social_Travel",
        "approve": "Proposal_Synthesizer",
    }
)
```

### Parallel Execution

使用 LangGraph 的自动并行机制：

```python
# Home_Chief 完成后，并行触发多个节点
for node in execution_layer:
    workflow.add_edge("Home_Chief", node)
```

### Human-in-the-Loop

启用 Checkpointer：

```python
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```

## 🎯 扩展建议

1. **添加更多专家**：如教育顾问、法律顾问等
2. **持久化存储**：使用 PostgreSQL 代替 MemorySaver
3. **前端界面**：使用 Streamlit 或 Gradio 构建 UI
4. **多模态输入**：支持图片、语音输入
5. **实时通知**：集成 Telegram/微信通知

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

如有问题，请提交 Issue 或联系维护者。
