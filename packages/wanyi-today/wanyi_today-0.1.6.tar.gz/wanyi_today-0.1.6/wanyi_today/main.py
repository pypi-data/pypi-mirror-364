"""
Wanyi Today - 一个基于 FastMCP 的演示服务器。

该服务器提供数字相加工具。
"""

from mcp.server.fastmcp import FastMCP

# 创建 MCP 服务器
mcp = FastMCP("Wanyi Today")


@mcp.tool()
def add(a: int, b: int) -> int:
    """将两个数字相加
    
    Args:
        a: 第一个数字
        b: 第二个数字
        
    Returns:
        两个数字的和
    """
    return a + b





def main():
    """服务器的主入口点"""
    # 根据 FastMCP 文档，使用 run 方法启动服务器
    mcp.run()


if __name__ == "__main__":
    main()