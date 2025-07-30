# Host Image Backup

<div align="center">
  <a href="README.md"><b>English</b></a> | <a href="README.zh-CN.md"><b>简体中文</b></a>
</div>

<p align="center">
  <a href="https://pypi.org/project/host-image-backup/">
    <img src="https://img.shields.io/pypi/v/host-image-backup?color=blue" alt="PyPI">
  </a>
  <img src="https://img.shields.io/github/stars/WayneXuCN/HostImageBackup?style=social" alt="GitHub stars">
  <img src="https://img.shields.io/github/license/WayneXuCN/HostImageBackup" alt="License">
  <img src="https://img.shields.io/github/actions/workflow/status/WayneXuCN/HostImageBackup/ci.yml?branch=main" alt="CI">
  <img src="https://img.shields.io/codecov/c/github/WayneXuCN/HostImageBackup?label=coverage" alt="Coverage">
</p>

> **Host Image Backup** 是一个功能强大的模块化 Python 命令行工具，帮助您轻松地从各种图床服务备份图片到本地机器。

---

## ✨ 功能特性

- 🏗️ **模块化架构** - 易于扩展新的图床提供商
- 🌐 **多图床支持** - 阿里云 OSS、腾讯云 COS、SM.MS、Imgur、GitHub
- 📊 **可视化进度** - 美观的备份操作进度条
- 🎨 **丰富 CLI 界面** - 直观的命令行体验
- ⚙️ **灵活配置** - 基于 YAML 的配置管理
- 🔄 **断点续传** - 无缝继续中断的传输
- 📝 **全面日志** - 详细的操作日志记录
- 🧪 **充分测试** - 全面的测试覆盖确保可靠性

---

## 🚀 支持的图床

| 图床       | 功能特性                     | 说明                       |
|-----------|------------------------------|----------------------------|
| **OSS**   | ✅ 列表、备份、续传、跳过   | 需要阿里云凭据             |
| **COS**   | ✅ 列表、备份、续传、跳过   | 需要腾讯云凭据             |
| **SM.MS** | ✅ 列表、备份               | 公共 API，有速率限制       |
| **Imgur** | ✅ 列表、备份               | 需要 Imgur 客户端 ID/密钥  |
| **GitHub**| ✅ 列表、备份               | 需要 GitHub token 和权限   |

---

## 📦 安装

### 环境要求

- **Python 3.10+** (推荐最新稳定版本)
- **pip** 或 **uv** 包管理器
- **虚拟环境** (强烈推荐)

### 快速安装

```bash
# 从 PyPI 安装
pip install host-image-backup

# 或升级到最新版本
pip install --upgrade host-image-backup

# 验证安装
host-image-backup --help
# 或使用短别名
hib --help
```

### 开发版安装

```bash
# 克隆仓库
git clone https://github.com/WayneXuCN/HostImageBackup.git
cd HostImageBackup

# 使用 uv 安装开发依赖（推荐）
uv lock  # 生成锁定文件
uv sync --all-extras # 安装所有额外依赖（dev）

# 或使用 pip
pip install -e ".[dev]"
```

---

## ⚙️ 配置

### 快速开始

```bash
# 初始化配置文件
host-image-backup init
# 或使用短别名
hib init

# 编辑生成的配置文件
# Linux/macOS: ~/.config/host-image-backup/config.yaml
# Windows: %APPDATA%/host-image-backup/config.yaml
```

### 配置结构

```yaml
# 全局设置
default_output_dir: "./backup"
max_concurrent_downloads: 5
timeout: 30
retry_count: 3
log_level: "INFO"

# 图床配置
providers:
  oss:
    enabled: true
    access_key_id: "your_access_key"
    access_key_secret: "your_secret_key"
    bucket: "your_bucket_name"
    endpoint: "oss-cn-hangzhou.aliyuncs.com"
    prefix: "images/"
  
  cos:
    enabled: false
    secret_id: "your_secret_id"
    secret_key: "your_secret_key"
    bucket: "your_bucket_name"
    region: "ap-guangzhou"
    prefix: "images/"
  
  sms:
    enabled: false
    api_token: "your_api_token"
  
  imgur:
    enabled: false
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    access_token: "your_access_token"
    refresh_token: "your_refresh_token"
  
  github:
    enabled: false
    token: "ghp_your_personal_access_token"
    owner: "your_username"
    repo: "your_repository"
    path: "images"  # 可选：指定文件夹路径
```

