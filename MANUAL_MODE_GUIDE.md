# 手动模式指南

## 📋 核心原则

**组织/团队必须手动创建，助手必须手动加入/退出**

- ❌ 不自动创建组织
- ❌ 不自动加入组织  
- ❌ 不自动退出组织
- ✅ 所有操作都需要显式执行

---

## 🏗️ 组织架构

### 树形结构

```
汪氏家族总部 (根组织，隔离)
├── 四川中古韵科技 (子组织，隔离)
│   ├── 运营团队 (团队，非隔离)
│   └── 技术团队 (团队，非隔离)
└── 家族办公室 (子组织，隔离)
```

### 组织类型

| 类型 | 说明 | 用途 |
|------|------|------|
| `org` | 正式机构 | 公司、部门等长期组织 |
| `team` | 临时团队 | 项目组、专项组等 |

---

## 🚀 快速开始

### 1. 创建组织

```bash
# 创建根组织（家族总部）
python3 -m memory_system.org_cli create "汪氏家族总部" --type org

# 创建子公司
python3 -m memory_system.org_cli create "中古韵科技" \
    --type org \
    --parent "<根组织 ID>"

# 创建团队
python3 -m memory_system.org_cli create "运营团队" \
    --type team \
    --parent "<子公司 ID>"
```

### 2. 查看组织

```bash
# 列出所有组织
python3 -m memory_system.org_cli list

# 查看组织状态
python3 -m memory_system.org_cli status
```

### 3. 加入组织

```bash
# Agent 加入组织
python3 -m memory_system.org_cli join "<组织名称或 ID>" "<Agent ID>"

# 示例
python3 -m memory_system.org_cli join "运维团队" "b78ce51e-d32d-42a7-9baf-03efffe3faad"
```

### 4. 退出组织

```bash
# Agent 退出组织
python3 -m memory_system.org_cli leave "<组织名称或 ID>" "<Agent ID>"
```

---

## 💻 Python API

### 创建组织

```python
from pathlib import Path
from memory_system.multiagent import OrganizationManager, OrgType

manager = OrganizationManager(Path('./memory'))

# 创建根组织
root_id = manager.create_organization(
    name="汪氏家族总部",
    org_type=OrgType.ORGANIZATION,
    is_isolated=True  # 默认隔离
)

# 创建子组织
child_id = manager.create_organization(
    name="中古韵科技",
    org_type=OrgType.ORGANIZATION,
    parent_id=root_id,
    is_isolated=True
)

# 创建团队
team_id = manager.create_organization(
    name="运营团队",
    org_type=OrgType.TEAM,
    parent_id=child_id,
    is_isolated=False  # 非隔离，允许上级查看
)
```

### 加入/退出组织

```python
# 加入组织
manager.add_member(team_id, agent_id, role="member")

# 退出组织
manager.remove_member(team_id, agent_id)

# 查看 Agent 所属组织
orgs = manager.get_member_orgs(agent_id)
```

---

## 📊 CLI 命令

### org_cli create - 创建组织

```bash
python3 -m memory_system.org_cli create "名称" \
    --type <org|team> \
    --description "描述" \
    --parent "<父组织 ID>" \
    --isolated  # 记忆隔离
```

### org_cli list - 列出组织

```bash
python3 -m memory_system.org_cli list
```

### org_cli join - 加入组织

```bash
python3 -m memory_system.org_cli join "<组织名称或 ID>" "<Agent ID>" \
    --role <member|admin>
```

### org_cli leave - 退出组织

```bash
python3 -m memory_system.org_cli leave "<组织名称或 ID>" "<Agent ID>"
```

### org_cli status - 查看状态

```bash
python3 -m memory_system.org_cli status
```

---

## 🎯 使用场景

### 场景 1: 家族企业

```bash
# 1. 创建家族总部
python3 -m memory_system.org_cli create "汪氏家族总部" --type org

# 2. 创建子公司
python3 -m memory_system.org_cli create "中古韵科技" \
    --type org \
    --parent "<总部 ID>"

# 3. 创建部门团队
python3 -m memory_system.org_cli create "运营团队" \
    --type team \
    --parent "<子公司 ID>"

# 4. Agent 加入
python3 -m memory_system.org_cli join "运营团队" "<Agent ID>"
```

### 场景 2: 项目组

```bash
# 1. 在项目下创建临时团队
python3 -m memory_system.org_cli create "项目 Alpha 组" \
    --type team \
    --parent "<项目组 ID>"

# 2. 成员加入
python3 -m memory_system.org_cli join "项目 Alpha 组" "<Agent 1 ID>"
python3 -m memory_system.org_cli join "项目 Alpha 组" "<Agent 2 ID>"

# 3. 项目结束后退出
python3 -m memory_system.org_cli leave "项目 Alpha 组" "<Agent 1 ID>"
```

---

## ✅ 最佳实践

### 1. 组织命名

```
机构：{机构名} + 类型
  - 汪氏家族总部
  - 中古韵科技

团队：{功能名} + 团队/组
  - 运营团队
  - 技术组
```

### 2. 权限控制

- **根组织**：默认隔离，保护核心数据
- **子组织**：默认隔离，按需开放
- **团队**：可非隔离，便于上级追踪

### 3. 成员管理

- 定期清理不活跃成员
- 明确角色和职责
- 记录加入/退出时间

---

## 🔗 相关文档

- [ORGANIZATION_GUIDE.md](ORGANIZATION_GUIDE.md) - 组织架构
- [MULTI_ASSISTANT_GUIDE.md](MULTI_ASSISTANT_GUIDE.md) - 多助手配置
- [MULTIAGENT.md](MULTIAGENT.md) - 多 Agent 支持

---

**版本**: v1.6.0+  
**最后更新**: 2026-03-09  
**维护者**: 运维 - 汪维维 (main)
