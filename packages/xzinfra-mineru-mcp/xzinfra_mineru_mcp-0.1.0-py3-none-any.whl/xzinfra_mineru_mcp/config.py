import os
from typing import List, Optional


class ConfigType:
    def __init__(self):
        self.mineru_base_url: Optional[str] = None
        self.mineru_api_key: Optional[str] = None
        self.allowed_paths: List[str] = []
        self.default_timeout: int = 600  # 默认10分钟超时（秒）
    
    def validate_environment(self) -> None:
        """校验必需的环境变量"""
        self.mineru_base_url = os.getenv("SELF_MINERU_BASE_URL")
        self.mineru_api_key = os.getenv("SELF_MINERU_API_KEY")
        
        if not self.mineru_base_url:
            raise ValueError("环境变量 SELF_MINERU_BASE_URL 是必需的")
        
        if not self.mineru_api_key:
            raise ValueError("环境变量 SELF_MINERU_API_KEY 是必需的")
    
    def set_allowed_paths(self, paths: List[str]) -> None:
        """设置允许的路径列表"""
        self.allowed_paths = paths
    
    def set_default_timeout(self, timeout: int) -> None:
        """设置默认超时时间（秒）"""
        if timeout <= 0:
            raise ValueError("超时时间必须大于0秒")
        self.default_timeout = timeout
        
config = ConfigType()