"""测试医疗 GraphRAG 检索"""
import sys, os
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.dirname(os.getcwd()))
from core.medical_retriever import MedicalRetriever

mr = MedicalRetriever()

for q in ["头痛恶心怎么回事", "高血压用什么药", "糖尿病饮食注意"]:
    print(f"\n问题: {q}")
    result = mr.search(q)
    print(f"实体: {result['entities']}")
    print(f"关系: {len(result['relations'])} 条")
    for r in result["relations"][:5]:
        print(f"  {r['source']} → {r['relation']} → {r['target']}")
    if result["context"]:
        answer = mr.ask(q)
        print(f"\n回答: {answer[:200]}...")
