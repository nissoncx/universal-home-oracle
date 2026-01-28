"""
Universal Home Oracle - Configuration
配置文件，支持通义千问 API
"""

import os
from typing import Optional

class Config:
    """系统配置类"""

    # 通义千问 API 配置
    # 请在环境变量中设置你的 API Key
    # 或者在运行时通过 set_api_key() 方法设置
    QWEN_API_KEY: Optional[str] = os.getenv("QWEN_API_KEY")

    # 通义千问模型选择
    # 可选: "qwen-max", "qwen-plus", "qwen-turbo"
    QWEN_MODEL: str = "qwen-max"

    # API 基础 URL (通义千问)
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # LangGraph 配置
    # 最大迭代次数（防止预算冲突无限循环）
    MAX_ITERATIONS: int = 3

    # Human-in-the-Loop 配置
    # 是否在最终提案前暂停等待人类确认
    ENABLE_HUMAN_CHECK: bool = True

    # Checkpoint 存储路径
    CHECKPOINT_DIR: str = "./checkpoints"

    @classmethod
    def set_api_key(cls, api_key: str) -> None:
        """设置 API Key"""
        cls.QWEN_API_KEY = api_key

    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        if not cls.QWEN_API_KEY:
            raise ValueError(
                "QWEN_API_KEY 未设置！请通过以下方式之一设置：\n"
                "1. 设置环境变量: export QWEN_API_KEY='your-api-key'\n"
                "2. 调用 Config.set_api_key('your-api-key')"
            )
        return True
