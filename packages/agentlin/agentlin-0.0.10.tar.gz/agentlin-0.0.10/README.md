# AgentLin

通用 Agent 架构

## 开始使用

### 1. 安装

```bash
pip install agentlin
```

本地安装

```bash
pip install -e .
```

### 2. 创建 `.env` 文件

复制 `.env.example` 文件为 `.env` 并填写所需的环境变量。

环境变量定义了访问 o3 模型的 API 密钥和其他配置。


### 3. 创建软链接

将公共数据目录 `/mnt/aime/datasets/agent/agent_data` 软链接到你本地项目的 `data` 目录下

```bash
ln -s /mnt/aime/datasets/agent/agent_data data
```

### 4. 运行应用程序

```bash
streamlit run chart_agent/chart_o3.py
```

注意：如果你不是在交互式建模的容器里运行的，需要挂一个代理服务将本地请求转发到北美：

```bash
cd tool_server
bash run_aime_proxy_server.sh
```

## 目录结构

```sh
agentlin/
├── core/                 # 核心架构组件
│   ├── agent_schema.py   # Agent 模式定义
│   ├── simulator.py      # 仿真器
│   └── types.py          # 数据类型定义
├── route/                # 路由和代理管理
│   ├── client.py         # 客户端
│   ├── mcp_proxy_*.py    # MCP 代理相关
│   └── *_task_manager.py # 任务管理器
└── tools/                # 工具集合
    ├── tool_aime.py      # AIME 工具
    ├── tool_calendar.py  # 日历工具
    ├── tool_code_interpreter.py # 代码解释器
    └── ...               # 其他工具

chart_agent/              # 图表 Agent
table_agent/              # 表格 Agent
tool_server/              # 工具服务器
docs/                     # 项目文档
data/                     # 数据文件，软链接到 /mnt/aime/datasets/agent/agent_data
├── aime/                 # AIME 相关数据
└── wencai/               # 问财相关数据
```




