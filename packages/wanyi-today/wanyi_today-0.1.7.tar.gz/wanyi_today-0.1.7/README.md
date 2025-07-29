# Wanyi Today - MCP Server

一个基于 FastMCP 的演示服务器，提供数字相加功能和神秘的答案之书体验。

## 功能特性

### 工具 (Tools)
- `add(a, b)` - 将两个数字相加
- `answer_book(user_input)` - 答案之书，提供神秘回答

### 答案之书使用指南

答案之书是一个神秘的占卜工具，当你在输入中包含特定关键词时，它会为你提供简短而模棱两可的神秘回答。

**触发方式：**
- 使用 `/答案之书` 指令
- 在文本中包含 `答案之书` 关键词

**示例用法：**
- "我想问答案之书一个问题"
- "/答案之书 今天运势如何"
- "答案之书，我应该做什么决定"

**回答风格：**
答案之书会返回简短、模棱两可的神秘回答，如：
- "时机未到"
- "答案就在你心中" 
- "或许是，或许不是"
- "静待花开"

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