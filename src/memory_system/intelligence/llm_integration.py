#!/usr/bin/env python3
"""
LLM Integration - LLM 深度集成模块

核心功能:
1. 语义复杂度检测 - 识别需要 LLM 处理的复杂内容
2. 智能触发策略 - 根据内容复杂度决定是否调用 LLM
3. LLM 失败回退机制 - 失败时回退到规则结果
4. API Key 多源获取 - OpenClaw主配置 → 环境变量 → 配置文件
"""

import os
import re
import json
import subprocess
import glob
from typing import Optional, Dict, Any, Tuple, List


def load_openclaw_config() -> Dict[str, Any]:
    """从 OpenClaw 主配置文件加载 LLM 配置"""
    # 查找主配置文件
    possible_paths = [
        os.path.expanduser("~/.openclaw/openclaw.json"),
        os.path.expanduser("~/.config/openclaw/openclaw.json"),
    ]
    
    for config_path in possible_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 提取 LLM 配置
                llm_config = {}
                
                # 遍历所有 provider
                providers = config.get("models", {}).get("providers", {})
                for provider_name, provider_config in providers.items():
                    api_key = provider_config.get("apiKey")
                    base_url = provider_config.get("baseUrl")
                    models = provider_config.get("models", [])
                    
                    if api_key and base_url:
                        # 取第一个模型的 ID 作为标识
                        model_id = models[0]["id"] if models else f"{provider_name}/default"
                        llm_config[provider_name] = {
                            "api_key": api_key,
                            "base_url": base_url,
                            "model": model_id,
                            "provider": provider_name,
                        }
                
                return {
                    "enabled": True,
                    "providers": llm_config,
                    "default": "xunfei" if "xunfei" in llm_config else list(llm_config.keys())[0] if llm_config else None,
                }
            except Exception as e:
                print(f"Warning: 读取 OpenClaw 配置失败: {e}")
    
    return {"enabled": False, "providers": {}}


# 加载 OpenClaw 主配置
OPENCLAW_CONFIG = load_openclaw_config()


# LLM 配置
LLM_INTEGRATION_CONFIG = {
    # LLM 触发策略
    "trigger": {
        "high_confidence_threshold": 0.5,   # 高于此值，规则直接接受
        "low_confidence_threshold": 0.2,    # 低于此值，检查语义复杂度
        "uncertain_range": (0.2, 0.5),      # 不确定区间，交给 LLM
        "force_llm_on_complex": True,       # 复杂内容强制 LLM
    },
    # 语义复杂度检测
    "complexity": {
        "min_length_for_check": 10,         # 最小长度才检测
        "entity_count_threshold": 3,        # 实体数量阈值
        "relation_indicators": [            # 关系指示词
            "认为", "觉得", "怀疑", "可能", "也许", "大概", "据说", "听说",
            "似乎", "好像", "应该", "或许", "如果", "假如", "除非", "尽管",
            "虽然", "但是", "因为", "所以", "导致", "造成", "影响", "关系",
        ],
        "negation_indicators": [            # 否定/反转指示词
            "不是", "没有", "并非", "其实", "实际上", "事实上", "相反",
            "反而", "却", "倒是", "恰恰",
        ],
        "metaphor_indicators": [            # 隐喻/比喻指示词
            "像", "如同", "仿佛", "好比", "就像", "犹如", "简直", "堪比",
            "不亚于", "胜过",
        ],
        "temporal_complexity": [            # 时间复杂性
            "之前", "之后", "同时", "期间", "直到", "自从", "曾经", "一直",
            "最近", "将来", "过去",
        ],
    },
    # 回退策略
    "fallback": {
        "on_llm_failure": "rule",           # LLM 失败时：rule / discard
        "on_parse_failure": "rule",         # 解析失败时
        "retry_count": 1,                   # 重试次数
        "timeout_seconds": 30,              # 超时时间
    },
    # API 配置（从 OpenClaw 主配置读取）
    "api": {
        "env_key": "OPENAI_API_KEY",        # 环境变量名（备用）
        "default_model": "gpt-4o-mini",     # 默认模型（备用）
        "default_base_url": "https://api.openai.com/v1",  # 默认地址（备用）
        # OpenClaw 配置的 provider 映射
        "provider_map": {
            "xunfei": {
                "base_url": "https://maas-api.cn-huabei-1.xf-yun.com/v2",
                "models": ["xminimaxm25", "xopglm5", "xopkimik25", "xopqwen35397b", "xop3qwen1b7"],
            },
            "nvidia": {
                "base_url": "https://integrate.api.nvidia.com/v1",
                "models": ["nvidia/nemotron-3-nano-30b-a3b", "nvidia/qwen/qwen3.5-397b-a17b", "nvidia/minimaxai/minimax-m2.1", "nvidia/deepseek-ai/deepseek-v3.2", "nvidia/z-ai/glm4.7", "moonshotai/kimi-k2.5"],
            },
        },
    },
}


