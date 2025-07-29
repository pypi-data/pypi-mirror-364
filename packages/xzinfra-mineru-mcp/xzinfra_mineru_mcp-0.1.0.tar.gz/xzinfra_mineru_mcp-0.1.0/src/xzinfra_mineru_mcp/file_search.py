import os
import fnmatch
from pathlib import Path
from typing import List, Optional, Set
from dataclasses import dataclass


@dataclass
class SearchResult:
    """搜索结果数据类"""
    file_path: str
    file_name: str
    file_size: int
    file_type: str
    modified_time: float


class FileSearcher:
    """文件搜索器，支持文件名模糊搜索和文件类型搜索"""
    
    def __init__(self, allowed_paths: List[str]):
        """
        初始化文件搜索器
        
        Args:
            allowed_paths: 允许搜索的路径列表
        """
        self.allowed_paths = allowed_paths
        
    def search_files(
        self,
        filename_pattern: Optional[str] = None,
        file_types: Optional[List[str]] = None,
        max_results: int = 100
    ) -> List[SearchResult]:
        """
        搜索文件
        
        Args:
            filename_pattern: 文件名模糊匹配模式，支持通配符 * 和 ?
            file_types: 文件类型列表，如 ['pdf', 'docx', 'txt']
            max_results: 最大返回结果数量
            
        Returns:
            搜索结果列表
        """
        if not filename_pattern and not file_types:
            raise ValueError("至少需要提供 filename_pattern 或 file_types 中的一个搜索条件")
            
        results = []
        
        # 标准化文件类型，统一转换为小写
        normalized_file_types = None
        if file_types:
            normalized_file_types = {ext.lower().lstrip('.') for ext in file_types}
        
        for allowed_path in self.allowed_paths:
            if not os.path.exists(allowed_path):
                continue
                
            results.extend(
                self._search_in_directory(
                    allowed_path, 
                    filename_pattern, 
                    normalized_file_types,
                    max_results - len(results)
                )
            )
            
            if len(results) >= max_results:
                break
                
        # 按修改时间倒序排列
        results.sort(key=lambda x: x.modified_time, reverse=True)
        return results[:max_results]
    
    def _search_in_directory(
        self,
        directory: str,
        filename_pattern: Optional[str],
        file_types: Optional[Set[str]],
        max_results: int
    ) -> List[SearchResult]:
        """
        在指定目录中搜索文件
        
        Args:
            directory: 搜索目录
            filename_pattern: 文件名模式
            file_types: 文件类型集合
            max_results: 最大结果数量
            
        Returns:
            搜索结果列表
        """
        results = []
        
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if len(results) >= max_results:
                        return results
                        
                    if self._matches_criteria(file, filename_pattern, file_types):
                        file_path = os.path.join(root, file)
                        try:
                            stat = os.stat(file_path)
                            file_ext = Path(file).suffix.lower().lstrip('.')
                            
                            result = SearchResult(
                                file_path=file_path,
                                file_name=file,
                                file_size=stat.st_size,
                                file_type=file_ext,
                                modified_time=stat.st_mtime
                            )
                            results.append(result)
                        except (OSError, IOError):
                            # 跳过无法访问的文件
                            continue
                            
        except (OSError, IOError):
            # 跳过无法访问的目录
            pass
            
        return results
    
    def _matches_criteria(
        self,
        filename: str,
        filename_pattern: Optional[str],
        file_types: Optional[Set[str]]
    ) -> bool:
        """
        检查文件是否匹配搜索条件
        
        Args:
            filename: 文件名
            filename_pattern: 文件名模式
            file_types: 文件类型集合
            
        Returns:
            是否匹配
        """
        # 检查文件名模式匹配
        if filename_pattern and not fnmatch.fnmatch(filename.lower(), filename_pattern.lower()):
            return False
            
        # 检查文件类型匹配
        if file_types:
            file_ext = Path(filename).suffix.lower().lstrip('.')
            if file_ext not in file_types:
                return False
                
        return True
    
    def get_file_info(self, file_path: str) -> Optional[SearchResult]:
        """
        获取单个文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息，如果文件不存在或不在允许路径中则返回 None
        """
        # 检查文件是否在允许的路径中
        abs_file_path = os.path.abspath(file_path)
        is_allowed = False
        
        for allowed_path in self.allowed_paths:
            abs_allowed_path = os.path.abspath(allowed_path)
            if abs_file_path.startswith(abs_allowed_path):
                is_allowed = True
                break
                
        if not is_allowed:
            return None
            
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return None
            
        try:
            stat = os.stat(file_path)
            filename = os.path.basename(file_path)
            file_ext = Path(filename).suffix.lower().lstrip('.')
            
            return SearchResult(
                file_path=file_path,
                file_name=filename,
                file_size=stat.st_size,
                file_type=file_ext,
                modified_time=stat.st_mtime
            )
        except (OSError, IOError):
            return None


def search_documents(
    allowed_paths: List[str],
    filename_pattern: Optional[str] = None,
    file_types: Optional[List[str]] = None,
    max_results: int = 100
) -> List[dict]:
    """
    便捷的文档搜索函数
    
    Args:
        allowed_paths: 允许搜索的路径列表
        filename_pattern: 文件名模糊匹配模式
        file_types: 文件类型列表
        max_results: 最大返回结果数量
        
    Returns:
        搜索结果字典列表
    """
    searcher = FileSearcher(allowed_paths)
    results = searcher.search_files(filename_pattern, file_types, max_results)
    
    return [
        {
            "file_path": result.file_path,
            "file_name": result.file_name,
            "file_size": result.file_size,
            "file_type": result.file_type,
            "modified_time": result.modified_time
        }
        for result in results
    ]