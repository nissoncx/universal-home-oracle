"""
Universal Home Oracle - Agent Nodes
实现 9 个专家智能体节点
"""

from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from ..graph.state import AgentState
from ..config import Config


def create_llm():
    """
    创建 LLM 实例，支持通义千问 API
    使用 ChatOpenAI 兼容接口连接通义千问
    """
    Config.validate()

    return ChatOpenAI(
        model=Config.QWEN_MODEL,
        api_key=Config.QWEN_API_KEY,
        base_url=Config.QWEN_BASE_URL,
        temperature=0.7,
    )


# ============================================================================
# 1. Home_Chief (Supervisor) - 路由节点
# ============================================================================

def home_chief(state: AgentState) -> Dict[str, Any]:
    """
    家庭首席官 - 总监节点
    功能：解析用户需求，理解用户画像，为其他专家分配任务
    """
    print("\n" + "="*60)
    print("🏠 [Home_Chief] 正在分析用户需求...")
    print("="*60)

    user_request = state["user_request"]
    user_profile = state["user_profile"]

    # 构建提示词
    prompt = f"""
你是一个经验丰富的家庭管理总监。请分析以下用户需求：

用户需求: {user_request}
用户画像: {user_profile}

你的任务：
1. 理解用户的核心需求
2. 识别关键约束条件（健康、预算、时间等）
3. 为各个专家部门分配明确的任务指令

请输出一份清晰的任务分配概述（不超过100字）。
"""

    llm = create_llm()
    response = llm.invoke([HumanMessage(content=prompt)])

    chief_analysis = response.content

    print(f"📋 需求分析完成:")
    print(f"   {chief_analysis}")

    # 添加消息到历史
    new_message = AIMessage(content=f"[Home_Chief] 需求分析: {chief_analysis}")

    return {
        "messages": [new_message],
        "sub_plans": state.get("sub_plans", {}),
        "budget_status": state.get("budget_status", "OK"),
        "conflict_detected": state.get("conflict_detected", False),
        "iteration_count": state.get("iteration_count", 0)
    }


# ============================================================================
# 2. Health_Nutrition - 健康营养专家
# ============================================================================

def health_nutrition(state: AgentState) -> Dict[str, Any]:
    """
    健康营养专家
    功能：生成饮食计划、运动建议，考虑用户的健康状况
    """
    print("\n" + "="*60)
    print("🥗 [Health_Nutrition] 正在制定健康方案...")
    print("="*60)

    user_request = state["user_request"]
    user_profile = state["user_profile"]

    prompt = f"""
你是一位专业的健康营养顾问。请为用户制定健康方案：

用户需求: {user_request}
用户画像: {user_profile}

请提供：
1. 本周饮食建议（考虑用户健康状况）
2. 运动计划（强度、频率）
3. 健康风险提示

输出简洁的建议内容（200字以内）。
"""

    llm = create_llm()
    response = llm.invoke([HumanMessage(content=prompt)])

    plan = response.content
    print(f"✅ 健康方案已生成")

    # 更新 sub_plans
    sub_plans = state.get("sub_plans", {})
    sub_plans["Health_Nutrition"] = plan

    return {
        "sub_plans": sub_plans,
        "messages": [AIMessage(content=f"[Health_Nutrition] 方案: {plan}")]
    }


# ============================================================================
# 3. Social_Travel - 社交出行专家
# ============================================================================

def social_travel(state: AgentState) -> Dict[str, Any]:
    """
    社交出行专家
    功能：规划娱乐活动、出行方案，估算花费
    注意：可能触发预算冲突
    """
    print("\n" + "="*60)
    print("✈️ [Social_Travel] 正在规划社交出行...")
    print("="*60)

    user_request = state["user_request"]
    user_profile = state["user_profile"]
    budget_status = state.get("budget_status", "OK")
    iteration_count = state.get("iteration_count", 0)

    # 构建提示词 - 如果预算超支，要求降低
    if budget_status == "OVERRUN":
        prompt = f"""
你是一位社交出行规划专家。用户之前的方案预算超支，需要重新规划：

用户需求: {user_request}
用户画像: {user_profile}

⚠️ 预算警告：你之前的方案花费过高！请大幅削减预算，选择：
1. 更经济的娱乐方式（免费展览、公园、家庭聚会等）
2. 省钱的出行方案（公共交通、拼车等）
3. 减少高消费项目

请提供新的社交出行方案（200字以内），务必控制预算。
"""
    else:
        prompt = f"""
你是一位社交出行规划专家。请为用户规划本周的社交和出行：

用户需求: {user_request}
用户画像: {user_profile}

请提供：
1. 娱乐活动建议（餐厅、演出、展览等）
2. 出行安排（交通方式）
3. 预估花费

请提供详细方案（200字以内）。
"""

    llm = create_llm()
    response = llm.invoke([HumanMessage(content=prompt)])

    plan = response.content
    print(f"✅ 社交出行方案已生成")

    sub_plans = state.get("sub_plans", {})
    sub_plans["Social_Travel"] = plan

    return {
        "sub_plans": sub_plans,
        "messages": [AIMessage(content=f"[Social_Travel] 方案: {plan}")]
    }


