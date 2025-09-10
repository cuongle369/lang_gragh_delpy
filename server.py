from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from langgraph.store.memory import InMemoryStore
from langchain_core.messages import HumanMessage

import configuration
from task_maistro import graph

# Khởi tạo FastAPI
app = FastAPI()

# Tạo store in-memory
store = InMemoryStore()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "default_user")
    todo_category = data.get("todo_category", "default_category")
    role = data.get("role", "You are Task Maestro, a helpful assistant.")

    user_message = data.get("message", "")

    # Config cho graph
    config = configuration.Configuration(
        user_id=user_id,
        todo_category=todo_category,
        task_maistro_role=role
    ).to_runnable_config()

    # Thêm tin nhắn user
    inputs = {"messages": [HumanMessage(content=user_message)]}

    # Chạy graph với memory store
    result = graph.invoke(inputs, config, store=store)

    # Lấy phản hồi cuối cùng
    messages = result["messages"]
    last_message = messages[-1].content if messages else ""

    return JSONResponse({"response": last_message})
