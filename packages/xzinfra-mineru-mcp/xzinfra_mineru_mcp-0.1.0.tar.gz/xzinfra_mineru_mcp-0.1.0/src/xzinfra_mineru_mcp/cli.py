import argparse
import sys

from .config import config
from .server import run_server

def main() -> None:
    
    """MCP服务器命令行入口"""
    parser = argparse.ArgumentParser(description="xzinfra-mineru-mcp 服务器")
    parser.add_argument(
        "--allowed", 
        action="append", 
        dest="allowed_paths",
        help="允许访问的路径，可以指定多个"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="文档解析API调用超时时间，单位秒，默认600秒（10分钟）"
    )
    
    args = parser.parse_args()

    config.validate_environment()

    if args.allowed_paths:
        config.set_allowed_paths(args.allowed_paths)
    
    try:
        config.set_default_timeout(args.timeout)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    
    run_server()


if __name__ == "__main__":
    main()