# ============================================================================
# 4. Smart_Home_Admin - 智能家居管理员
# ============================================================================

def smart_home_admin(state: AgentState) -> Dict[str, Any]:
    """
    智能家居管理员
    功能：家电维护、家政安排、智能家居控制
    """
    print("\n" + "="*60)
    print("🏠 [Smart_Home_Admin] 正在安排家居管理...")
    print("="*60)

    user_request = state["user_request"]
    user_profile = state["user_profile"]

    prompt = f"""
你是一位智能家居管理专家。请为用户安排本周的家居管理：

用户需求: {user_request}
用户画像: {user_profile}

请提供：
1. 家电维护建议（空调清洁、冰箱检查等）
2. 家政安排（保洁、维修等）
3. 智能设备优化建议

输出简洁方案（200字以内）。
"""

    llm = create_llm()
    response = llm.invoke([HumanMessage(content=prompt)])

    plan = response.content
    print(f"✅ 家居管理方案已生成")

    sub_plans = state.get("sub_plans", {})
    sub_plans["Smart_Home_Admin"] = plan

    return {
        "sub_plans": sub_plans,
        "messages": [AIMessage(content=f"[Smart_Home_Admin] 方案: {plan}")]
    }


# ============================================================================
# 5. Psychology_Coach - 心理健康教练
# ============================================================================

def psychology_coach(state: AgentState) -> Dict[str, Any]:
    """
    心理健康教练
    功能：压力监测、情绪管理建议、心理健康评估
    """
    print("\n" + "="*60)
    print("🧠 [Psychology_Coach] 正在评估心理状态...")
    print("="*60)

    user_request = state["user_request"]
    user_profile = state["user_profile"]

    prompt = f"""
你是一位专业的心理健康教练。请为用户评估心理状态并提供建议：

用户需求: {user_request}
用户画像: {user_profile}

请提供：
1. 压力水平评估
2. 情绪管理建议
3. 心理调节练习

输出建议内容（200字以内）。
"""

    llm = create_llm()
    response = llm.invoke([HumanMessage(content=prompt)])

    plan = response.content
    print(f"✅ 心理健康方案已生成")

    sub_plans = state.get("sub_plans", {})
    sub_plans["Psychology_Coach"] = plan

    return {
        "sub_plans": sub_plans,
        "messages": [AIMessage(content=f"[Psychology_Coach] 方案: {plan}")]
    }


# ============================================================================
# 6. Financial_Advisor - 财务顾问（审核节点）
# ============================================================================

def financial_advisor(state: AgentState) -> Dict[str, Any]:
    """
    财务顾问
    功能：审核预算，检测预算超支
    关键：如果 Social_Travel 的花费过高，将 budget_status 设为 'OVERRUN'
    """
    print("\n" + "="*60)
    print("💰 [Financial_Advisor] 正在审核预算...")
    print("="*60)

    sub_plans = state.get("sub_plans", {})
    social_plan = sub_plans.get("Social_Travel", "")
    user_profile = state.get("user_profile", {})

    # 构建 LLM 提示词来分析预算
    prompt = f"""
你是一位严格的财务顾问。请审核以下方案：

用户预算等级: {user_profile.get('budget', 'medium')}
社交出行方案: {social_plan}

你的任务：
1. 评估该方案的花费是否合理
2. 如果用户预算是 'low' 或 'medium'，而方案包含高消费项目（高档餐厅、豪华旅行等），判定为预算超支
3. 如果方案包含大量消费活动，也判定为超支

请只输出以下两个关键词之一：
- BUDGET_OK（预算合理）
- BUDGET_OVERRUN（预算超支）

判断标准要严格！倾向于保守。
"""

    llm = create_llm()
    response = llm.invoke([HumanMessage(content=prompt)])

    decision = response.content.strip().upper()

    # 简单的关键词匹配
    if "OVERRUN" in decision:
        budget_status = "OVERRUN"
        print(f"⚠️ 预算审核结果: 超支！")
        print(f"   决策依据: {decision}")
    else:
        budget_status = "OK"
        print(f"✅ 预算审核结果: 通过")

    new_message = AIMessage(
        content=f"[Financial_Advisor] 预算审核: {budget_status}"
    )

    return {
        "budget_status": budget_status,
        "messages": [new_message]
    }


# ============================================================================
# 7. Fact_Checker - 事实核查员
# ============================================================================

