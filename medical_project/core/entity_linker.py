"""
医疗实体链接
将用户问题中的症状、疾病、药物名映射到知识图谱实体
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KG_PATH = os.path.join(BASE_DIR, "data/kg/medical_graph.json")


class EntityLinker:
    """实体链接器"""

    def __init__(self, kg_path=KG_PATH):
        # 加载图谱节点列表
        with open(kg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.all_entities = [n["name"] for n in data["nodes"] if len(n["name"]) >= 2]
        self.all_entities.sort(key=len, reverse=True)
        print(f"实体链接器加载完成: {len(self.all_entities)} 个实体")

    def link(self, text, top_k=5):
        """
        从文本中提取医疗实体

        参数:
            text: 用户问题
            top_k: 最多返回 top_k 个实体

        返回:
            list of dict: [{"entity": "头痛", "start": 0, "end": 2}]
        """
        found = []
        # 遍历排序后的实体列表，正向最大匹配
        for entity in self.all_entities:
            if len(found) >= top_k:
                break
            if entity in text:
                # 检查是否已被包含在已有匹配中
                start = text.index(entity)
                end = start + len(entity)
                # 简单去重：如果这个位置已经被覆盖，跳过
                is_covered = False
                for f in found:
                    if not (end <= f["start"] or start >= f["end"]):
                        is_covered = True
                        break
                if not is_covered:
                    found.append({"entity": entity, "start": start, "end": end})

        # 按文本出现顺序排序
        found.sort(key=lambda x: x["start"])
        return found


if __name__ == "__main__":
    linker = EntityLinker()

    test_queries = [
        "头痛恶心肌肉痛怎么回事",
        "高血压患者可以吃阿莫西林吗",
        "糖尿病饮食注意事项",
        "怀孕37周拉肚子怎么办",
    ]

    for q in test_queries:
        print(f"\n问题: {q}")
        results = linker.link(q)
        for r in results:
            print(f"  → {r['entity']}")