### 配置字段参考

| 字段                     | 描述                        | 必需 | 默认值 |
|---------------------------|-----------------------------|------|--------|
| **全局设置**             |                             |      |        |
| `default_output_dir`      | 默认备份目录                | 否   | "./backup" |
| `max_concurrent_downloads`| 最大并发下载数              | 否   | 5      |
| `timeout`                 | 请求超时时间（秒）          | 否   | 30     |
| `retry_count`             | 失败重试次数                | 否   | 3      |
| `log_level`               | 日志级别                    | 否   | "INFO" |
| **OSS 配置**             |                             |      |        |
| `access_key_id`           | 阿里云 OSS access key ID    | 是   | -      |
| `access_key_secret`       | 阿里云 OSS access key secret| 是   | -      |
| `bucket`                  | OSS 存储桶名称              | 是   | -      |
| `endpoint`                | OSS 端点 URL                | 是   | -      |
| `prefix`                  | 图片路径前缀                | 否   | ""     |
| **COS 配置**             |                             |      |        |
| `secret_id`               | 腾讯云 COS secret ID        | 是   | -      |
| `secret_key`              | 腾讯云 COS secret key       | 是   | -      |
| `bucket`                  | COS 存储桶名称              | 是   | -      |
| `region`                  | COS 区域                    | 是   | -      |
| **SM.MS 配置**           |                             |      |        |
| `api_token`               | SM.MS API token             | 是   | -      |
| **Imgur 配置**           |                             |      |        |
| `client_id`               | Imgur 应用客户端 ID         | 是   | -      |
| `client_secret`           | Imgur 应用客户端密钥        | 是   | -      |
| `access_token`            | Imgur 用户访问令牌          | 是   | -      |
| `refresh_token`           | Imgur 刷新令牌              | 否   | -      |
| **GitHub 配置**          |                             |      |        |
| `token`                   | GitHub 个人访问令牌         | 是   | -      |
| `owner`                   | 仓库所有者用户名            | 是   | -      |
| `repo`                    | 仓库名称                    | 是   | -      |
| `path`                    | 仓库内特定文件夹路径        | 否   | ""     |

---

## 🛠️ CLI 使用

### 快速开始命令

```bash
# 1. 初始化配置
host-image-backup init
# 或使用短别名
hib init

# 2. 测试图床连接
host-image-backup test oss
# 或使用短别名
hib test oss

# 3. 列出可用图床
host-image-backup list
# 或使用短别名
hib list

# 4. 从图床备份图片
host-image-backup backup oss --output ./my-backup
# 或使用短别名
hib backup oss --output ./my-backup

# 5. 从所有启用的图床备份
host-image-backup backup-all --output ./full-backup
# 或使用短别名
hib backup-all --output ./full-backup
```

### 命令参考

| 命令         | 描述                          | 别名 |
|--------------|-------------------------------|------|
| `init`       | 初始化默认配置文件            | -    |
| `backup`     | 从指定图床备份图片            | -    |
| `backup-all` | 从所有启用的图床备份          | -    |
| `list`       | 列出所有可用图床              | `list-providers` |
| `test`       | 测试图床连接                  | -    |
| `info`       | 显示图床详细信息              | -    |

### 详细命令用法

#### `init` - 初始化配置

创建包含所有图床的默认配置文件。

```bash
host-image-backup init
# 或使用短别名
hib init
```

**选项：**
- 如有需要会自动创建配置目录
- 覆盖现有配置前会提示确认
- 生成包含所有支持图床的模板

#### `backup` - 从图床备份

从指定图床备份图片到本地存储。

```bash
host-image-backup backup <provider> [OPTIONS]
# 或使用短别名
hib backup <provider> [OPTIONS]
```

