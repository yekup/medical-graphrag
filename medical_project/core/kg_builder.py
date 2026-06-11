"""
医疗知识图谱构建器
解析OpenCMKG三元组，构建NetworkX图
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0,os.path.dirname(BASE_DIR))

import networkx as nx

#关系类型中文映射
RELATION_CN = {
    "disease_has_symptom": "症状",
    "disease_belong_department": "所属科室",
    "disease_acompany_disease": "伴随疾病",
    "disease_use_drug": "常用药物",
    "drug_has_ingredient": "药物成分",
    "drug_treat_disease": "治疗疾病",
    "symptom_belong_disease": "所属疾病",
}

def load_triples(filepath="data/raw/OpenCMKG/triples.txt"):
    """加载 OpenCMKG 三元组"""
    triples = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) >= 3:
                triples.append({
                    "source": parts[0].strip(),
                    "relation": parts[1].strip(),
                    "target": parts[2].strip(),
                })
    print(f"加载三元组: {len(triples)} 条")
    return triples


def load_entities(filepath="data/raw/OpenCMKG/entities_dict.txt"):
    """加载实体词典，按类型分组"""
    entities = {"disease": [], "drug": [], "symptom": [], "department": []}
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # 按类型解析
    import json
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            for k, v in data.items():
                if k in entities:
                    entities[k] = v if isinstance(v, list) else []
    except json.JSONDecodeError:
        pass
    for k, v in entities.items():
        print(f"  {k}: {len(v)} 个")
    return entities


def build_graph(triples):
    """从三元组构建 NetworkX 图"""
    G = nx.Graph()
    for t in triples:
        G.add_node(t["source"])
        G.add_node(t["target"])
        rel_cn = RELATION_CN.get(t["relation"], t["relation"])
        G.add_edge(t["source"], t["target"], relation=rel_cn)
    print(f"图构建完成: {G.number_of_nodes()} 节点, {G.number_of_edges()} 条边")
    return G

def save_graph(G, filepath="data/kg/medical_graph.json"):
    """保存图谱为 JSON"""
    data = {
        "nodes": [{"name": n} for n in G.nodes],
        "edges": [
            {"source": u, "target": v, **G.edges[u, v]}
            for u, v in G.edges
        ],
    }
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"图谱已保存: {filepath}")
    return data
