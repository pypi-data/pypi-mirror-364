# TensorFlow Serving Config Utilities

Python utilities for reading, writing, and validating TensorFlow Serving `models.config` files. This project provides a convenient way to programmatically manage your TensorFlow Serving model configurations using Python.

## 描述

该项目旨在提供一套 Python 工具，用于处理 TensorFlow Serving 的 `models.config` 文件。通过使用 Protobuf 定义，您可以轻松地创建、修改和验证模型服务器配置，从而实现自动化部署和管理 TensorFlow Serving 实例。

## 特性

- **生成 `models.config`**: 轻松创建符合 TensorFlow Serving 规范的 `models.config` 文件。
- **读取和解析**: 从现有 `models.config` 文件中读取并解析配置，方便程序化访问。
- **验证**: 利用 Protobuf 的结构化特性，确保配置文件的格式正确性。
- **模块化和可重用**: 代码遵循面向对象设计原则，易于集成和扩展。

## 安装

### 先决条件

- Python 3.8 或更高版本

### 使用 pip 安装

```bash
pip install tensorflow_serving_config
```

### 从源代码安装

1. 克隆仓库:
   ```bash
   git clone https://github.com/colorblank/tensorflow_serving_config.git
   cd tensorflow_serving_config
   ```
2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```
3. 安装项目:
   ```bash
   python setup.py install
   ```

## 依赖

本项目依赖以下库:

- `protobuf>=6.31.1`
- `grpcio>=1.73.1`
- `grpcio-tools==1.73.1` (用于生成 Protobuf 代码)
- `wheel`

## 使用示例

以下是一个简单的示例，展示如何使用此库生成并读取一个 `models.config` 文件：

```python
from google.protobuf import text_format
from tensorflow_serving.config import model_server_config_pb2
import os

# --- 生成一个示例 models.config 文件 ---
sample_config = model_server_config_pb2.ModelServerConfig()

# 添加第一个模型配置
model1 = sample_config.model_config_list.config.add()
model1.name = "example_model_a"
model1.base_path = "/var/lib/tensorflow_serving/models/example_model_a"
model1.model_platform = "tensorflow"
model1.model_version_policy.specific.versions.append(1)
model1.model_version_policy.specific.versions.append(2)

# 添加第二个模型配置
model2 = sample_config.model_config_list.config.add()
model2.name = "example_model_b"
model2.base_path = "/var/lib/tensorflow_serving/models/example_model_b"
model2.model_platform = "tensorflow"

config_file_path = "models.config"
with open(config_file_path, "w") as f:
    f.write(text_format.MessageToString(sample_config))
print(f"示例配置文件 '{config_file_path}' 生成成功！")

# --- 读取并解析 models.config 文件 ---
model_server_config = model_server_config_pb2.ModelServerConfig()
try:
    with open(config_file_path, "r") as f:
        config_content = f.read()
        text_format.Parse(config_content, model_server_config)

    print("\n配置文件 'models.config' 读取并解析成功！")
    print("\n--- 读取到的模型配置 ---")

    for model_config in model_server_config.model_config_list.config:
        print(f"模型名称: {model_config.name}")
        print(f"模型路径: {model_config.base_path}")
        print(f"模型平台: {model_config.model_platform}")
        if model_config.model_version_policy.HasField("specific"):
            versions = list(model_config.model_version_policy.specific.versions)
            print(f"版本策略: {versions}")
        else:
            print("版本策略: 默认 (Latest)")
        print("-" * 20)

except FileNotFoundError:
    print(f"错误: 找不到配置文件 '{config_file_path}'")
except text_format.ParseError as e:
    print(f"错误: 解析配置文件失败，请检查文件格式是否正确。错误详情: {e}")

# 清理生成的示例文件
if os.path.exists(config_file_path):
    os.remove(config_file_path)
    print(f"\n清理: 示例配置文件 '{config_file_path}' 已删除。")
```

## 许可证

本项目采用 Apache-2.0 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

- **作者**: Colorblank
- **邮箱**: colorblank@example.com
- **GitHub**: [https://github.com/colorblank/tensorflow_serving_config](https://github.com/colorblank/tensorflow_serving_config)
