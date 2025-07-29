# Wanyi Today - MCP Server

一个基于 FastMCP 的演示服务器，提供基础工具和资源用于演示目的。

## 功能特性

### 工具 (Tools)
- `add(a, b)` - 将两个数字相加
- `multiply(a, b)` - 将两个数字相乘

### 资源 (Resources)
- `greeting://{name}` - 获取个性化问候语
- `info://server` - 获取服务器信息

### 提示 (Prompts)
- `greet_user(name, style)` - 生成问候提示

## 安装

```bash
pip install wanyi-today
```

或者使用 uvx：

```bash
uvx wanyi-today
```

## 使用方法

### 作为 MCP 服务器运行

```bash
wanyi-today
```

### 在 Claude Desktop 中配置

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "wanyi-today": {
      "command": "uvx",
      "args": ["wanyi-today"]
    }
  }
}
```

### 开发模式

```bash
# 克隆仓库
git clone https://github.com/Ryan7t/wanyi-today.git
cd wanyi-today

# 安装依赖
pip install -e .

# 运行服务器
python -m wanyi_today
```

## 测试

使用 MCP Inspector 测试服务器：

```bash
npx @modelcontextprotocol/inspector uvx wanyi-today
```

## 许可证

MIT License