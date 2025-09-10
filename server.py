from fastapi import FastAPI
from pydantic import BaseModel
from task_maistro import graph  # graph bạn đã build ở task_maistro.py

app = FastAPI()

# Health check
@app.get("/")
def root():
    return {"status": "ok", "message": "LangGraph is running"}

# Input schema cho endpoint /invoke
class GraphInput(BaseModel):
    messages: list[dict]

@app.post("/invoke")
def invoke_graph(data: GraphInput):
    # Chuyển input thành dict để graph xử lý
    result = graph.invoke({"messages": data.messages})
    return result
