"""
Universal Home Oracle - State Definition
定义系统的共享状态结构
"""

from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage
from operator import add
from typing_extensions import Annotated


class AgentState(TypedDict):
    """Agent之间的共享状态（共享内存）"""

    # 用户的原始需求
    user_request: str

    # 用户画像（健康状态、预算等级、偏好等）
    user_profile: Dict[str, Any]

    # 对话历史（LangChain消息格式，支持消息追加）
    messages: Annotated[List[BaseMessage], add]

    # 各专家的建议存储
    # 结构: {"Health_Nutrition": "建议内容", "Social_Travel": "建议内容", ...}
    sub_plans: Dict[str, str]

    # 是否检测到冲突
    conflict_detected: bool

    # 预算状态: 'OK' 或 'OVERRUN'
    budget_status: str

    # 最终提案
    final_proposal: str

    # 迭代计数器（防止无限循环）
    iteration_count: int
