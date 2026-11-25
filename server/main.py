"""AIAgent-server (LLM・AIエージェントサーバー)

StyleBertVits2-server と同じ書き方のインターフェース:
  POST /chat {"msg": "..."} → {"text": "...", "expression": "normal" | "smile"}
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import LLMOutput, build_agent
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _agent
    if not settings.GOOGLE_API_KEY:
        logger.warning("GOOGLE_API_KEY is empty. Set it in .env (see .env.example).")
    _agent = build_agent()
    logger.info("Agent ready: model=%s", settings.MODEL)
    yield


app = FastAPI(title="AIAgent Server", lifespan=lifespan)


class ChatRequest(BaseModel):
    msg: str


@app.post("/chat", response_model=LLMOutput)
async def chat(req: ChatRequest) -> LLMOutput:
    if not req.msg or not req.msg.strip():
        raise HTTPException(status_code=400, detail="msg must not be empty")

    received_at = time.perf_counter()
    logger.info("chat request received: msg=%r", req.msg[:40])

    try:
        # Gemini APIの応答待ち(I/O待ち)なので、ainvokeでawaitすればイベントループは塞がらない。
        # (StyleBertVits2-serverのようなCPU推論ではないため、run_in_threadpoolは不要)
        result = await _agent.ainvoke({"messages": [{"role": "user", "content": req.msg}]})
    except Exception as e:
        logger.error("LLM error after %.3fs: %s", time.perf_counter() - received_at, e)
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    output = result.get("structured_response")
    if output is None:
        logger.error("structured_response is missing: %r", result)
        raise HTTPException(status_code=502, detail="LLM returned no structured response")

    logger.info(
        "chat OK: text=%r expression=%s total=%.3fs",
        output.text[:40], output.expression, time.perf_counter() - received_at,
    )
    return output


@app.get("/health")
def health():
    return {
        "status": "ok" if _agent is not None else "not_ready",
        "model": settings.MODEL,
        "api_key_configured": bool(settings.GOOGLE_API_KEY),
    }
