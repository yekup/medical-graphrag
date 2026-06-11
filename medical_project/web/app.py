"""医疗 GraphRAG API"""
import os, sys
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.medical_retriever import MedicalRetriever

retriever = MedicalRetriever()

template_dir = os.path.join(BASE_DIR, "web", "templates")
env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

app = FastAPI(title="医疗 GraphRAG 问答系统")

@app.get("/")
async def index():
    t = env.get_template("index.html")
    return HTMLResponse(t.render())

@app.get("/api/ask")
async def ask(query: str = ""):
    if not query:
        return {"answer": "请输入问题"}
    answer = retriever.ask(query)
    result = retriever.search(query)
    return {"answer": answer, "entities": result["entities"], "relations_count": len(result["relations"])}