def get_omg_config() -> Dict[str, Any]:
    """读取 OMG 配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "memory/config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


# 缓存 OMG 配置
OMG_CONFIG = get_omg_config()


def get_llm_config(provider: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
    """
    获取 LLM 配置，优先级：
    1. OMG 配置文件 (memory/config.json) - 指定 provider 和 model
    2. OpenClaw 主配置 (~/.openclaw/openclaw.json) - 获取 API Key
    3. 环境变量 (备用)
    
    Args:
        provider: 指定 provider (xunfei/nvidia)，默认使用 OMG 配置
        model: 指定模型 ID，默认使用 OMG 配置
    
    Returns:
        包含 api_key, base_url, model 的字典
    """
    # 0. 读取 OMG 配置
    omg_llm = OMG_CONFIG.get("llm", {})
    omg_provider = omg_llm.get("provider", "xunfei")
    omg_model = omg_llm.get("model", "xminimaxm25")
    
    # 1. 优先使用参数，其次使用 OMG 配置
    target_provider = provider or omg_provider
    target_model = model or omg_model
    
    # 2. 从 OpenClaw 主配置获取 API Key 和 Base URL
    if OPENCLAW_CONFIG.get("enabled") and OPENCLAW_CONFIG.get("providers"):
        if target_provider in OPENCLAW_CONFIG["providers"]:
            pc = OPENCLAW_CONFIG["providers"][target_provider]
            
            # 获取该 provider 的模型列表
            models = pc.get("models", [])
            
            # 尝试找到指定模型
            found_model = None
            for m in models:
                if m.get("id") == target_model:
                    found_model = target_model
                    break
            
            # 如果没找到指定模型，使用 provider 默认模型
            if not found_model:
                found_model = models[0]["id"] if models else target_model
            
            # 获取 provider 映射配置
            api_config = LLM_INTEGRATION_CONFIG["api"]
            provider_map = api_config.get("provider_map", {})
            
            if target_provider in provider_map:
                pm = provider_map[target_provider]
                return {
                    "api_key": pc["api_key"],
                    "base_url": pm.get("base_url", pc.get("base_url", "")),
                    "model": found_model,
                    "provider": target_provider,
                }
            else:
                return {
                    "api_key": pc["api_key"],
                    "base_url": pc.get("base_url", ""),
                    "model": found_model,
                    "provider": target_provider,
                }
    
    # 3. 无配置
    return {"api_key": None, "base_url": None, "model": None, "provider": None}

# 统计信息
LLM_STATS = {
    "total_calls": 0,
    "successful_calls": 0,
    "failed_calls": 0,
    "fallback_count": 0,
    "total_tokens": 0,
}


def detect_semantic_complexity(content: str) -> Dict[str, Any]:
    """
    检测内容的语义复杂度
    
    返回:
    {
        "is_complex": bool,          # 是否复杂
        "complexity_score": float,   # 复杂度分数 (0-1)
        "reasons": list,             # 复杂原因
        "should_use_llm": bool,      # 是否应该使用 LLM
    }
    """
    config = LLM_INTEGRATION_CONFIG["complexity"]
    reasons = []
    score = 0.0
    
    # 1. 长度检查
    if len(content) < config["min_length_for_check"]:
        return {
            "is_complex": False,
            "complexity_score": 0.0,
            "reasons": ["内容太短"],
            "should_use_llm": False,
        }
    
    # 2. 关系指示词检测
    relation_count = sum(1 for indicator in config["relation_indicators"] 
                        if indicator in content)
    if relation_count >= config["entity_count_threshold"]:
        reasons.append(f"包含{relation_count}个关系指示词")
        score += 0.3
    
    # 3. 否定/反转检测
    negation_count = sum(1 for indicator in config["negation_indicators"] 
                        if indicator in content)
    if negation_count > 0:
        reasons.append(f"包含{negation_count}个否定/反转词")
        score += 0.2
    
    # 4. 隐喻/比喻检测
    metaphor_count = sum(1 for indicator in config["metaphor_indicators"] 
                        if indicator in content)
    if metaphor_count > 0:
        reasons.append(f"包含{metaphor_count}个隐喻/比喻词")
        score += 0.2
    
    # 5. 时间复杂性
    temporal_count = sum(1 for indicator in config["temporal_complexity"] 
                        if indicator in content)
    if temporal_count >= 2:
        reasons.append(f"包含{temporal_count}个时间复杂词")
        score += 0.2
    
    # 6. 句子结构复杂性
    sentences = re.split(r'[,.!?。！？]+', content)
    if len([s for s in sentences if s.strip()]) > 3:
        reasons.append("多句子结构")
        score += 0.1
    
    # 归一化分数
    score = min(1.0, score)
    is_complex = score > 0.3
    
    return {
        "is_complex": is_complex,
        "complexity_score": score,
        "reasons": reasons,
        "should_use_llm": is_complex,
    }


def should_use_llm_for_filtering(
    content: str,
    rule_confidence: float,
    force_complexity: bool = True,
) -> Tuple[bool, str]:
    """
    判断是否应该使用 LLM 进行过滤
    
    返回：(是否使用 LLM, 原因)
    """
    config = LLM_INTEGRATION_CONFIG["trigger"]
    
    # 高置信度 → 不需要 LLM
    if rule_confidence >= config["high_confidence_threshold"]:
        return False, "规则置信度高"
    
    # 检测语义复杂度
    complexity = detect_semantic_complexity(content)
    
    # 低置信度 + 复杂 → 需要 LLM
    if rule_confidence < config["low_confidence_threshold"]:
        if complexity["is_complex"] and force_complexity:
            return True, "低置信度 + 高复杂度"
        return False, "低置信度但简单"
    
    # 不确定区间 → 需要 LLM
    low, high = config["uncertain_range"]
    if low <= rule_confidence <= high:
        return True, "置信度不确定区间"
    
    return False, "规则置信度中等"


def call_llm_with_fallback(
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 1000,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    调用 LLM，失败时回退
    
    返回：(success, result, error)
    """
    LLM_STATS["total_calls"] += 1
    
    # 获取配置（优先从 OpenClaw 主配置读取）
    llm_cfg = get_llm_config(provider)
    api_key = api_key or llm_cfg.get("api_key")
    base_url = base_url or llm_cfg.get("base_url")
    model = model or llm_cfg.get("model")
    
    # 检查 API Key
    if not api_key:
        LLM_STATS["failed_calls"] += 1
        return False, None, "API Key 未配置"
    
    # 构建请求
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    request_data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }
    
    try:
        # 使用 curl 调用
        result = subprocess.run(
            [
                "curl", "-s", "--max-time", str(LLM_INTEGRATION_CONFIG["fallback"]["timeout_seconds"]),
                f"{base_url}/chat/completions",
                "-H", f"Authorization: Bearer {api_key}",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(request_data),
            ],
            capture_output=True,
            text=True,
            timeout=LLM_INTEGRATION_CONFIG["fallback"]["timeout_seconds"] + 10,
        )
        
        if result.returncode != 0:
            LLM_STATS["failed_calls"] += 1
            return False, None, f"curl 失败：{result.stderr}"
        
        # 解析响应
        resp = json.loads(result.stdout)
        
        if "error" in resp:
            LLM_STATS["failed_calls"] += 1
            return False, None, f"API 错误：{resp['error']}"
        
        # 提取内容
        message = resp["choices"][0]["message"]
        content = message.get("content", "").strip()
        
        # 兼容思考模型
        if not content:
            content = message.get("reasoning_content", "").strip()
        
        # 统计 token
        usage = resp.get("usage", {})
        LLM_STATS["total_tokens"] += usage.get("total_tokens", 0)
        LLM_STATS["successful_calls"] += 1
        
        return True, content, None
        
    except subprocess.TimeoutExpired:
        LLM_STATS["failed_calls"] += 1
        return False, None, "LLM 调用超时"
    except Exception as e:
        LLM_STATS["failed_calls"] += 1
        return False, None, f"LLM 调用失败：{str(e)}"


def get_llm_stats() -> Dict[str, Any]:
    """获取 LLM 调用统计"""
    return LLM_STATS.copy()


def reset_llm_stats():
    """重置统计"""
    global LLM_STATS
    LLM_STATS = {
        "total_calls": 0,
        "successful_calls": 0,
        "failed_calls": 0,
        "fallback_count": 0,
        "total_tokens": 0,
    }
