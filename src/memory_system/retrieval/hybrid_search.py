#!/usr/bin/env python3
"""
Hybrid Search - 混合检索引擎

结合关键词检索和语义检索。
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SearchResult:
    """搜索结果"""
    content: str
    score: float
    source: str
    metadata: Optional[Dict[str, Any]] = None


class HybridSearchEngine:
    """
    混合检索引擎
    
    支持：
    - 关键词检索 (BM25)
    - 语义检索 (向量)
    - 混合排序 (RRF)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.keyword_weight = self.config.get('keyword_weight', 0.3)
        self.vector_weight = self.config.get('vector_weight', 0.7)
        self.min_score = self.config.get('min_score', 0.2)
    
    def search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        use_vector: bool = False,
    ) -> List[SearchResult]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            documents: 文档列表，每个文档包含 content 字段
            use_vector: 是否使用向量检索 (需要额外依赖)
        
        Returns:
            搜索结果列表，按相关性排序
        """
        if not documents:
            return []
        
        # 关键词检索
        keyword_results = self._keyword_search(query, documents)
        
        if use_vector:
            # 向量检索 (TODO: 实现)
            vector_results = self._vector_search(query, documents)
            # 混合排序
            results = self._merge_results(keyword_results, vector_results)
        else:
            results = keyword_results
        
        # 过滤低分结果
        results = [r for r in results if r.score >= self.min_score]
        
        return results
    
    def _keyword_search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
    ) -> List[SearchResult]:
        """关键词检索 (TF-IDF 简化版)"""
        results = []
        query_terms = self._tokenize(query)
        
        for doc in documents:
            content = doc.get('content', '')
            doc_terms = self._tokenize(content)
            
            # 计算简单重叠度
            matches = len(set(query_terms) & set(doc_terms))
            score = matches / (len(query_terms) + len(doc_terms) + 1)
            
            # 考虑词频
            term_freq = sum(1 for term in query_terms if term in content)
            score *= (1 + term_freq / len(content)) if content else 0
            
            if score > 0:
                results.append(SearchResult(
                    content=content,
                    score=score,
                    source=doc.get('id', 'unknown'),
                    metadata=doc,
                ))
        
        # 按分数排序
        results.sort(key=lambda r: r.score, reverse=True)
        return results
    
    def _vector_search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
    ) -> List[SearchResult]:
        """向量检索 (TODO: 实现)"""
        # 需要向量嵌入支持
        return []
    
    def _merge_results(
        self,
        keyword_results: List[SearchResult],
        vector_results: List[SearchResult],
    ) -> List[SearchResult]:
        """
        合并两种检索结果 (RRF - Reciprocal Rank Fusion)
        """
        merged = {}
        
        # 关键词结果
        for i, result in enumerate(keyword_results):
            merged[result.source] = {
                'content': result.content,
                'keyword_score': 1.0 / (i + 1),
                'vector_score': 0,
            }
        
        # 向量结果
        for i, result in enumerate(vector_results):
            if result.source in merged:
                merged[result.source]['vector_score'] = 1.0 / (i + 1)
            else:
                merged[result.source] = {
                    'content': result.content,
                    'keyword_score': 0,
                    'vector_score': 1.0 / (i + 1),
                }
        
        # 计算加权分数
        results = []
        for source, data in merged.items():
            score = (
                self.keyword_weight * data['keyword_score'] +
                self.vector_weight * data['vector_score']
            )
            
            if score > 0:
                results.append(SearchResult(
                    content=data['content'],
                    score=score,
                    source=source,
                ))
        
        results.sort(key=lambda r: r.score, reverse=True)
        return results
    
    def _tokenize(self, text: str) -> List[str]:
        """分词 (简化版)"""
        # 中文按字符，英文按单词
        text = text.lower()
        
        # 提取英文单词
        words = re.findall(r'\b[a-z]+\b', text)
        
        # 提取中文字符
        chinese = [c for c in text if '\u4e00' <= c <= '\u9fff']
        
        return words + chinese
