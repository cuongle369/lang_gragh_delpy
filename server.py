import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback

from langchain_core.messages import HumanMessage
import configuration
from task_maistro import graph, store

# ===================================
# FastAPI App Setup
# ===================================
app = FastAPI()

# Cho phép CORS (frontend gọi API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================================
# Root endpoint test
# ===================================
@app.get("/")
async def root():
    return {"message": "Task Maestro API is running!"}

# ===================================
# Chat endpoint
# ===================================
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "default_user")
    todo_category = data.get("todo_category", "default_category")
    role = data.get("role", "You are Task Maestro, a helpful assistant.")
    user_message = data.get("message", "")

    try:
        config = configuration.Configuration(
            user_id=user_id,
            todo_category=todo_category,
            task_maistro_role=role,
        ).to_runnable_config()

        # ✅ Fix: add store vào config
        config["store"] = store

        inputs = {"messages": [HumanMessage(content=user_message)]}
        result = graph.invoke(inputs, config)

        messages = result.get("messages", [])
        last_message = messages[-1].content if messages else ""

        return {
            "response": last_message,
            "messages": [getattr(m, "content", str(m)) for m in messages],
        }
    except Exception as e:
        print("CHAT ERROR:", e)
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

# ===================================
# Threads endpoint
# ===================================
@app.post("/threads")
async def threads(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "default_user")
    todo_category = data.get("todo_category", "default_category")
    role = data.get("role", "You are Task Maestro, a helpful assistant.")
    user_message = data.get("message", "")

    try:
        config = configuration.Configuration(
            user_id=user_id,
            todo_category=todo_category,
            task_maistro_role=role,
        ).to_runnable_config()

        # ✅ Fix: add store vào config
        config["store"] = store

        inputs = {"messages": [HumanMessage(content=user_message)]}
        result = graph.invoke(inputs, config)

        messages = result.get("messages", [])
        last_message = messages[-1].content if messages else ""

        return {
            "id": f"thread-{user_id}",
            "object": "thread.message",
            "response": last_message,
            "messages": [getattr(m, "content", str(m)) for m in messages],
        }
    except Exception as e:
        print("THREADS ERROR:", e)
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

# ===================================
# Debug Exception Handler
# ===================================
@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    print("ERROR TRACEBACK:\n", tb)
    return PlainTextResponse(str(exc), status_code=500)
