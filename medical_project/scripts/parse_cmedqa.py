"""
解析 cMedQA2 问答数据集
解压 ZIP → 提取问题和答案 → 保存为结构化 JSON
"""
import csv
import os
import zipfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data/raw/cMedQA2")
OUTPUT_DIR = os.path.join(BASE_DIR, "data/processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_questions():
    """解析问题文件"""
    questions = {}
    with zipfile.ZipFile(os.path.join(RAW_DIR, "question.zip")) as z:
        with z.open("question.csv") as f:
            reader = csv.reader(f.read().decode("utf-8").splitlines())
            for row in reader:
                if len(row) >= 2:
                    qid = row[0].strip()
                    text = row[1].strip()
                    if qid and text:
                        questions[qid] = text
    print(f"问题数: {len(questions)}")
    return questions


def parse_answers():
    """解析答案文件"""
    answers = {}
    with zipfile.ZipFile(os.path.join(RAW_DIR, "answer.zip")) as z:
        with z.open("answer.csv") as f:
            reader = csv.reader(f.read().decode("utf-8").splitlines())
            for row in reader:
                if len(row) >= 3:
                    aid = row[0].strip()
                    qid = row[1].strip()
                    text = row[2].strip()
                    if aid and text:
                        if qid not in answers:
                            answers[qid] = []
                        answers[qid].append({"answer_id": aid, "text": text})
    print(f"有答案的问题数: {len(answers)}")
    return answers


def build_qa_pairs(questions, answers, max_pairs=1000):
    """构建 QA 对（取前 max_pairs 条做测试集）"""
    qa_pairs = []
    for qid, q_text in list(questions.items())[:max_pairs]:
        if qid in answers:
            best_answer = answers[qid][0]["text"]
            qa_pairs.append({
                "question": q_text,
                "answer": best_answer,
                "qid": qid,
            })
    print(f"QA 对: {len(qa_pairs)} 条")
    return qa_pairs


if __name__ == "__main__":
    import json
    questions = parse_questions()
    answers = parse_answers()
    qa_pairs = build_qa_pairs(questions, answers, max_pairs=500)

    output_path = os.path.join(OUTPUT_DIR, "cmedqa_500.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
    print(f"已保存: {output_path}")

    # 打印几条示例
    for qa in qa_pairs[:3]:
        print(f"\nQ: {qa['question'][:80]}")
        print(f"A: {qa['answer'][:120]}")
