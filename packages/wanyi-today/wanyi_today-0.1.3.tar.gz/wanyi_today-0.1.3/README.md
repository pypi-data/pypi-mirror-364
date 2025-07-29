# Wanyi Today

一个基于 FastMCP 的演示服务器，提供基础工具和资源用于演示目的。

## 功能特性

- **加法工具**: 将两个数字相加
- **问候资源**: 获取个性化问候语
- **问候提示**: 生成不同风格的问候提示

## 安装

```bash
pip install wanyi-today
```

## 使用方法

运行服务器：

```bash
wanyi-today-server
```

或者直接使用 Python 运行：

```bash
python -m wanyi_today.main
```

## 开发

本项目使用 `uv` 进行依赖管理。

```bash
# 安装依赖
uv sync

# 运行服务器
uv run python -m wanyi_today.main
```

## 标准的 PyPI 包目录结构

一个标准的 PyPI 包应该具有以下目录结构：

```
wanyi_today/                    # 项目根目录
├── wanyi_today/               # 包目录（Python包）
│   ├── __init__.py           # 包初始化文件，定义版本等
│   ├── main.py               # 主模块文件
│   └── other_modules.py      # 其他模块文件
├── tests/                    # 测试目录（可选但推荐）
│   ├── __init__.py
│   └── test_main.py
├── docs/                     # 文档目录（可选）
├── dist/                     # 构建输出目录（自动生成）
│   ├── *.whl                # wheel分发包
│   └── *.tar.gz             # 源码分发包
├── pyproject.toml           # 项目配置文件（现代Python项目标准）
├── README.md                # 项目说明文档
├── LICENSE                  # 许可证文件
├── .gitignore              # Git忽略文件
└── uv.lock                 # 依赖锁定文件（使用uv时）
```

### 关键文件说明

1. **pyproject.toml**: 现代 Python 项目的配置文件，包含：
   - 项目元数据（名称、版本、描述等）
   - 依赖关系
   - 构建系统配置
   - 脚本入口点

2. **包目录结构**:
   - 包名使用下划线（如 `wanyi_today`）
   - PyPI 项目名可以使用连字符（如 `wanyi-today`）
   - `__init__.py` 文件标识这是一个 Python 包

3. **入口点配置**:
   ```toml
   [project.scripts]
   wanyi-today-server = "wanyi_today.main:main"
   ```
   这样用户安装后可以直接运行 `wanyi-today-server` 命令

4. **模块运行方式**:
   - `python -m wanyi_today.main` - 以模块方式运行
   - `wanyi-today-server` - 通过安装的脚本运行

## 上传到 PyPI 的完整流程

### 1. 准备工作

确保已安装必要的工具：
```bash
pip install build twine
```

### 2. 配置 PyPI 认证

在用户目录下创建 `.pypirc` 文件（如果还没有）：
```ini
[pypi]
username = __token__
password = your-api-token-here
```

### 3. 构建包

清理之前的构建文件并重新构建：
```powershell
# 清理旧的构建文件（PowerShell）
Remove-Item -Recurse -Force dist/, build/, *.egg-info/ -ErrorAction SilentlyContinue

# 使用 uv 构建（推荐）
uv build

# 或者使用标准工具构建
python -m build
```

### 4. 检查包

验证构建的包是否正确：
```bash
twine check dist/*
```

### 5. 上传到 PyPI

```bash
# 上传到正式 PyPI
twine upload dist/*

# 或者先上传到测试 PyPI（推荐）
twine upload --repository testpypi dist/*
```

### 6. 测试安装

从 PyPI 安装并测试：
```bash
# 从测试 PyPI 安装
pip install --index-url https://test.pypi.org/simple/ wanyi-today

# 从正式 PyPI 安装
pip install wanyi-today
```

### 7. 版本更新流程

当需要发布新版本时：

1. 更新 `pyproject.toml` 中的版本号
2. 更新 `wanyi_today/__init__.py` 中的版本号
3. 重新构建和上传：
   ```powershell
   uv build
   twine check dist/*
   twine upload dist/*
   ```

### 常见问题

- **403 错误**: 包名已被占用，需要选择不同的名称
- **400 错误**: 版本号已存在，需要增加版本号
- **认证失败**: 检查 API token 是否正确配置

## 许可证

MIT License