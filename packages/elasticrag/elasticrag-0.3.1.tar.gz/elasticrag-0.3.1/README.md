# ElasticRAG

ElasticRAG 是一个基于 Elasticsearch 的 RAG（Retrieval-Augmented Generation）系统，充分利用 Elasticsearch 的 ingest pipeline 功能来处理整个 RAG 工作流。

## 特性

- 🔍 基于 Elasticsearch 的向量搜索和文本搜索
- 🛠️ 使用 ingest pipeline 进行文档处理和向量化
- 👥 多用户支持和认证
- 🧠 多模型支持（OpenAI、HuggingFace 等）
- 📚 知识库（Collection）管理
- 🔄 混合搜索和 RRF（Reciprocal Rank Fusion）算法
- 📄 支持多种文档格式的文本分割
- ⚙️ 支持环境变量配置和命令行参数
- 🌐 可选的 Web 管理界面
- ✨ **新增**: 通过知识图谱和术语库进行增强检索

## 增强检索：结合知识图谱与术语库

ElasticRAG 支持通过集成知识图谱实体和术语库来增强用户查询，从而实现更高级的检索策略。这种混合方法结合了词法搜索、语义搜索和结构化知识，以获得更准确、更相关的结果。

### 工作原理

`Collection` 类中的 `query` 方法可以通过以下可选参数进行增强：

-   `k_hop_entities`: 一个列表的列表，表示从用户查询中提取的实体的 k-hop 邻居。例如：`[['实体_A1', '实体_A2'], ['实体_B1']]`，其中第一个列表包含 1-hop 邻居，第二个列表包含 2-hop 邻居。
-   `terminology`: 与查询相关的术语或同义词列表。

这些参数用于构建一个增强查询，该查询通过两种方式运作：

1.  **文本搜索增强**:
    *   **术语库**: 使用 `match_phrase_prefix` 查询查找包含相关术语的文档。这对于同义词和技术术语非常有用。
    *   **实体**: 使用 `terms` 查询匹配其文本块包含所提供 k-hop 实体的文档。相关性得分（`boost`）会随着跳数的增加而衰减，从而给予更近的实体更高的权重。

2.  **向量搜索增强**:
    *   术语和实体与原始查询文本一起被格式化为一个结构化的提示（Prompt）。
    *   这个增强的提示随后被转换为用于 KNN 搜索的嵌入向量。这丰富了查询的语义上下文，从而实现更好的相似度匹配。

### 灵活的权重配置

术语和实体对文本搜索得分的影响可以通过 `query` 方法中的 `boost_config` 参数进行自定义。该字典可以包含：

-   `terminology_boost`: 术语匹配的权重（默认值：`0.6`）。
-   `entity_base_boost`: 1-hop 实体匹配的基础权重（默认值：`0.4`）。
-   `entity_decay_factor`: 后续跳数的衰减因子（默认值：`0.6`）。

### 数据准备

要利用基于实体的检索，您必须在数据摄入过程中从文档中提取实体，并将它们存储在每个文本块的 `metadata.entities` 字段中。这通常需要在调用 `collection.add()` 之前使用命名实体识别（NER）模型来完成。

## 安装

### 基础安装

仅安装核心功能（CLI 命令行工具）：

```bash
uv add elasticrag
```

### 完整安装

包含 Web 管理界面：

```bash
uv add 'elasticrag[web]'
```

### 开发安装

包含开发工具：

```bash
uv add 'elasticrag[dev]'
```

### 全部安装

包含所有功能：

```bash
uv add 'elasticrag[all]'
```

### 从源码安装

```bash
git clone <repository-url>
cd elasticrag
uv sync
# 或安装包含 web 界面
uv sync --extra web
```

## 配置

### 环境变量配置

创建 `.env` 文件（从 `.env.example` 复制）：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# Elasticsearch Configuration
ELASTICSEARCH_HOST=http://localhost:9200

# Authentication
ELASTICRAG_USERNAME=your_username
ELASTICRAG_API_KEY=your_api_key

# Text Embedding Service
TEXT_EMBEDDING_URL=http://your-embedding-service:8080/embed
TEXT_EMBEDDING_API_KEY=your_embedding_api_key
```

### 命令行参数

你也可以通过命令行参数覆盖环境变量：

```bash
elasticrag --host localhost:9200 -u admin -k secret setup
```

## 快速开始

### 1. 初始化系统

```bash
elasticrag setup
```

### 2. 启动 Web 管理界面（可选）

⚠️ **注意**: Web 界面需要额外安装 gradio 依赖：

```bash
# 安装 web 依赖
uv add 'elasticrag[web]'

