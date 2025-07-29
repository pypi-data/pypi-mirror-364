import traceback
from typing import List, Optional, Annotated

from fastmcp import FastMCP
from .config import config
from .file_search import search_documents
from .document_parser import parse_documents_sync

mcp =FastMCP(
    name="MinerU File to Markdown Converter",
    instructions="""
    一个将文档转化工具，可以将文档转化成Markdown、Json等格式，支持多种文件格式，包括
    PDF、Word、PPT以及图片格式（JPG、PNG、JPEG）。

    系统工具:
    get_ocr_languages: 获取OCR支持的语言列表
    find_document_path: 在配置的本地文档目录中搜索相关的文件路径
    parse_documents: 解析本地文档,自动读取内容
    """
)


@mcp.tool()
def find_document_path(
    filename_pattern: Annotated[Optional[str], "文件名模糊匹配模式，支持通配符 * 和 ?，例如 '*.pdf' 或 'report*'"] = None,
    file_types: Annotated[Optional[List[str]], "文件类型列表，例如 ['pdf', 'docx', 'txt', 'jpg', 'png']"] = None,
    max_results: Annotated[int, "最大返回结果数量，默认50"] = 50
) -> dict:
    """
    在配置的本地文档目录中搜索相关的文件路径
    
    Args:
        filename_pattern: 文件名模糊匹配模式，支持通配符 * 和 ?，例如 "*.pdf" 或 "report*"
        file_types: 文件类型列表，例如 ["pdf", "docx", "txt", "jpg", "png"]
        max_results: 最大返回结果数量，默认50
        
    Returns:
        包含搜索结果的字典，格式为:
        {
            "success": bool,
            "message": str,
            "results": [
                {
                    "file_path": str,
                    "file_name": str, 
                    "file_size": int,
                    "file_type": str,
                    "modified_time": float
                }
            ],
            "total_found": int
        }
    """
    try:
        if not config.allowed_paths:
            return {
                "success": False,
                "message": "未配置允许搜索的路径，请使用 --allowed 参数指定",
                "results": [],
                "total_found": 0
            }
        
        if not filename_pattern and not file_types:
            return {
                "success": False,
                "message": "至少需要提供 filename_pattern 或 file_types 中的一个搜索条件",
                "results": [],
                "total_found": 0
            }
        
        results = search_documents(
            allowed_paths=config.allowed_paths,
            filename_pattern=filename_pattern,
            file_types=file_types,
            max_results=max_results
        )
        
        return {
            "success": True,
            "message": f"找到 {len(results)} 个匹配的文件",
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"搜索文件时发生错误: {str(e)}",
            "results": [],
            "total_found": 0
        }


@mcp.tool()
def parse_documents(
    file_paths: Annotated[List[str], "本地文件路径字符串列表，支持PDF、Word、PPT以及图片格式"],
    return_images: Annotated[bool, "是否返回base64图片，默认为False"] = False,
    timeout: Annotated[Optional[int], "API调用超时时间（秒），不指定则使用服务器默认超时时间"] = None
) -> dict:
    """
    解析本地文档,自动读取内容并转换为Markdown格式
    
    Args:
        file_paths: 本地文件路径字符串列表，支持PDF、Word、PPT以及图片格式
        return_images: 是否返回base64图片，默认为False
        timeout: API调用超时时间（秒），不指定则使用服务器默认超时时间
        
    Returns:
        包含解析结果的字典，格式为:
        {
            "success": bool,
            "message": str,
            "data": dict,  # MinerU API返回的解析结果
            "error": str,  # 错误信息（如果有）
            "files_processed": int  # 成功处理的文件数量
        }
    """
    try:
        # 验证环境配置
        if not config.mineru_base_url or not config.mineru_api_key:
            try:
                config.validate_environment()
            except ValueError as e:
                return {
                    "success": False,
                    "message": f"配置错误: {str(e)}",
                    "data": None,
                    "error": str(e),
                    "files_processed": 0
                }
        
        # 验证输入参数
        if not file_paths:
            return {
                "success": False,
                "message": "未提供文件路径",
                "data": None,
                "error": "file_paths 参数不能为空",
                "files_processed": 0
            }
        
        # 检查文件格式支持
        from .document_parser import MinerUDocumentParser
        unsupported_files = []
        for file_path in file_paths:
            if not MinerUDocumentParser.is_supported_file(file_path):
                unsupported_files.append(file_path)
        
        if unsupported_files:
            return {
                "success": False,
                "message": f"不支持的文件格式: {', '.join(unsupported_files)}",
                "data": None,
                "error": "只支持PDF、Word、PPT以及图片格式(JPG、PNG、JPEG等)",
                "files_processed": 0
            }
        
        # 确定超时时间
        actual_timeout = timeout if timeout is not None else config.default_timeout
        
        # 调用文档解析服务
        result = parse_documents_sync(
            base_url=config.mineru_base_url,
            api_key=config.mineru_api_key,
            file_paths=file_paths,
            return_images=return_images,
            allowed_paths=config.allowed_paths if config.allowed_paths else None,
            timeout=actual_timeout
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"解析文档时发生未知错误: {str(e)}",
            "data": None,
            "error": str(e),
            "files_processed": 0
        }


def run_server():
    try:
        mcp.run("stdio")
    except Exception:
        traceback.print_exc()
    finally:
        clean_resources()
        
        
def clean_resources():
    pass