from fastapi import FastAPI
from pydantic import BaseModel
from task_maistro import builder   # 👈 import builder thay vì graph
from langgraph.store.memory import InMemoryStore

app = FastAPI()

# Tạo store in-memory
store = InMemoryStore()
graph = builder.compile(store=store)

# Health check
@app.get("/")
def root():
    return {"status": "ok", "message": "LangGraph is running"}

# Input schema
class GraphInput(BaseModel):
    messages: list[dict]

@app.post("/invoke")
def invoke_graph(data: GraphInput):
    try:
        result = graph.invoke(
            {"messages": data.messages},
            config={"configurable": {"user_id": "default-user"}}
        )
        return result
    except Exception as e:
        return {"error": str(e)}