# 启动 web 界面
elasticrag server --port 7860
```

然后访问 http://localhost:7860 进入管理界面。

默认管理员账户：
- 用户名: admin
- 密码: admin123

### 3. 使用命令行工具

```bash
# 列出可用模型
elasticrag list-models

# 添加文档
elasticrag add document.pdf -c my_collection -m my_model

# 搜索文档
elasticrag search "your query" -c my_collection -m my_model -s 10
```

你也可以在搜索时加入知识图谱和术语库参数（注意：CLI当前不支持复杂数据结构，此功能主要通过API使用）：

```python
# API 调用示例
results = await collection.query(
    query_text="什么是机器学习？",
    terminology=["AI", "人工智能"],
    k_hop_entities=[
        ["深度学习", "神经网络"],  # 1-hop
        ["TensorFlow", "PyTorch"]              # 2-hop
    ],
    boost_config={
        "terminology_boost": 0.7,
        "entity_base_boost": 0.5,
        "entity_decay_factor": 0.5
    }
)
```

## CLI 命令参考

### 全局选项

- `--host`: Elasticsearch 主机地址
- `-u, --username`: 用户名
- `-k, --api-key`: API 密钥
- `-v, --verbose`: 启用详细日志

### 命令

- `setup`: 初始化系统
- `server`: 启动 Gradio Web 管理界面 **（需要安装 web 依赖）**
- `list-models`: 列出可用模型
- `list-users`: 列出所有用户
- `list-collections`: 列出所有集合
- `list-documents [collection] [model]`: 列出文档
- `add <file_path> [-c collection] [-m model]`: 添加文档
- `search <query> [-c collection] [-m model] [-s size]`: 搜索文档

#### server 命令选项

⚠️ **注意**: server 命令需要安装额外依赖：

```bash
uv add 'elasticrag[web]'
```

然后可以使用：

```bash
elasticrag server [选项]

选项:
  --port PORT           Web界面端口 (默认: 7860)
  --host HOST           Web界面主机 (默认: 0.0.0.0)
  --share               通过 Gradio 创建公共链接
  --admin-username USER 管理员用户名
  --admin-password PASS 管理员密码
```

## 依赖说明

### 核心依赖

- `elasticsearch>=8.0.0`: Elasticsearch 客户端
- `python-dotenv>=1.0.0`: 环境变量管理
- `aiohttp>=3.10.11`: 异步 HTTP 客户端

### 可选依赖

#### Web 界面 (`elasticrag[web]`)

- `gradio>=4.0.0`: Web 界面框架
- `pandas>=1.3.0`: 数据处理

#### 开发工具 (`elasticrag[dev]`)

- `pytest>=7.0.0`: 测试框架
- `pytest-asyncio>=0.21.0`: 异步测试支持
- `black>=23.0.0`: 代码格式化
- `isort>=5.12.0`: 导入排序

## Web 管理界面

### 安装 Web 依赖

```bash
uv add 'elasticrag[web]'
```

### 管理员功能

使用管理员账户登录后可以：

- **用户管理**: 查看、添加、删除用户
- **模型管理**: 查看、添加模型配置
- **系统监控**: 查看系统状态和资源使用

### 用户功能

使用普通用户账户登录后可以：

- **集合管理**: 查看自己的文档集合
- **文档管理**: 添加、删除、查看文档
- **搜索调试**: 在集合中搜索文档并查看结果

### 环境变量配置

Web 界面相关的环境变量：

```bash
# 管理员账户配置
ELASTICRAG_ADMIN_USERNAME=admin
ELASTICRAG_ADMIN_PASSWORD=admin123
```

## API 使用

```python
from elasticrag import Client

# 创建客户端
client = Client('http://localhost:9200')

# 认证用户
user = client.authenticate('username', 'api_key')

# 获取集合
collection = client.get_collection('my_collection', 'my_model')

# 添加文档
collection.add('doc_id', 'Document Name', text_content='Your content here')

# 搜索
results = await collection.query('your query')

# 使用知识图谱和术语库进行增强搜索
kg_results = await collection.query(
    query_text='your query',
    terminology=['term1', 'term2'],
    k_hop_entities=[['entity1'], ['entity2']],
    boost_config={'terminology_boost': 0.8}
)
```

## 开发

```bash
# 安装开发依赖
uv sync --extra dev

# 安装所有依赖（包括 web）
uv sync --extra all

# 运行测试
uv run pytest

# 代码格式化
uv run black .
uv run isort .
```

## 许可证

MIT License
