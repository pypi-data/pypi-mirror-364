# FastAPI CLI Generator

🚀 快速创建不同架构模式的FastAPI项目的命令行工具

[中文文档](README_CN.md) | [English Documentation](README.md)

## 功能特性

- 🏗️ **两种架构模式**: 功能分层架构 vs 模块化架构
- 🎯 **交互式CLI**: 友好的中文交互界面
- 📁 **完整项目结构**: 基于最佳实践的项目模板
- ⚡ **即开即用**: 生成的项目可以直接运行

## 安装

```bash
pip install fastapi-cli-generator
```

## 快速开始

### 交互式模式（推荐）
```bash
fastapi-create
```

### 命令行模式
```bash
# 指定模板创建
fastapi-create create my-project --template module
fastapi-create create my-project --template function

# 查看可用模板
fastapi-create list-templates
```

## 架构模式

### 1. 模块化架构 (module) - 推荐
按业务领域组织代码，每个模块包含完整的MVC结构：

```
my-project/
├── src/
│   ├── core/                 # 核心配置
│   ├── modules/              # 业务模块
│   │   ├── auth/             # 认证模块
│   │   ├── users/            # 用户管理
│   │   └── items/            # 项目管理
│   └── shared/               # 共享工具
├── tests/                    # 测试文件
└── requirements.txt
```

**适用场景:**
- 中大型项目
- 团队协作开发
- 需要清晰业务边界的项目

### 2. 功能分层架构 (function)
按技术层次组织代码：

```
my-project/
├── src/
│   ├── api/v1/endpoints/     # API端点
│   ├── core/                 # 核心配置
│   ├── db/repositories/      # 数据库操作
│   ├── models/               # 数据模型
│   ├── services/             # 业务逻辑
│   └── utils/                # 工具函数
├── tests/                    # 测试文件
└── requirements.txt
```

**适用场景:**
- 小型项目
- 学习和原型开发
- 简单的API服务

## 使用示例

### 创建项目
```bash
# 交互式创建（推荐）
fastapi-create

# 快速创建模块化项目
fastapi-create create my-api --template module

# 快速创建功能分层项目
fastapi-create create my-api --template function
```

### 运行项目
```bash
cd my-api
pip install -r requirements.txt
uvicorn src.main:app --reload
```

访问 http://localhost:8000/docs 查看API文档

## 开发

```bash
# 克隆项目
git clone https://github.com/xukache/fastapi-cli-generator.git
cd fastapi-cli-generator

# 安装开发依赖
pip install -e .

# 测试工具
fastapi-create --help
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
