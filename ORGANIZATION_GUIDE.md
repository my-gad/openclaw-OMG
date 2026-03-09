# 组织架构与记忆共享指南

## 📋 概述

OpenClaw-OMG v1.6.0+ 提供完整的组织架构管理和记忆共享系统：

- **机构/团队创建**：支持创建正式机构（organization）和临时团队（team）
- **嵌套结构**：组织可以嵌套，形成树形结构
- **记忆共享规则**：
  - 同一组织内共享记忆
  - 上层可查看下层非隔离记忆
  - 下层不可查看上层记忆
- **权限控制**：精细化的访问权限管理

---

## 🏗️ 组织架构模型

### 树形结构示例

```
汪氏家族总部 (根组织，隔离)
├── 四川中古韵科技 (子组织，隔离)
│   ├── 运营团队 (团队，非隔离) ← 上层可查看
│   ├── 技术团队 (团队，非隔离) ← 上层可查看
│   └── 设计团队 (团队，非隔离) ← 上层可查看
├── 家族办公室 (子组织，隔离)
│   └── 财务组 (团队，非隔离)
└── 家族理事会 (子组织，隔离)
```

### 组织类型

| 类型 | 说明 | 用途 | 示例 |
|------|------|------|------|
| `organization` | 正式机构 | 公司、部门等长期组织 | 汪氏家族总部、中古韵科技 |
| `team` | 临时团队 | 项目组、专项组等 | 运营团队、技术团队 |

### 记忆共享规则

```
┌─────────────────────────────────────┐
│ 根组织 (隔离)                        │
│  - 记忆：根组织私有                   │
│  - 上层：无                          │
│  - 下层：可查看子组织的非隔离记忆      │
├─────────────────────────────────────┤
│ 子组织 (隔离)                        │
│  - 记忆：子组织私有                   │
│  - 上层：根组织可查看（如果允许）      │
│  - 下层：可查看子团队的非隔离记忆      │
├─────────────────────────────────────┤
│ 子团队 (非隔离)                      │
│  - 记忆：对上层可见                   │
│  - 上层：可查看                      │
│  - 下层：无                          │
└─────────────────────────────────────┘
```

**核心规则：**
1. 上层可查看下层的非隔离记忆
2. 下层不可查看上层记忆
3. 同层组织间默认隔离

---

## 🚀 快速开始

### 1. 创建根组织

```bash
# 创建家族总部
python3 -m memory_system.cli org-create "汪氏家族总部" --type org
```

### 2. 创建子组织

```bash
# 获取父组织 ID
python3 -m memory_system.cli org-list

# 创建子公司
python3 -m memory_system.cli org-create "中古韵科技" \
    --type org \
    --parent <根组织 ID>
```

### 3. 创建团队

```bash
# 在子公司下创建团队
python3 -m memory_system.cli org-create "运营团队" \
    --type team \
    --parent <子公司 ID> \
    --shared  # 非隔离，允许上级查看
```

### 4. 加入组织

```bash
# Agent 加入组织
python3 -m memory_system.cli org-join <组织 ID> <Agent ID> --role admin
```

---

## 💻 Python API 使用

### 创建组织

```python
from pathlib import Path
from memory_system.multiagent import OrganizationManager, OrgType

# 初始化
manager = OrganizationManager(Path('./memory'))

# 创建根组织
root_id = manager.create_organization(
    name="汪氏家族总部",
    org_type=OrgType.ORGANIZATION,
    description="家族最高管理机构",
    is_isolated=True  # 默认隔离
)

# 创建子组织（嵌套）
child_id = manager.create_organization(
    name="中古韵科技",
    org_type=OrgType.ORGANIZATION,
    description="子公司",
    parent_id=root_id,  # 指定父组织
    is_isolated=True
)

# 创建团队（非隔离，允许上级查看）
team_id = manager.create_organization(
    name="运营团队",
    org_type=OrgType.TEAM,
    description="运营团队",
    parent_id=child_id,
    is_isolated=False  # 非隔离
)
```

### 组织嵌套

```python
# 获取祖先组织（从下到上）
ancestors = manager.get_ancestor_orgs(team_id)
print(f"祖先组织：{[a.name for a in ancestors]}")
# 输出：祖先组织：['中古韵科技', '汪氏家族总部']

# 获取后代组织（从上到下）
descendants = manager.get_descendant_orgs(root_id)
print(f"后代组织：{[d.name for d in descendants]}")
# 输出：后代组织：['中古韵科技', '运营团队']
```

### 权限控制

```python
# 检查记忆访问权限
can_view = manager.can_view_memory(
    viewer_org_id=root_id,  # 查看方
    target_org_id=team_id   # 被查看方
)
print(f"根组织可查看团队记忆：{can_view}")  # True

# 下层不能查看上层
can_view_up = manager.can_view_memory(
    viewer_org_id=team_id,
    target_org_id=root_id
)
print(f"团队可查看根组织记忆：{can_view_up}")  # False
```

### 成员管理

```python
# 添加成员
manager.add_member(org_id, agent_id, role="admin")

# 移除成员
manager.remove_member(org_id, agent_id)

# 获取 Agent 所属组织
orgs = manager.get_member_orgs(agent_id)
```

---

## 📊 CLI 命令

### org-create

创建组织/团队