**参数：**
- `<provider>`: 图床名称 (oss, cos, sms, imgur, github)

**选项：**
```bash
-o, --output PATH           输出目录（默认：./backup）
-l, --limit INTEGER         限制下载图片数量
-c, --config PATH          自定义配置文件路径
--skip-existing / --no-skip-existing  
                           跳过已存在的文件（默认：跳过）
-v, --verbose              显示详细日志
```

**示例：**
```bash
# 基本备份
host-image-backup backup oss
# 或使用短别名
hib backup oss

# 自定义输出目录和限制
host-image-backup backup oss --output ~/Pictures/backup --limit 100
# 或使用短别名
hib backup oss --output ~/Pictures/backup --limit 100

# 详细日志和自定义配置
host-image-backup backup imgur --config ./my-config.yaml --verbose
# 或使用短别名
hib backup imgur --config ./my-config.yaml --verbose

# 不跳过已存在文件
host-image-backup backup github --no-skip-existing
# 或使用短别名
hib backup github --no-skip-existing
```

#### `backup-all` - 备份所有图床

依次从所有启用的图床备份图片。

```bash
host-image-backup backup-all [OPTIONS]
# 或使用短别名
hib backup-all [OPTIONS]
```

**选项：**
```bash
-o, --output PATH           所有图床的输出目录
-l, --limit INTEGER         每个图床的限制（非总数）
--skip-existing / --no-skip-existing  
                           对所有图床跳过已存在文件
-v, --verbose              显示详细日志
```

**示例：**
```bash
host-image-backup backup-all --output ~/backup --limit 50 --verbose
# 或使用短别名
hib backup-all --output ~/backup --limit 50 --verbose
```

#### `list` - 列出图床

显示所有可用图床及其状态。

```bash
host-image-backup list
# 或使用短别名
hib list
```

**输出包括：**
- 图床名称
- 启用/禁用状态
- 配置验证状态

#### `test` - 测试连接

测试指定图床的连接和认证。

```bash
host-image-backup test <provider>
# 或使用短别名
hib test <provider>
```

**示例：**
```bash
host-image-backup test oss
host-image-backup test github
# 或使用短别名
hib test oss
hib test github
```

#### `info` - 图床信息

显示指定图床的详细信息。

```bash
host-image-backup info <provider>
# 或使用短别名
hib info <provider>
```

**信息包括：**
- 图床状态
- 配置验证
- 连接测试结果
- 总图片数量（如果可用）

### 全局选项

所有命令都支持这些全局选项：

```bash
-c, --config PATH          自定义配置文件路径
-v, --verbose              启用详细日志
--help                     显示帮助信息
```

---

## 💡 使用场景和示例

### 常见场景

- **📦 备份迁移**: 将云图床的图片镜像到本地存储
- **🔄 多图床聚合**: 将多个服务的图片整合到一处
- **⏰ 定时备份**: 通过 cron 作业或 CI/CD 管道自动化备份
- **🗂️ 归档管理**: 创建有组织的本地图片归档
- **🚀 灾难恢复**: 维护离线副本以确保业务连续性

### 实际应用示例

#### 个人照片备份

```bash
# 从多个服务备份所有个人照片
host-image-backup backup-all --output ~/PhotoBackup --verbose
# 或使用短别名
hib backup-all --output ~/PhotoBackup --verbose
```

#### 定时备份 (Cron)

```bash
# 添加到 crontab 进行每日备份
0 2 * * * /usr/local/bin/host-image-backup backup-all --output /backup/images --limit 100
# 或使用短别名
0 2 * * * /usr/local/bin/hib backup-all --output /backup/images --limit 100
```

#### 图床间迁移

```bash
# 步骤 1: 从旧图床备份
host-image-backup backup old-provider --output ./migration-temp
# 或使用短别名
hib backup old-provider --output ./migration-temp

# 步骤 2: 上传到新图床（手动或脚本方式）
# 您的上传脚本...
```

---

## 🔧 故障排除

### 常见问题和解决方案

#### ❌ 认证错误

**问题**: 无效的凭据或令牌

**解决方案**:

