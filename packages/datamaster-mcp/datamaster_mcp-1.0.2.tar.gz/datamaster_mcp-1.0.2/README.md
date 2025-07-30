# 📊 DataMaster MCP

> **超级数据分析MCP工具** - 为AI提供强大的数据分析能力

## 🎯 核心理念

**工具专注数据获取和计算，AI专注智能分析和洞察**

## 🚀 快速开始

### 用户安装

```bash
pip install datamaster-mcp
```

### 开发者安装

```bash
# 1. 克隆项目
git clone https://github.com/szqshan/DataMaster.git
cd DataMaster

# 2. 自动设置开发环境
python scripts/setup_dev.py

# 3. 测试环境
python scripts/setup_dev.py --test-only
```

### 基本使用

1. **配置 Claude Desktop**

将以下配置添加到 Claude Desktop 的配置文件中：

```json
{
  "mcpServers": {
    "datamaster-mcp": {
      "command": "python",
      "args": ["-m", "datamaster_mcp.main"],
      "env": {
        "PYTHONPATH": "/path/to/your/project"
      }
    }
  }
}
```

2. **使用示例**

```python
# 导入Excel数据
connect_data_source(
    source_type="excel",
    config={"file_path": "data.xlsx"},
    target_table="my_data"
)

# 执行SQL查询
execute_sql("SELECT * FROM my_data LIMIT 10")

# 数据分析
analyze_data(analysis_type="basic_stats", table_name="my_data")

# 导出结果
export_data(export_type="excel", data_source="my_data")
```

## ✨ 核心功能

### 📁 数据导入导出
- **Excel/CSV文件导入** - 支持多种格式和编码
- **数据库连接** - MySQL、PostgreSQL、MongoDB、SQLite
- **API数据获取** - RESTful API连接和数据提取
- **多格式导出** - Excel、CSV、JSON格式导出

### 🔍 数据查询分析
- **SQL查询执行** - 本地和外部数据库查询
- **数据统计分析** - 基础统计、相关性、异常值检测
- **数据质量检查** - 缺失值、重复值分析

### 🛠️ 数据处理
- **数据清洗** - 去重、填充缺失值
- **数据转换** - 类型转换、格式化
- **数据聚合** - 分组统计、汇总

## 📚 文档

### 用户文档
- [用户使用手册](用户使用手册.md)
- [本地测试指南](LOCAL_TEST_GUIDE.md)

### 开发者文档
- [开发者文档](开发者文档.md)
- [开发流程指南](DEVELOPMENT_WORKFLOW.md) 🆕
- [项目结构说明](项目结构说明.md)
- [PyPI发布指南](PYPI_RELEASE_GUIDE.md)

### 快速开发
```bash
# 设置开发环境
python scripts/setup_dev.py

# 运行测试
python scripts/setup_dev.py --test-only

# 发布新版本
python scripts/release.py 1.0.2
```

### 版本信息
- **[更新日志](CHANGELOG.md)** - 版本更新记录
- **[版本信息](VERSION.md)** - 当前版本详情

## 🛡️ 安全特性

- SQL注入防护
- 危险操作拦截
- 查询结果限制
- 参数验证
- 环境变量管理敏感信息

## 📞 支持

- 📖 查看[用户使用手册](用户使用手册.md)获取详细使用说明
- 🛠️ 查看[开发者文档](开发者文档.md)了解技术细节
- 📁 查看[项目结构说明](项目结构说明.md)了解文件组织
- 🐛 提交Issue报告问题或建议

---

**版本**: v1.0.0 | **状态**: ✅ 稳定版 | **更新**: 2025-01-24
