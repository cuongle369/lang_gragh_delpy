from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from langgraph.store.memory import InMemoryStore
from langchain_core.messages import HumanMessage

import configuration
from task_maistro import graph

# Khởi tạo FastAPI
app = FastAPI()

# Store memory dùng cho toàn bộ service
store = InMemoryStore()

# Root endpoint để health-check
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"message": "Task Maestro API is running!"}

# Endpoint chat đơn giản
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
        task_maistro_role=role,
    ).to_runnable_config()

    # Input messages
    inputs = {"messages": [HumanMessage(content=user_message)]}

    # Chạy graph
    result = graph.invoke(inputs, config, store=store)

    # Trả về response cuối cùng
    messages = result["messages"]
    last_message = messages[-1].content if messages else ""
    return JSONResponse({"response": last_message})


# Endpoint kiểu /threads (giống OpenAI assistant API)
@app.post("/threads")
async def threads(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "default_user")
    todo_category = data.get("todo_category", "default_category")
    role = data.get("role", "You are Task Maestro, a helpful assistant.")
    user_message = data.get("message", "")

    # Config cho graph
    config = configuration.Configuration(
        user_id=user_id,
        todo_category=todo_category,
        task_maistro_role=role,
    ).to_runnable_config()

    inputs = {"messages": [HumanMessage(content=user_message)]}
    result = graph.invoke(inputs, config, store=store)

    messages = result["messages"]
    last_message = messages[-1].content if messages else ""
    return {
        "id": f"thread-{user_id}",
        "object": "thread.message",
        "response": last_message,
        "messages": [m.content for m in messages],
    }