- 验证配置文件格式和凭据
- 检查令牌过期日期
- 确保 API 访问权限正确
- 测试单个图床: `host-image-backup test <provider>` 或 `hib test <provider>`

#### ❌ 网络连接问题

**问题**: 连接超时或失败

**解决方案**:

- 检查网络连接
- 在配置中增加超时时间
- 使用 `--verbose` 标志获取详细错误信息
- 验证图床服务状态

#### ❌ 权限和文件系统错误

**问题**: 无法写入输出目录

**解决方案**:

```bash
# 创建具有适当权限的输出目录
mkdir -p ~/backup && chmod 755 ~/backup

# 为安全设置配置文件权限
chmod 600 ~/.config/host-image-backup/config.yaml
```

#### ❌ 速率限制

**问题**: 图床 API 请求过多

**解决方案**:

- 在配置中减少 `max_concurrent_downloads`
- 在请求间添加延迟
- 使用 `--limit` 选项控制下载量
- 检查图床特定的速率限制

### 调试命令

```bash
# 测试特定图床连接
host-image-backup test oss --verbose
# 或使用短别名
hib test oss --verbose

# 显示图床详细信息
host-image-backup info github
# 或使用短别名
hib info github

# 以最大详细程度运行备份
host-image-backup backup imgur --verbose --limit 5
# 或使用短别名
hib backup imgur --verbose --limit 5
```

### 日志分析

```bash
# 检查最近的日志
tail -f logs/host_image_backup_*.log

# 搜索错误
grep -i error logs/host_image_backup_*.log

# 监控备份进度
grep -E "(Successfully|Failed)" logs/host_image_backup_*.log
```

---

## 🔒 安全和最佳实践

### 凭据安全

- **绝不提交凭据** 到版本控制
- **尽可能使用环境变量** 存储敏感数据
- **为配置文件设置限制性权限**:

```bash
chmod 600 ~/.config/host-image-backup/config.yaml
```

### 环境变量支持

```bash
# 通过环境变量设置凭据
export OSS_ACCESS_KEY_ID="your_key"
export OSS_ACCESS_KEY_SECRET="your_secret"
export GITHUB_TOKEN="ghp_your_token"

# 在配置文件中引用
providers:
  oss:
    access_key_id: "${OSS_ACCESS_KEY_ID}"
    access_key_secret: "${OSS_ACCESS_KEY_SECRET}"
```

### 网络安全

- 仅使用 HTTPS 端点（默认启用）
- 考虑为敏感数据使用 VPN 或私有网络
- 监控网络流量中的异常模式

---

## 🏗️ 开发和贡献

### 开发环境搭建

```bash
# 克隆仓库
git clone https://github.com/WayneXuCN/HostImageBackup.git
cd HostImageBackup

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 使用 uv 安装开发依赖（推荐）
uv lock  # 生成锁定文件
uv sync --all-extras # 安装所有额外依赖（dev）

# 设置 pre-commit 钩子
pre-commit install
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=src/host_image_backup

# 运行特定测试文件
pytest tests/test_config.py

# 运行带详细输出的测试
pytest -v
```

### 代码质量

```bash
# 格式化代码
ruff format src tests

# 类型检查
mypy src

# 代码检查
ruff check src tests

# 运行所有质量检查
make lint  # 或您首选的任务运行器
```

### 添加新图床

1. **在 `src/host_image_backup/providers/` 中创建图床类**
2. **从 `BaseProvider` 实现必需方法**
3. **在 `src/host_image_backup/config.py` 中添加配置类**
4. **在服务和 CLI 模块中更新图床注册表**
5. **添加全面测试**
6. **更新文档**

详细说明请参阅 [贡献指南](CONTRIBUTING.md)。

---

## 🗺️ 路线图

### 版本 0.2.0

- [ ] **增强错误处理**: 更好的错误消息和恢复
- [ ] **配置验证**: 实时配置验证
- [ ] **进度持久化**: 恢复中断的备份
- [ ] **性能优化**: 更快的并发下载

### 版本 0.3.0

