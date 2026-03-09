# OpenClaw-OMG 代码合并优化方案

## 📋 版本清单

### 已合并到 v1.5.0 的代码
- ✅ v1.1.x - 基础三层架构
- ✅ v1.2.x - QMD 集成 + SQLite
- ✅ v1.3.0 - Memory Operator + 冲突消解
- ✅ v1.4.0 - 时序引擎

### 待合并的 Legacy 代码
- ⬜ `v1_1_5_entity_system.py` - 实体系统增强
- ⬜ `v1_1_7_llm_integration.py` - LLM 深度集成
- ⬜ `sqlite_backend_v1_2_5.py` - SQLite 后端优化版
- ⬜ `v1_1_commands.py` - v1.1 CLI 命令
- ⬜ `v1_1_config.py` - v1.1 配置
- ⬜ `v1_1_helpers.py` - v1.1 辅助函数

## 🎯 合并策略

### Phase 1: 实体系统 (v1.1.5)
**目标**: 增强实体识别和管理能力

**合并位置**:
```
src/memory_system/intelligence/entity_system.py
```

**关键功能**:
- 正则实体提取
- 实体隔离存储
- 学习实体清理
- 实体关系图谱

### Phase 2: LLM 深度集成 (v1.1.7)
**目标**: 智能筛选和实体提取

**合并位置**:
```
src/memory_system/intelligence/llm_integration.py
```

**关键功能**:
- 语义复杂度检测
- 智能触发策略
- LLM 失败回退
- 多源 API Key 获取

### Phase 3: SQLite 后端优化 (v1.2.5)
**目标**: 替换当前 sqlite_backend.py

**合并位置**:
```
src/memory_system/storage/sqlite_backend.py (替换)
```

**改进点**:
- WAL 模式优化
- 并发安全增强
- 索引优化
- 迁移工具

### Phase 4: 工具函数整合
**目标**: 清理和整合辅助函数

**合并位置**:
```
src/memory_system/utils/helpers.py (整合 v1_1_helpers.py)
src/memory_system/utils/config.py (整合 v1_1_config.py)
```

## 📦 优化措施

### 1. 代码去重
- 移除重复的函数定义
- 统一配置管理
- 合并相似的 CLI 命令

### 2. 性能优化
- 异步索引更新
- 缓存管理优化
- 批量操作支持

### 3. 可维护性提升
- 统一类型注解
- 完善文档字符串
- 标准化错误处理

### 4. 测试覆盖
- 单元测试（每个模块）
- 集成测试（模块间交互）
- 性能基准测试

## 🚀 执行计划

### Step 1: 分析 Legacy 代码 (30 分钟)
```bash
# 统计各文件行数和关键函数
wc -l legacy/*.py
grep -n "^def\|^class" legacy/*.py
```

### Step 2: 逐个合并 (2-3 小时)
1. 实体系统
2. LLM 集成
3. SQLite 后端
4. 工具函数

### Step 3: 测试验证 (1 小时)
```bash
# 运行所有测试
python3 -m pytest tests/ -v

# 性能基准
python3 src/benchmark.py
```

### Step 4: 文档更新 (30 分钟)
- 更新 API 文档
- 编写迁移指南
- 添加使用示例

## ✅ 验收标准

- [ ] 所有 legacy 功能已合并
- [ ] 通过所有现有测试
- [ ] 性能无退化
- [ ] 代码覆盖率 >80%
- [ ] 文档完整
- [ ] 向后兼容

---

**创建时间**: 2026-03-08  
**版本**: v1.5.0 → v1.6.0 (计划)