def fact_checker(state: AgentState) -> Dict[str, Any]:
    """
    事实核查员
    功能：验证各专家建议的真实性、合理性
    """
    print("\n" + "="*60)
    print("🔍 [Fact_Checker] 正在进行事实核查...")
    print("="*60)

    sub_plans = state.get("sub_plans", {})

    prompt = f"""
你是一位严格的事实核查专家。请审查以下方案：

{chr(10).join([f"- {role}: {plan}" for role, plan in sub_plans.items()])}

你的任务：
1. 检查是否有明显的事实错误
2. 检查是否有逻辑矛盾
3. 评估整体合理性

如果发现严重问题，请输出 CONFLICT_DETECTED
如果整体合理，请输出 FACT_CHECK_PASS

只输出关键词。
"""

    llm = create_llm()
    response = llm.invoke([HumanMessage(content=prompt)])

    result = response.content.strip().upper()
    conflict_detected = "CONFLICT" in result

    if conflict_detected:
        print(f"⚠️ 事实核查: 发现冲突")
    else:
        print(f"✅ 事实核查: 通过")

    return {
        "conflict_detected": conflict_detected,
        "messages": [AIMessage(content=f"[Fact_Checker] 核查结果: {result}")]
    }


# ============================================================================
# 8. Knowledge_Curator - 知识策展人
# ============================================================================

def knowledge_curator(state: AgentState) -> Dict[str, Any]:
    """
    知识策展人
    功能：推荐学习资料、书籍、课程
    """
    print("\n" + "="*60)
    print("📚 [Knowledge_Curator] 正在推荐学习资源...")
    print("="*60)

    user_request = state["user_request"]
    user_profile = state["user_profile"]

    prompt = f"""
你是一位知识策展人。请根据用户需求推荐学习资源：

用户需求: {user_request}
用户画像: {user_profile}

请推荐：
1. 相关书籍
2. 在线课程
3. 学习建议

输出推荐列表（200字以内）。
"""

    llm = create_llm()
    response = llm.invoke([HumanMessage(content=prompt)])

    plan = response.content
    print(f"✅ 学习资源已推荐")

    sub_plans = state.get("sub_plans", {})
    sub_plans["Knowledge_Curator"] = plan

    return {
        "sub_plans": sub_plans,
        "messages": [AIMessage(content=f"[Knowledge_Curator] 推荐: {plan}")]
    }


# ============================================================================
# 9. Proposal_Synthesizer - 方案合成器
# ============================================================================

def proposal_synthesizer(state: AgentState) -> Dict[str, Any]:
    """
    方案合成器
    功能：汇总所有专家建议，生成最终的《周生活提案》
    """
    print("\n" + "="*60)
    print("📝 [Proposal_Synthesizer] 正在合成最终方案...")
    print("="*60)

    sub_plans = state.get("sub_plans", {})
    user_request = state["user_request"]
    budget_status = state.get("budget_status", "OK")
    iteration_count = state.get("iteration_count", 0)

    prompt = f"""
你是一位专业的方案合成师。请将以下各专家的建议整合成一份完整的《周生活提案》。

用户原始需求: {user_request}
预算审核状态: {budget_status}
迭代轮次: {iteration_count}

各专家方案：
{chr(10).join([f"【{role}】\n{plan}\n" for role, plan in sub_plans.items()])}

请生成一份结构清晰、内容完整的《周生活提案》，包含：
1. 方案概述
2. 各领域详细计划（健康、出行、家居、心理等）
3. 预算总结
4. 执行建议

输出格式要美观、易读。
"""

    llm = create_llm()
    response = llm.invoke([HumanMessage(content=prompt)])

    final_proposal = response.content

    print("\n" + "="*60)
    print("🎉 最终方案生成完成！")
    print("="*60)
    print(f"\n{final_proposal}\n")

    return {
        "final_proposal": final_proposal,
        "messages": [AIMessage(content=f"[Proposal_Synthesizer] 最终方案已生成")]
    }


# ============================================================================
# 路由函数（Conditional Edge）
# ============================================================================

def should_revise_budget(state: AgentState) -> str:
    """
    条件路由函数：决定是否需要修正预算

    如果 budget_status == 'OVERRUN' 且未超过最大迭代次数，
    返回 'revise'（重新规划），
    否则返回 'approve'（继续到下一步）
    """
    budget_status = state.get("budget_status", "OK")
    iteration_count = state.get("iteration_count", 0)

    print(f"\n🔀 [路由决策] 预算状态: {budget_status}, 迭代次数: {iteration_count}")

    if budget_status == "OVERRUN" and iteration_count < Config.MAX_ITERATIONS:
        print("   → 决策: 预算超支，返回修正 (路由到 Social_Travel)")
        return "revise"
    else:
        if budget_status == "OVERRUN":
            print("   → 决策: 已达最大迭代次数，强制通过 (路由到 Proposal_Synthesizer)")
        else:
            print("   → 决策: 预算审核通过 (路由到 Proposal_Synthesizer)")
        return "approve"
