#!/bin/bash
#
# OpenClaw-OMG 安装脚本
# 使用方法：./install.sh
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${PROJECT_DIR}/src"
MEMORY_DIR="${PROJECT_DIR}/memory"

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}OpenClaw-OMG 安装脚本${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""

# 检查 Python 版本
echo -e "${YELLOW}[1/5] 检查 Python 版本...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "  Python 版本：${PYTHON_VERSION}"

# 检查 Python 版本是否 >= 3.8
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}❌ 错误：需要 Python 3.8 或更高版本${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓ Python 版本满足要求${NC}"
echo ""

# 创建必要目录
echo -e "${YELLOW}[2/5] 创建目录结构...${NC}"
mkdir -p "${MEMORY_DIR}"/{layer1,layer2/active,layer2/archive,layer2/entities,layer3,agents,agent_messages,shared_spaces}
echo -e "  ${GREEN}✓ 目录创建完成${NC}"
echo ""

# 设置环境变量
echo -e "${YELLOW}[3/5] 设置环境变量...${NC}"
export PYTHONPATH="${SRC_DIR}:${PYTHONPATH}"
echo "  PYTHONPATH=${PYTHONPATH}"
echo -e "  ${GREEN}✓ 环境变量设置完成${NC}"
echo ""

# 初始化记忆系统
echo -e "${YELLOW}[4/5] 初始化记忆系统...${NC}"
cd "${PROJECT_DIR}"
python3 -m memory_system.cli init
echo -e "  ${GREEN}✓ 记忆系统初始化完成${NC}"
echo ""

# 验证安装
echo -e "${YELLOW}[5/5] 验证安装...${NC}"
python3 -c "
from memory_system.core import MemoryManager, MemoryType
from memory_system.multiagent import AgentManager
print('  ✓ 核心模块导入成功')
"

python3 -m memory_system.cli status
echo -e "  ${GREEN}✓ 验证通过${NC}"
echo ""

# 完成
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}安装完成！${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo "使用指南:"
echo "  1. 添加记忆:"
echo "     python3 -m memory_system.cli add \"内容\" --type fact"
echo ""
echo "  2. 搜索记忆:"
echo "     python3 -m memory_system.cli search \"关键词\""
echo ""
echo "  3. 注册 Agent:"
echo "     python3 -m memory_system.cli agent-register \"名称\" --role main"
echo ""
echo "  4. 查看更多帮助:"
echo "     python3 -m memory_system.cli --help"
echo ""
echo "文档:"
echo "  - README.md      - 项目说明"
echo "  - INSTALL.md     - 详细安装指南"
echo "  - MULTIAGENT.md  - 多 Agent 文档"
echo ""
