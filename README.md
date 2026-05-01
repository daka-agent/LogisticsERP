# 🚚 物流教学软件 (Logistics Teaching Software)

> 面向本科物流管理专业的教学软件，支持采购、运输、仓储、库存全流程模拟，支持单人练习和多人协作。

[![GitHub stars](https://img.shields.io/github/stars/daka-agent/logistics-teaching?style=social)](https://github.com/daka-agent/logistics-teaching)
[![GitHub forks](https://img.shields.io/github/forks/daka-agent/logistics-teaching?style=social)](https://github.com/daka-agent/logistics-teaching)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.0+-green.svg)](https://vuejs.org/)

---

## 📖 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速启动](#快速启动)
- [项目结构](#项目结构)
- [功能模块](#功能模块)
- [部署方案](#部署方案)
- [API文档](#api文档)
- [常见问题](#常见问题)
- [后续规划](#后续规划)
- [贡献指南](#贡献指南)
- [开源协议](#开源协议)
- [联系方式](#联系方式)

---

## 📝 项目简介

本软件是一款面向**本科物流管理专业**的教学辅助工具，通过模拟真实物流企业的业务流程，帮助学生理解并掌握：

- ✅ 采购管理全流程（申请→审批→订单→验收→入库）
- ✅ 运输管理全流程（下单→审核→调度→运输→签收）
- ✅ 仓储管理全流程（入库→上架→出库→拣货→盘点）
- ✅ 库存管理（查询→预警→流水→分析）
- ✅ 财务结算（应付/应收管理）
- ✅ 合同管理（审批流）
- ✅ **多人协作模式**（5-6角色组队完成订单）
- ✅ **教学辅助功能**（场景管理、事件注入、自动评分）

### 🎯 适用对象

- 高校物流管理专业教师（课堂教学、实验教学）
- 物流管理专业学生（课程练习、流程模拟）
- 企业培训（新员工入职培训）

---

## ✨ 功能特性

### 核心业务模块

| 模块 | 功能 | 状态 |
|------|------|------|
| 🛒 **采购管理** | 采购申请、审批、订单、到货验收 | ✅ 已完成 |
| 🚛 **运输管理** | 运输订单、审核、调度、跟踪、签收 | ✅ 已完成 |
| �仓库管理** | 入库、上架、出库、拣货、移库、盘点 | ✅ 已完成 |
| 📦 **库存管理** | 库存查询、预警、流水、报表 | ✅ 已完成 |
| 💰 **财务结算** | 应付账款、应收账款、付款、收款 | ✅ 已完成 |
| 📄 **合同管理** | 采购合同、运输合同、审批流 | ✅ 已完成 |

### 教学特色功能

| 功能 | 说明 | 状态 |
|------|------|------|
| 👥 **多人协作** | 5-6角色组队，实时协作完成订单 | ✅ 已完成 |
| 🎯 **教学场景** | 预设5种典型物流场景，教师可自定义 | ✅ 已完成 |
| ⚡ **突发事件** | 教师端注入突发事件，测试学生应变能力 | ✅ 已完成 |
| 📊 **自动评分** | 按模块+操作自动评分，多维度评估 | ✅ 已完成 |
| 📝 **操作日志** | 记录所有业务操作，支持回放分析 | ✅ 已完成 |
| 📈 **数据报表** | ECharts可视化报表（库存周转率、运输准时率等） | ✅ 已完成 |

### 技术特性

- 📱 **响应式设计**：支持PC、平板、手机访问
- 🐳 **Docker支持**：一键部署，环境一致
- 📤 **数据导出**：支持Excel/CSV格式导出
- 🔐 **权限管理**：基于角色的访问控制（RBAC）
- 🌐 **实时通信**：Flask-SocketIO实现实时协作

---

## 🛠 技术栈

### 后端

- **框架**：[Flask](https://flask.palletsprojects.com/) 3.0+
- **ORM**：[SQLAlchemy](https://www.sqlalchemy.org/)
- **认证**：[Flask-Login](https://flask-login.readthedocs.io/)
- **实时通信**：[Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- **数据库**：SQLite（开发环境）
- **密码加密**：bcrypt

### 前端

- **框架**：[Vue 3](https://vuejs.org/)
- **构建工具**：[Vite](https://vitejs.dev/)
- **UI组件库**：[Element Plus](https://element-plus.org/)
- **状态管理**：[Pinia](https://pinia.vuejs.org/)
- **路由**：[Vue Router](https://router.vuejs.org/)
- **HTTP客户端**：[Axios](https://axios-http.com/)
- **图表**：[ECharts](https://echarts.apache.org/)

---

## 🚀 快速启动

### 方式一：单机启动（推荐首次体验）

#### 环境要求

- Python 3.10+
- Node.js 18+

#### 步骤

**1. 克隆项目**

```bash
git clone https://github.com/daka-agent/logistics-teaching.git
cd logistics-teaching
```

**2. 启动后端**

打开**第一个终端**：

```bash
cd backend
pip install -r requirements.txt
python run.py
```

✅ 看到 `Running on http://127.0.0.1:5000` 表示启动成功

**3. 启动前端**

打开**第二个终端**：

```bash
cd frontend
npm install
npm run dev
```

✅ 看到 `Local: http://localhost:5173/` 表示启动成功

**4. 访问系统**

打开浏览器，访问：`http://localhost:5173`

**5. 登录**

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员/教师 |

---

### 方式二：Docker一键启动

#### 环境要求

- Docker
- Docker Compose

#### 步骤

```bash
# 克隆项目
git clone https://github.com/daka-agent/logistics-teaching.git
cd logistics-teaching

# 一键启动
docker-compose up -d --build

# 查看状态
docker-compose ps
```

访问：`http://localhost`

**常用命令**

```bash
# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart
```

---

### 方式三：校园网部署（多人使用）

详见 [部署文档](部署文档.md) 或 [08-部署方案.md](08-部署方案.md)

---

## 📁 项目结构

```
物流教学软件/
├── backend/                      # 后端Flask应用
│   ├── app/
│   │   ├── __init__.py           # Flask应用工厂
│   │   ├── config.py             # 配置文件
│   │   ├── models/               # 数据库模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # 用户、角色
│   │   │   ├── purchase.py       # 采购申请、订单
│   │   │   ├── transport.py      # 运输订单、跟踪
│   │   │   ├── warehouse.py      # 仓库、库区、货位
│   │   │   ├── inventory.py      # 库存、入库、出库
│   │   │   ├── finance.py        # 应付、应收
│   │   │   ├── contract.py       # 采购合同、运输合同
│   │   │   ├── collab.py         # 操作日志、评分
│   │   │   └── ...
│   │   ├── api/                  # API路由
│   │   │   ├── auth.py           # 认证API
│   │   │   ├── purchase.py       # 采购API
│   │   │   ├── transport.py      # 运输API
│   │   │   ├── warehouse.py      # 仓储API
│   │   │   ├── inventory.py      # 库存API
│   │   │   ├── finance.py        # 财务API
│   │   │   ├── contracts.py      # 合同API
│   │   │   ├── collab.py         # 协作API
│   │   │   ├── teaching.py       # 教学场景API
│   │   │   └── ...
│   │   ├── socket/               # WebSocket
│   │   │   └── __init__.py       # SocketIO事件处理
│   │   ├── utils/                # 工具函数
│   │   │   ├── scoring.py        # 自动评分引擎
│   │   │   └── ...
│   │   └── extensions.py         # 扩展（db、login、socket）
│   ├── run.py                    # 启动文件
│   ├── reset_db.py               # 数据库重置脚本
│   └── requirements.txt         # Python依赖
│
├── frontend/                     # 前端Vue应用
│   ├── src/
│   │   ├── main.js               # Vue入口
│   │   ├── App.vue               # 根组件
│   │   ├── views/                # 页面组件
│   │   │   ├── LoginView.vue     # 登录页
│   │   │   ├── HomeView.vue      # 数据看板
│   │   │   ├── PurchaseView.vue  # 采购管理
│   │   │   ├── TransportView.vue # 运输管理
│   │   │   ├── WarehouseView.vue # 仓储管理
│   │   │   ├── InventoryView.vue # 库存管理
│   │   │   ├── FinanceView.vue   # 财务管理
│   │   │   ├── ContractView.vue  # 合同管理
│   │   │   ├── RoomHallView.vue  # 协作大厅
│   │   │   ├── teacher/          # 教师后台
│   │   │   └── ...
│   │   ├── router/               # 路由配置
│   │   ├── stores/               # Pinia状态管理
│   │   ├── api/                  # API请求
│   │   └── styles/               # 全局样式
│   ├── package.json
│   └── vite.config.js
│
├── docs/                         # 文档
│   ├── 01-方案设计文档.md
│   ├── 02-数据库设计.sql
│   ├── 03-系统架构图.html
│   ├── 04-界面线框图.html
│   ├── 05-开发任务清单.md
│   ├── 06-API接口设计.md
│   ├── 07-后续完善建议.md
│   ├── 08-部署方案.md
│   └── 部署文档.md
│
├── docker-compose.yml            # Docker Compose配置
├── .gitignore                   # Git忽略文件
├── LICENSE                      # 开源协议
└── README.md                    # 本文件
```

---

## 📦 功能模块详解

### 1. 采购管理

**流程**：采购申请 → 审批 → 生成订单 → 到货验收 → 入库

**核心功能**：
- 采购申请（创建、提交、审批）
- 采购订单（生成、确认、完成）
- 到货验收（验收、生成入库单）
- 评分规则：申请+10分、审批+5分、验收+10分

### 2. 运输管理

**流程**：下单 → 审核 → 调度 → 运输跟踪 → 签收 → 完成

**核心功能**：
- 运输订单（创建、审核、调度、状态更新）
- 车辆调度（分配车辆、司机）
- 运输跟踪（添加跟踪记录、更新状态）
- 运费计算（按重量/体积/距离）

### 3. 仓储管理

**流程**：入库 → 验收 → 上架 → 出库 → 拣货 → 发货

**核心功能**：
- 入库管理（创建入库单、验收、上架）
- 出库管理（创建出库单、拣货、发货）
- 库内作业（移库、盘点）

### 4. 库存管理

**核心功能**：
- 库存查询（多条件筛选）
- 库存预警（最低/最高库存预警）
- 库存流水（所有变动记录）
- 库存报表（ECharts图表）

### 5. 财务结算

**核心功能**：
- 应付账款（基于采购订单自动生成）
- 应收账款（基于运输订单自动生成）
- 付款/收款操作
- 财务统计（ Dashboard 展示）

### 6. 合同管理

**核心功能**：
- 采购合同（基于采购订单生成、审批流）
- 运输合同（基于运输订单生成、审批流）
- 合同终止

### 7. 多人协作

**核心功能**：
- 创建协作房间
- 选择角色加入房间
- 实时同步订单状态
- WebSocket推送通知

### 8. 教学辅助

**核心功能**：
- 教学场景管理（CRUD + 5个预设场景）
- 突发事件注入（6种事件类型）
- 操作日志记录（所有操作自动记录）
- 自动评分引擎（正确性+完整性+效率）
- 进度监控（教师查看各组进度）
- 成绩统计（表格+导出）

---

## 🌐 部署方案

### 方案对比

| 方案 | 适用场景 | 难度 | 推荐指数 |
|------|---------|------|---------|
| **A. 单机启动** | 个人演示、课堂投屏 | ⭐ | ⭐⭐⭐⭐⭐ |
| **B. 校园网部署** | 实验室/机房教学 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **C. 云服务器部署** | 远程教学/在线课程 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **D. Docker部署** | 快速复制到多台机器 | ⭐⭐ | ⭐⭐⭐⭐ |

### 详细部署文档

- [单机启动详解](08-部署方案.md#三方案a单机快速启动)
- [校园网部署指南](08-部署方案.md#四方案b校园网实验室部署推荐)
- [云服务器部署指南](08-部署方案.md#五方案c云服务器部署远程教学用)
- [Docker部署指南](08-部署方案.md#六方案d-docker-一键部署)

---

## 📚 API文档

详细的API接口设计文档请参考：

- [06-API接口设计.md](docs/06-API接口设计.md)

### API响应格式

所有API统一使用以下格式：

```json
{
  "code": 200,
  "message": " success",
  "data": { ... }
}
```

**常用API端点**：

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | `/api/auth/login` | 登录 |
| 采购 | `/api/purchase-requests` | 采购申请 |
| 运输 | `/api/orders` | 运输订单 |
| 仓储 | `/api/inbound-orders` | 入库单 |
| 库存 | `/api/inventory` | 库存查询 |
| 财务 | `/api/finance/overview` | 财务概览 |
| 合同 | `/api/contracts/purchase` | 采购合同 |

---

## ❓ 常见问题

### 1. 登录显示500错误

**原因**：后端服务未启动

**解决**：
```bash
cd backend
python run.py
```

### 2. 端口被占用

**后端（5000端口）**：
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

**前端（5173端口）**：

编辑 `frontend/vite.config.js`，修改端口：
```javascript
export default defineConfig({
  server: {
    port: 5174,
  }
})
```

### 3. 数据库损坏

**解决**：
```bash
cd backend
python reset_db.py
```

### 4. 前端编译失败

**解决**：
```bash
cd frontend
rm -rf node_modules
npm install
```

### 5. WebSocket连接失败

**检查**：
- 后端是否启动
- Nginx配置是否支持WebSocket（生产环境）

---

## 🔮 后续规划

### V2.0 计划开发功能

#### 高优先级（教学核心价值）

- [ ] **审批工作流引擎**：可视化流程设计器、多节点审批、条件分支
- [ ] **操作回放**：时间线形式回放学生操作过程
- [ ] **错误提示与引导**：操作错误时给出提示，引导学生纠正
- [ ] **权限管理细化**：数据权限、操作权限、字段权限

#### 中优先级（接近真实ERP）

- [ ] **通知提醒系统**：站内信、邮件通知、微信/钉钉机器人
- [ ] **报表与分析增强**：供应商评分、客户贡献度、库存龄期分析
- [ ] **条码/二维码支持**：打印商品条码、库位二维码、移动端扫描
- [ ] **数据导入功能**：Excel批量导入商品、客户、供应商

详见 [07-后续完善建议.md](docs/07-后续完善建议.md)

---

## 🤝 贡献指南

我们欢迎任何形式的贡献！

### 如何贡献

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

### 贡献规范

- 遵循现有代码风格
- 添加必要的注释
- 更新相关文档
- 确保测试通过

### 报告Bug

请使用 [GitHub Issues](https://github.com/daka-agent/logistics-teaching/issues) 报告Bug，并包含：

- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 截图（如果有）

---

## 📄 开源协议

本项目采用 **MIT 开源协议** - 详见 [LICENSE](LICENSE) 文件

你可以自由地：
- ✅ 使用（用于教学、研究、商业用途）
- ✅ 修改（根据自己的需求定制）
- ✅ 分发（分享给其他人）
- ✅ 私人使用

只需要：
- 📝 保留版权声明和许可证

---

## 📧 联系方式

- **作者**：大卡 (daka-agent)
- **GitHub**：[@daka-agent](https://github.com/daka-agent)
- **Email**：（zhangdaka@gdufe.edu.cn）

---

## 🙏 致谢

感谢以下开源项目的支持：

- [Flask](https://flask.palletsprojects.com/)
- [Vue 3](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [ECharts](https://echarts.apache.org/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)

---

## 📊 项目统计

![GitHub last commit](https://img.shields.io/github/last-commit/daka-agent/logistics-teaching)
![GitHub repo size](https://img.shields.io/github/repo-size/daka-agent/logistics-teaching)
![GitHub language count](https://img.shields.io/github/languages/count/daka-agent/logistics-teaching)
![GitHub top language](https://img.shields.io/github/languages/top/daka-agent/logistics-teaching)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个星标！ ⭐**

Made with ❤️ by [daka-agent](https://github.com/daka-agent)

</div>
