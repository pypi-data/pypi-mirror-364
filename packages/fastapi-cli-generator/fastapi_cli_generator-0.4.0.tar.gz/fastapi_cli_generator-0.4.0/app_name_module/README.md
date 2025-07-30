# 大数据服务API脚手架

基于FastAPI的大数据团队数据服务接口脚手架，为业务方提供标准化的数据查询服务。

## 🚀 项目特点

- **生产就绪**: 完整的日志、异常处理、配置管理
- **类型安全**: 全面使用Pydantic进行数据验证
- **分层架构**: Repository-Service-Router三层架构
- **简洁实用**: 专注核心功能，易于扩展
- **开箱即用**: 包含完整配置和示例接口

## 🏗️ 技术栈

- **框架**: FastAPI + SQLAlchemy 2.0 (异步)
- **数据库**: MySQL (aiomysql驱动)
- **日志**: structlog (结构化日志)
- **配置**: Pydantic Settings (环境变量管理)
- **认证**: Bearer Token (固定API Key)

## 📁 项目结构

```
bigdata-api/                    # 项目根目录
├─ README.md                    # 项目文档
├─ .env                         # 开发环境配置
├─ .env.prod                    # 生产环境配置
├─ requirements.txt             # 依赖包列表
├─ Dockerfile                   # Docker构建文件
├─ src/                         # 源代码目录
│  ├─ main.py                   # FastAPI应用入口
│  ├─ core/                     # 核心配置
│  │  ├─ config.py              # 应用配置管理
│  │  └─ dependencies.py        # 全局依赖注入
│  ├─ shared/                   # 共享组件
│  │  ├─ database.py            # 数据库连接管理
│  │  ├─ logger.py              # 结构化日志组件
│  │  ├─ responses.py           # 标准响应格式
│  │  ├─ exceptions.py          # 异常处理机制
│  │  └─ utils.py               # 通用工具函数
│  └─ modules/                  # 业务模块
│     ├─ auth/                  # 认证模块
│     │  ├─ dependencies.py     # Bearer token验证
│     │  ├─ schemas.py          # 认证相关模型
│     │  └─ routers.py          # 认证接口
│     └─ items/                 # 数据查询模块(示例)
│        ├─ models.py           # 数据模型(企业信息)
│        ├─ repositories.py     # 数据访问层
│        ├─ services.py         # 业务逻辑层
│        ├─ schemas.py          # 请求响应模型
│        └─ routers.py          # 查询接口
└─ tests/                       # 测试目录
   ├─ conftest.py               # 测试配置
   └─ test_xx.py                # 测试用例
```

## ⚡ 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

编辑 `.env` 文件，配置数据库连接：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=fastapi_dev

# 固定API密钥
FIXED_API_KEY=ak_bigdata_internal_2024
```

### 3. 启动服务

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. 访问文档

- API文档: http://localhost:8080/docs
- 健康检查: http://localhost:8080/health

## 📋 API接口

### 认证测试

```bash
POST /api/auth/test-auth
Authorization: Bearer ak_bigdata_internal_2024
```

### 企业信息查询

```bash
POST /api/reports/enterprise-query
Authorization: Bearer ak_bigdata_internal_2024
Content-Type: application/json

{
    "enterprise_name": "阿里巴巴",
    "query_fields": ["basic_info", "business_status", "risk_info"],
    "region": "浙江省",
    "industry": "互联网"
}
```

**查询字段说明:**

- `basic_info`: 基本信息（法人、注册资本、成立日期、经营范围）
- `business_status`: 经营状况（经营状态、年营业额、员工数量）
- `risk_info`: 风险信息（风险等级、诉讼数量、行政处罚数量）

## 🔧 配置说明

### 环境变量

| 变量名        | 说明        | 默认值                   |
| ------------- | ----------- | ------------------------ |
| DEBUG_MODE    | 调试模式    | true                     |
| DB_HOST       | 数据库主机  | localhost                |
| DB_PORT       | 数据库端口  | 3306                     |
| DB_USER       | 数据库用户  | root                     |
| DB_PASSWORD   | 数据库密码  | 123456                   |
| DB_NAME       | 数据库名称  | fastapi_dev              |
| FIXED_API_KEY | 固定API密钥 | ak_bigdata_internal_2024 |
| LOG_LEVEL     | 日志级别    | DEBUG                    |
| LOG_FORMAT    | 日志格式    | json                     |

## 🐳 Docker部署

### 构建镜像

```bash
docker build -t bigdata-api .
```

### 运行容器

```bash
docker run -d --name bigdata-api -p 8080:20201 bigdata-api
```

## 🧪 测试

### 运行测试

```bash
pytest tests/
```

### 手动测试

```bash
# 测试认证
curl -X POST "http://localhost:8080/api/auth/test-auth" \
     -H "Authorization: Bearer ak_bigdata_internal_2024"

# 测试企业查询
curl -X POST "http://localhost:8080/api/reports/enterprise-query" \
     -H "Authorization: Bearer ak_bigdata_internal_2024" \
     -H "Content-Type: application/json" \
     -d '{"enterprise_name": "测试企业", "query_fields": ["basic_info"]}'
```

## 📝 开发指南

### 添加新的数据查询接口

1. **创建数据模型** (`models.py`)
2. **定义请求响应模型** (`schemas.py`)
3. **实现数据访问层** (`repositories.py`)
4. **编写业务逻辑** (`services.py`)
5. **添加路由接口** (`routers.py`)
6. **注册路由** (`main.py`)

### 标准响应格式

```json
{
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {...}
}
```

## 🔒 安全说明

- 使用固定API Key进行认证，适合内部系统调用
- 所有API请求都需要Bearer token认证
- 支持请求日志记录和链路追踪
- 统一的异常处理和错误响应

## 📄 许可证

MIT License
