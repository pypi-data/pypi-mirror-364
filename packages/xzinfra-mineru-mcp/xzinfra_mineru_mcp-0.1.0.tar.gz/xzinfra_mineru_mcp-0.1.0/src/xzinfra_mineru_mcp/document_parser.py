import os
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiohttp
import aiofiles
from dataclasses import dataclass


@dataclass
class ParseResult:
    """文档解析结果"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MinerUDocumentParser:
    """MinerU 文档解析器"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        初始化文档解析器
        
        Args:
            base_url: MinerU API 基础URL
            api_key: API 密钥
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.parse_url = f"{self.base_url}/file_parse"
    
    async def parse_documents(
        self,
        file_paths: List[str],
        return_images: bool = False,
        allowed_paths: Optional[List[str]] = None,
        timeout: int = 600
    ) -> ParseResult:
        """
        解析文档
        
        Args:
            file_paths: 本地文件路径列表
            return_images: 是否返回base64图片，默认为False
            allowed_paths: 允许访问的路径列表，用于安全检查
            timeout: API调用超时时间（秒），默认600秒（10分钟）
            
        Returns:
            解析结果
        """
        try:
            # 验证文件路径
            validation_result = self._validate_file_paths(file_paths, allowed_paths)
            if not validation_result.success:
                return validation_result
            
            # 准备请求数据
            data = aiohttp.FormData()
            
            # 添加文件
            for file_path in file_paths:
                async with aiofiles.open(file_path, 'rb') as f:
                    file_content = await f.read()
                    filename = os.path.basename(file_path)
                    data.add_field('files', file_content, filename=filename)
            
            # 添加其他参数（使用默认值）
            data.add_field('output_dir', './output')
            data.add_field('lang_list', 'ch')
            data.add_field('backend', 'pipeline')
            data.add_field('parse_method', 'auto')
            data.add_field('formula_enable', 'true')
            data.add_field('table_enable', 'true')
            data.add_field('return_md', 'true')
            data.add_field('return_middle_json', 'false')
            data.add_field('return_model_output', 'false')
            data.add_field('return_content_list', 'false')
            data.add_field('return_images', str(return_images).lower())
            data.add_field('start_page_id', '0')
            data.add_field('end_page_id', '99999')
            
            # 发送请求
            headers = {
                'Authorization': f'Bearer {self.api_key}' if self.api_key else None
            }
            # 移除 None 值的 headers
            headers = {k: v for k, v in headers.items() if v is not None}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.parse_url,
                    data=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status == 200:
                        result_data = await response.json()
                        return ParseResult(
                            success=True,
                            message="文档解析成功",
                            data=result_data
                        )
                    else:
                        error_text = await response.text()
                        return ParseResult(
                            success=False,
                            message=f"API请求失败，状态码: {response.status}",
                            error=error_text
                        )
                        
        except (asyncio.TimeoutError, aiohttp.ServerTimeoutError):
            return ParseResult(
                success=False,
                message=f"文档解析超时（{timeout}秒）。可以通过以下方式增加超时时间：\n"
                       f"1. 启动时使用 --timeout 参数：xzinfra-mineru-mcp --timeout {timeout * 2}\n"
                       f"2. 调用工具时设置 timeout 参数：parse_documents(file_paths=[...], timeout={timeout * 2})",
                error=f"API调用超时，当前超时设置: {timeout}秒"
            )
        except aiohttp.ClientError as e:
            return ParseResult(
                success=False,
                message="网络请求错误",
                error=str(e)
            )
        except Exception as e:
            return ParseResult(
                success=False,
                message="文档解析过程中发生错误",
                error=str(e)
            )
    
    def _validate_file_paths(
        self,
        file_paths: List[str],
        allowed_paths: Optional[List[str]] = None
    ) -> ParseResult:
        """
        验证文件路径
        
        Args:
            file_paths: 文件路径列表
            allowed_paths: 允许的路径列表
            
        Returns:
            验证结果
        """
        if not file_paths:
            return ParseResult(
                success=False,
                message="未提供文件路径"
            )
        
        # 检查文件是否存在
        missing_files = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
            elif not os.path.isfile(file_path):
                missing_files.append(f"{file_path} (不是文件)")
        
        if missing_files:
            return ParseResult(
                success=False,
                message=f"以下文件不存在或不是有效文件: {', '.join(missing_files)}"
            )
        
        # 检查路径权限（如果提供了允许路径列表）
        if allowed_paths:
            unauthorized_files = []
            for file_path in file_paths:
                abs_file_path = os.path.abspath(file_path)
                is_allowed = False
                
                for allowed_path in allowed_paths:
                    abs_allowed_path = os.path.abspath(allowed_path)
                    if abs_file_path.startswith(abs_allowed_path):
                        is_allowed = True
                        break
                
                if not is_allowed:
                    unauthorized_files.append(file_path)
            
            if unauthorized_files:
                return ParseResult(
                    success=False,
                    message=f"以下文件不在允许的路径中: {', '.join(unauthorized_files)}"
                )
        
        # 检查文件大小（可选的安全检查）
        large_files = []
        max_file_size = 100 * 1024 * 1024  # 100MB
        
        for file_path in file_paths:
            try:
                file_size = os.path.getsize(file_path)
                if file_size > max_file_size:
                    large_files.append(f"{file_path} ({file_size / 1024 / 1024:.1f}MB)")
            except OSError:
                pass
        
        if large_files:
            return ParseResult(
                success=False,
                message=f"以下文件过大 (超过100MB): {', '.join(large_files)}"
            )
        
        return ParseResult(success=True, message="文件路径验证通过")
    
    @staticmethod
    def is_supported_file(file_path: str) -> bool:
        """
        检查文件是否为支持的格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否支持
        """
        supported_extensions = {
            '.pdf', '.doc', '.docx', '.ppt', '.pptx',
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'
        }
        
        file_ext = Path(file_path).suffix.lower()
        return file_ext in supported_extensions


