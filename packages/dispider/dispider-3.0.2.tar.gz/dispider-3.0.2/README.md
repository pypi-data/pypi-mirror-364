# Dispider

一个帮助初学者快速批量部署爬虫并管理任务的工具包。

## 安装

```bash
pip install dispider
```

## 快速开始

```python
from dispider import Dispider

# 初始化客户端
client = Dispider(
    username="your_username",
    password="your_password"
)

# 获取任务
task = client.get_next_task()
if task:
    # 处理任务
    result = {"data": "scraped_data"}
    client.submit_task_result(result)
```

## 主要功能

- 🚀 自动任务分发和负载均衡
- 📊 实时任务进度监控
- 🔄 自动重试机制
- 🐳 Docker容器化部署
- 🌐 分布式爬虫管理

## 版本历史

### v3.1.0
- 修复API路由问题
- 优化网络连接处理

### v3.0.2
- 基础功能实现