- [ ] **Web UI**: 基于浏览器的配置和监控
- [ ] **数据库支持**: 用于备份元数据的 SQLite
- [ ] **高级过滤**: 日期范围、文件类型、大小限制
- [ ] **云集成**: 直接云到云传输

### 版本 1.0.0

- [ ] **生产就绪**: 完全稳定性和性能
- [ ] **企业功能**: 用户管理、审计日志
- [ ] **插件系统**: 第三方图床扩展
- [ ] **API 接口**: 用于集成的 REST API

### 其他图床

- [ ] **Cloudinary**: 图片管理平台
- [ ] **AWS S3**: 亚马逊云存储
- [ ] **Google Drive**: 谷歌云存储
- [ ] **Dropbox**: 文件托管服务
- [ ] **OneDrive**: 微软云存储

---

## 🤝 贡献

我们欢迎贡献！以下是您可以帮助的方式：

### 贡献方式

- 🐛 **报告错误** 和请求功能
- 📝 **改进文档** 和示例
- 🔧 **添加新图床** 或增强现有图床
- 🧪 **编写测试** 和提高代码覆盖率
- 🎨 **改善用户体验** 和 CLI 界面

### 贡献流程

1. **Fork** 仓库
2. **创建** 您的功能分支 (`git checkout -b feature/amazing-feature`)
3. **提交** 您的更改 (`git commit -m '✨ add amazing feature'`)
4. **推送** 到分支 (`git push origin feature/amazing-feature`)
5. **打开** Pull Request

请阅读我们的 [贡献指南](CONTRIBUTING.md) 获取详细准则。

---

## 📞 支持和社区

### 获取帮助

