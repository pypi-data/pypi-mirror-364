"""
Wanyi Today - 一个基于 FastMCP 的演示服务器。

该服务器提供基础工具和资源用于演示目的。
"""

from mcp.server.fastmcp import FastMCP

# 创建 MCP 服务器
mcp = FastMCP("Wanyi Today")


# 添加加法工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """将两个数字相加"""
    return a + b


# 添加动态问候资源
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """获取个性化问候语"""
    return f"你好，{name}！"


# 添加问候提示
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """生成问候提示"""
    styles = {
        "friendly": "请写一个温暖友好的问候语",
        "formal": "请写一个正式专业的问候语",
        "casual": "请写一个随意轻松的问候语",
    }

    return f"{styles.get(style, styles['friendly'])}，对象是名叫 {name} 的人。"


def main():
    """服务器的主入口点。"""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()