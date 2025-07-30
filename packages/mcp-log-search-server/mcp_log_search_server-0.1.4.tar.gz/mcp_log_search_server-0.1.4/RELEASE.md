# 发布流程说明

## 快速发布

使用一条命令完成完整的发布流程：

```bash
make release VERSION=v1.0.0
```

这个命令会：
1. 运行代码检查和测试
2. 检查工作目录是否干净（所有更改已提交）
3. 创建带注释的 Git 标签
4. 推送标签到远程仓库
5. 触发 GitHub Action 自动构建和发布

## 分步操作

### 1. 准备发布

```bash
# 确保所有更改已提交
git add .
git commit -m "Prepare for release v1.0.0"

# 运行测试和检查
make all
```

### 2. 创建和推送标签

```bash
# 只创建和推送标签
make tag-push VERSION=v1.0.0
```

### 3. 查看发布状态

创建标签后，可以在 GitHub 上查看：
- Actions 页面：查看构建和发布状态
- Releases 页面：查看发布的包

## 版本号格式

使用语义化版本号（Semantic Versioning）：
- `v1.0.0` - 主要版本
- `v1.1.0` - 次要版本（新功能）
- `v1.0.1` - 修复版本（Bug修复）

## 安全检查

`make release` 命令包含以下安全检查：

1. **代码质量检查**：确保代码通过基本检查
2. **工作目录检查**：确保所有更改已提交
3. **标签重复检查**：防止覆盖现有标签

## 错误处理

如果发布过程中出现错误：

### 标签已存在
```bash
Tag v1.0.0 already exists!
```
解决：使用不同的版本号

### 工作目录不干净
```bash
Error: Working directory is not clean. Please commit all changes first.
```
解决：提交所有更改后再发布

### 代码检查失败
先修复代码问题，然后重新运行发布命令

## 示例发布流程

```bash
# 1. 开发完成，提交代码
git add .
git commit -m "Add new feature: simplified log search interface"

# 2. 运行完整发布流程
make release VERSION=v1.1.0

# 3. 查看GitHub Actions页面确认发布成功
```

发布成功后，新版本会自动发布到 PyPI，用户可以通过以下命令安装：

```bash
pip install mcp-log-search-server==1.1.0
```
