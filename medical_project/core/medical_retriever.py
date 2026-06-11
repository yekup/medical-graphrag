"""
医疗 GraphRAG 检索器
实体链接 → 图谱检索 → 上下文拼接 → LLM 生成
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(BASE_DIR))

from core.entity_linker import EntityLinker
from agent_project.core.llm import call_llm

KG_PATH = os.path.join(BASE_DIR, "data/kg/medical_graph.json")


class MedicalRetriever:
    """医疗 GraphRAG 检索器"""

    def __init__(self, kg_path=KG_PATH):
        self.linker = EntityLinker(kg_path)
        # 加载图谱边（三元组）
        with open(kg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.edges = data["edges"]
        print(f"GraphRAG 检索器加载完成: {len(self.edges)} 条关系")

    def search(self, query, max_relations=15):
        """
        检索流程：实体链接 → 查找相关三元组 → 返回上下文

        参数:
            query: 用户问题
            max_relations: 最多返回的关系数

        返回:
            dict: {entities, relations, context}
        """
        # 1. 实体链接
        entities = self.linker.link(query, top_k=5)
        entity_names = [e["entity"] for e in entities]

        if not entity_names:
            return {"entities": [], "relations": [], "context": ""}

        # 2. 从图谱中查找相关三元组
        matched_relations = []
        seen = set()
        for e in entity_names:
            for edge in self.edges:
                if e in edge["source"] or e in edge["target"]:
                    key = (edge["source"], edge["target"])
                    if key not in seen:
                        seen.add(key)
                        matched_relations.append(edge)
                        if len(matched_relations) >= max_relations:
                            break
            if len(matched_relations) >= max_relations:
                break

        # 3. 格式化上下文
        context_parts = []
        for r in matched_relations:
            context_parts.append(f"{r['source']} → {r['relation']} → {r['target']}")

        context = "\n".join(context_parts)

        return {
            "entities": entity_names,
            "relations": matched_relations,
            "context": context,
        }

    def ask(self, query):
        """完整问答：检索 → 生成"""
        result = self.search(query)
        if not result["context"]:
            return "未找到相关的医学信息。"

        prompt = f"""你是一个医学知识助手。请基于以下医学知识图谱信息回答用户问题。

【知识图谱信息】
{result["context"]}

【问题】
{query}

请基于以上信息回答。如果信息不足，如实说明。
"""

        response = call_llm([{"role": "user", "content": prompt}])
        return response