async def parse_documents_async(
    base_url: str,
    api_key: str,
    file_paths: List[str],
    return_images: bool = False,
    allowed_paths: Optional[List[str]] = None,
    timeout: int = 600
) -> Dict[str, Any]:
    """
    异步解析文档的便捷函数
    
    Args:
        base_url: MinerU API 基础URL
        api_key: API 密钥
        file_paths: 文件路径列表
        return_images: 是否返回base64图片
        allowed_paths: 允许的路径列表
        timeout: API调用超时时间（秒）
        
    Returns:
        解析结果字典
    """
    parser = MinerUDocumentParser(base_url, api_key)
    result = await parser.parse_documents(file_paths, return_images, allowed_paths, timeout)
    
    return {
        "success": result.success,
        "message": result.message,
        "data": result.data,
        "error": result.error,
        "files_processed": len(file_paths) if result.success else 0
    }


def parse_documents_sync(
    base_url: str,
    api_key: str,
    file_paths: List[str],
    return_images: bool = False,
    allowed_paths: Optional[List[str]] = None,
    timeout: int = 600
) -> Dict[str, Any]:
    """
    同步解析文档的便捷函数
    
    Args:
        base_url: MinerU API 基础URL
        api_key: API 密钥
        file_paths: 文件路径列表
        return_images: 是否返回base64图片
        allowed_paths: 允许的路径列表
        timeout: API调用超时时间（秒）
        
    Returns:
        解析结果字典
    """
    try:
        # 检查是否已经在事件循环中
        loop = asyncio.get_running_loop()
        # 如果已经在事件循环中，创建任务
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                _run_async_in_thread,
                base_url, api_key, file_paths, return_images, allowed_paths, timeout
            )
            return future.result()
    except RuntimeError:
        # 没有运行的事件循环，可以使用 asyncio.run()
        return asyncio.run(
            parse_documents_async(
                base_url, api_key, file_paths, return_images, allowed_paths, timeout
            )
        )


def _run_async_in_thread(
    base_url: str,
    api_key: str,
    file_paths: List[str],
    return_images: bool,
    allowed_paths: Optional[List[str]],
    timeout: int
) -> Dict[str, Any]:
    """在新线程中运行异步函数"""
    return asyncio.run(
        parse_documents_async(
            base_url, api_key, file_paths, return_images, allowed_paths, timeout
        )
    )