```bash
python3 -m memory_system.cli org-create "名称" \
    --type <org|team> \
    --description "描述" \
    --parent <父组织 ID> \
    --shared  # 可选，非隔离
```

参数：
- `name`: 组织名称
- `--type`: 组织类型（org=机构，team=团队）
- `--description`: 描述
- `--parent`: 父组织 ID（嵌套）
- `--shared`: 非隔离（允许上层查看）

### org-list

列出所有组织

```bash
python3 -m memory_system.cli org-list
```

### org-join

加入组织

```bash
python3 -m memory_system.cli org-join <组织 ID> <Agent ID> \
    --role <admin|member>
```

### org-status

查看组织系统状态

```bash
python3 -m memory_system.cli org-status
```

---

## 🎯 使用场景

### 场景 1: 家族企业管理

```python
# 创建家族总部
root_id = manager.create_organization("汪氏家族总部", OrgType.ORGANIZATION)

# 创建旗下公司
company_id = manager.create_organization(
    "中古韵科技",
    OrgType.ORGANIZATION,
    parent_id=root_id
)

# 创建部门
dept_id = manager.create_organization(
    "运营部",
    OrgType.TEAM,
    parent_id=company_id,
    is_isolated=False  # 允许上级查看
)

# 注册 Agent 并加入
agent_id = agent_manager.register_agent("运营 - 汪维维")
manager.add_member(dept_id, agent_id, role="admin")
```

### 场景 2: 项目组临时团队

```python
# 在项目组下创建临时团队
project_team_id = manager.create_organization(
    "项目 Alpha 组",
    OrgType.TEAM,
    parent_id=dept_id,
    is_isolated=False  # 允许上级追踪进度
)

# 项目结束后删除
manager.delete_organization(project_team_id)
```

### 场景 3: 记忆共享控制

```python
# 非隔离团队 - 上级可查看
team_public = manager.create_organization(
    "公开团队",
    OrgType.TEAM,
    parent_id=dept_id,
    is_isolated=False  # 允许上级查看
)

# 隔离团队 - 上级不可查看
team_private = manager.create_organization(
    "机密团队",
    OrgType.TEAM,
    parent_id=dept_id,
    is_isolated=True  # 隔离
)
```

---

## 🔐 权限说明

### 记忆访问权限矩阵

| 查看方 \ 被查看方 | 根组织 | 子组织（隔离） | 子团队（非隔离） |
|-----------------|--------|----------------|------------------|
| 根组织          | ✅ 自身 | ✅ 允许时       | ✅ 是            |
| 子组织（隔离）   | ❌ 否   | ✅ 自身         | ✅ 是            |
| 子团队（非隔离） | ❌ 否   | ❌ 否           | ✅ 自身          |
| 其他组织        | ❌ 否   | ❌ 否           | ❌ 否            |

### 默认权限

- **根组织**：可查看下层的非隔离记忆
- **子组织**：可查看下层的非隔离记忆，不可查看上层
- **子团队（非隔离）**：记忆对上层可见，不可查看上层
- **子团队（隔离）**：完全隔离，不对任何组织可见

---

## 📁 目录结构

```
memory/
├── organizations/           # 组织数据
│   ├── organizations.json   # 组织列表
│   └── memberships.json     # 成员资格
├── shared_spaces/           # 共享记忆空间
│   ├── {space_id}/         # 空间目录
│   │   ├── config.json     # 空间配置
│   │   └── memory/         # 共享记忆
├── agents/                  # Agent 目录
│   ├── {agent_id}/         # Agent 独立空间
│   │   └── memory/
```

---

## ✅ 最佳实践

### 1. 组织设计原则

- **根组织隔离**：顶层组织默认隔离，保护核心数据
- **下层非隔离**：执行层团队非隔离，便于上级追踪
- **最小权限**：默认隔离，按需开放

### 2. 命名规范

```
机构：{机构名} + 类型（可选）
  - 汪氏家族总部
  - 中古韵科技

团队：{功能名} + 团队/组
  - 运营团队
  - 技术组
```

### 3. 权限管理

```python
# 创建时设置隔离
org = manager.create_organization(
    name="敏感团队",
    is_isolated=True  # 完全隔离
)

# 或修改现有组织
org = manager.get_organization(org_id)
org.allow_parent_view = False  # 禁止上级查看
```

---

## 🧪 测试

```python
from memory_system.multiagent import OrganizationManager, OrgType

manager = OrganizationManager(Path('./memory'))

# 创建测试组织
root = manager.create_organization("根", OrgType.ORGANIZATION)
child = manager.create_organization("子", OrgType.ORGANIZATION, parent_id=root)
team = manager.create_organization("团队", OrgType.TEAM, parent_id=child, is_isolated=False)

# 验证嵌套
assert len(manager.get_descendant_orgs(root)) == 2
assert len(manager.get_ancestor_orgs(team)) == 2

# 验证权限
assert manager.can_view_memory(root, team)  # 上层看下层
assert not manager.can_view_memory(team, root)  # 下层不看上层

print("✅ 所有测试通过")
```

---

## 🔗 相关文档

- [MULTIAGENT.md](MULTIAGENT.md) - 多 Agent 文档
- [INSTALL.md](INSTALL.md) - 安装指南
- [README.md](README.md) - 项目说明

---

**版本**: v1.6.0+  
**最后更新**: 2026-03-09  
**维护者**: 运维 - 汪维维 (main)