- 📖 **文档**: 查看此 README 和内联帮助
- 🐛 **错误报告**: [GitHub Issues](https://github.com/WayneXuCN/HostImageBackup/issues)
- 💬 **讨论**: [GitHub Discussions](https://github.com/WayneXuCN/HostImageBackup/discussions)
- 📧 **邮箱**: [wenjie.xu.cn@outlook.com](mailto:wenjie.xu.cn@outlook.com)

### 社区准则

- 保持尊重和包容
- 提供清晰的错误报告和重现步骤
- 分享您的使用案例和功能想法
- 在讨论和问题中帮助他人

---

## 📄 许可证

本项目采用 **MIT License** 许可 - 详情请参阅 [LICENSE](LICENSE) 文件。

### 第三方许可证

- 所有依赖项保持其各自的许可证
- 完整依赖项列表请参阅 [pyproject.toml](pyproject.toml)
| client_secret    | Imgur client secret          |
| token            | GitHub token                 |
| repo             | GitHub 仓库名称              |

#### 🔐 完整的配置示例

##### 阿里云 OSS 配置

```yaml
default_provider: oss
download_timeout: 30
retry_attempts: 3
create_subdirs: true

providers:
  oss:
    access_key_id: "LTAI5t9..."  # 在阿里云 RAM 控制台获取
    access_key_secret: "your_secret_key"
    bucket: "my-images-bucket"
    endpoint: "oss-cn-hangzhou.aliyuncs.com"
    prefix: "blog/images/"  # 可选，指定对象前缀
    enable_https: true      # 是否使用 HTTPS
```

##### 腾讯云 COS 配置

```yaml
default_provider: cos
download_timeout: 30
retry_attempts: 3
create_subdirs: true

providers:
  cos:
    secret_id: "AKIDxxx..."  # 在腾讯云 CAM 控制台获取
    secret_key: "your_secret_key" 
    bucket: "my-images-1234567890"  # 注意需要包含 APPID
    region: "ap-guangzhou"
    prefix: "website/uploads/"  # 可选，指定对象前缀
```

##### SM.MS 配置

```yaml
default_provider: smms
download_timeout: 30
retry_attempts: 3
create_subdirs: true

providers:
  smms:
    api_token: "xxxxxxxxxxxxxxxx"  # 在 SM.MS 用户中心获取
    api_base: "https://sm.ms/api/v2"  # 可选，自定义 API 地址
```

##### Imgur 配置

```yaml
default_provider: imgur
download_timeout: 30
retry_attempts: 3
create_subdirs: true

providers:
  imgur:
    client_id: "your_client_id"      # 在 Imgur API 控制台获取
    client_secret: "your_client_secret"
    access_token: "your_access_token"   # 可选，用于访问私有相册
    refresh_token: "your_refresh_token" # 可选，用于刷新访问令牌
```

##### GitHub 配置

```yaml
default_provider: github
download_timeout: 30
retry_attempts: 3
create_subdirs: true

providers:
  github:
    token: "ghp_xxxxxxxxxxxxxxxx"  # 在 GitHub Settings > Developer settings 创建
    repo: "username/repository"    # 格式：用户名/仓库名
    path: "images/"                # 可选，指定仓库内路径
    branch: "main"                 # 可选，指定分支，默认为 main
```

#### 🌍 使用环境变量

为了安全起见，建议将敏感信息存储在环境变量中：

```bash
# OSS 配置
export OSS_ACCESS_KEY_ID="your_access_key"
export OSS_ACCESS_KEY_SECRET="your_secret"

# COS 配置  
export COS_SECRET_ID="your_secret_id"
export COS_SECRET_KEY="your_secret_key"

# SM.MS 配置
export SMMS_API_TOKEN="your_token"

# Imgur 配置
export IMGUR_CLIENT_ID="your_client_id"
export IMGUR_CLIENT_SECRET="your_client_secret"

# GitHub 配置
export GITHUB_TOKEN="your_token"
```

然后在配置文件中引用：

```yaml
providers:
  oss:
    access_key_id: "${OSS_ACCESS_KEY_ID}"
    access_key_secret: "${OSS_ACCESS_KEY_SECRET}"
    bucket: "my-bucket"
    endpoint: "oss-cn-hangzhou.aliyuncs.com"
```

---

## 🛠️ 命令行用法

### 📋 命令总览

| 命令                  | 说明                                 | 示例                                           |
|-----------------------|--------------------------------------|------------------------------------------------|
| `init`                | 初始化配置文件                       | `host-image-backup init`                       |
| `backup`              | 从指定图床备份图片                   | `host-image-backup backup --provider oss`     |
| `list-providers`      | 列出支持的图床                       | `host-image-backup list-providers`            |
| `test`                | 测试图床连接                         | `host-image-backup test --provider oss`       |

### 🔧 命令详解

#### `init` - 初始化配置

初始化默认配置文件到 `~/.config/host-image-backup/config.yaml`。

```bash
host-image-backup init
```

配置文件会包含所有支持的图床配置模板，您只需填入相应的凭据信息即可。

#### `backup` - 备份图片

从指定图床下载所有图片到本地目录。

```bash
# 基本用法
host-image-backup backup --provider oss --output ./my-backup

# 使用自定义配置文件
host-image-backup backup --provider cos --output ./backup --config ./my-config.yaml

# 限制下载数量（用于测试）
host-image-backup backup --provider smms --output ./test --limit 10

# 跳过已存在的文件
host-image-backup backup --provider imgur --output ./backup --skip-existing

# 启用详细日志
host-image-backup backup --provider github --output ./backup --verbose
```

**常用参数说明：**

| 参数               | 必需 | 说明                               | 示例                     |
|--------------------|------|-----------------------------------|------------------------|
| `--provider`       | ✅   | 指定图床服务                       | `oss`, `cos`, `smms`   |
| `--output`         | ✅   | 备份输出目录                       | `./backup`, `/tmp/imgs` |
| `--config`         | ❌   | 自定义配置文件路径                 | `./config.yaml`        |
| `--limit`          | ❌   | 限制下载图片数量                   | `10`, `100`            |
| `--skip-existing`  | ❌   | 跳过已下载的文件                   | 布尔标志               |
| `--verbose`        | ❌   | 显示详细日志信息                   | 布尔标志               |

#### `list-providers` - 列出支持的图床

显示所有支持的图床服务及其状态。

```bash
host-image-backup list-providers
```

输出示例：

```text
支持的图床服务：
✅ oss      - 阿里云对象存储 OSS
✅ cos      - 腾讯云对象存储 COS  
✅ smms     - SM.MS 图床
✅ imgur    - Imgur 图床
✅ github   - GitHub 仓库
```

#### `test` - 测试连接

测试指定图床的连接和认证状态。

```bash
# 测试单个图床
host-image-backup test --provider oss

# 使用自定义配置文件
host-image-backup test --provider cos --config ./my-config.yaml

# 测试所有配置的图床
host-image-backup test --all
```

测试成功输出示例：

```text
✅ OSS 连接测试成功
   - 存储桶: my-images-bucket
   - 区域: oss-cn-hangzhou
   - 可访问图片数量: 1,234
```

### 💡 实用技巧

#### 批量备份多个图床

```bash
#!/bin/bash
# backup-all.sh - 备份所有图床的脚本

providers=("oss" "cos" "smms" "imgur" "github")

for provider in "${providers[@]}"; do
    echo "正在备份 $provider..."
    host-image-backup backup 
        --provider "$provider" 
        --output "./backup/$provider" 
        --skip-existing 
        --verbose
done
```

#### 定期自动备份（crontab）

```bash
# 每日凌晨 2 点自动备份
0 2 * * * /usr/local/bin/host-image-backup backup --provider oss --output /backup/images --skip-existing

# 每周日凌晨 3 点备份所有图床
0 3 * * 0 /home/user/scripts/backup-all.sh
```

#### 使用配置文件模板

```bash
# 生成配置模板
host-image-backup init

# 编辑配置文件
vim ~/.config/host-image-backup/config.yaml

# 验证配置
host-image-backup test --all
```

---

## 典型用例场景

- 将云端图床图片镜像备份到本地磁盘，便于迁移或归档。
- 聚合多图床图片到统一本地目录，便于统一管理。
- 结合定时任务或 CI/CD 自动化定期备份。

---

## 错误处理与常见问题

### 常见问题

- **凭据无效**：请检查配置文件是否有拼写错误。
- **网络错误**：请确保网络连接正常。
- **速率限制**：部分图床（如 SM.MS、Imgur）可能限制请求频率。
- **权限不足**：请确认输出目录有写入权限。

### 排查建议

- 使用 `--verbose` 参数获取详细日志。
- 检查输出目录下的日志文件。
- 针对图床相关问题，请参考其官方文档。

---

## 安全性说明

- **凭据保护**：请勿公开分享你的配置文件或凭据。
- 建议使用环境变量或密钥管理工具存储敏感信息。
- 配置文件建议设置权限为仅自己可读写（`chmod 600 ~/.config/host-image-backup/config.yaml`）。

---

## 扩展与自定义开发

- 新增图床支持：在 `src/host_image_backup/providers/` 下实现子类。
- 参考 [src/host_image_backup/providers/base.py](src/host_image_backup/providers/base.py) 了解 provider 接口。
- 欢迎贡献新 provider！

---

## 项目路线图

- [ ] 增加更多图床支持
- [ ] 提供 Web UI 配置与监控
- [ ] 支持定时自动备份
- [ ] 错误报告增强
- [ ] 多线程下载优化

---

## 开发与测试

### 环境搭建

```bash
git clone git@github.com:WayneXuCN/HostImageBackup.git
cd HostImageBackup
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -e ".[dev]"
pre-commit install
```

### 测试

```bash
pytest
```

### 代码格式化

```bash
black src tests
```

### 类型检查

```bash
mypy src
```

---

## 贡献流程

1. Fork 仓库
2. 创建分支 (`git checkout -b feature/foo`)
3. 提交更改 (`git commit -am 'Add foo feature'`)
4. 推送分支 (`git push origin feature/foo`)
5. 创建 Pull Request

详细流程请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 社区与支持

- GitHub Issues：[提交问题](https://github.com/WayneXuCN/HostImageBackup/issues)
- 讨论区：[GitHub Discussions](https://github.com/WayneXuCN/HostImageBackup/discussions)
- 邮箱：[wayne.xu.cn@gmail.com](mailto:wayne.xu.cn@gmail.com)

---

## 许可证

MIT License
