# securipaperbot/agents/base_agent.py

from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
import logging


class BaseAgent(ABC):
    """基础代理类，定义所有代理的通用接口"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def process(self, *args, **kwargs) -> Dict[str, Any]:
        """处理方法，需要被子类实现"""
        pass

    def validate_config(self) -> bool:
        """验证配置是否有效"""
        return True

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """记录错误信息"""
        self.logger.error(f"Error in {self.__class__.__name__}: {str(error)}",
                          extra={"context": context})

    def log_info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """记录信息"""
        self.logger.info(message, extra={"context": context})