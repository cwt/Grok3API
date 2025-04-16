# this code is not very well debugged yet, but it seems to work


import os
import json
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from grok3api.client import GrokClient
from grok3api.grok3api_logger import logger
from grok3api.types.GrokResponse import GrokResponse
import uvicorn

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "grok-3"
    messages: List[Message]
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Dict[str, Any]

app = FastAPI(title="Grok3API OpenAI-Compatible Server")

env_cookies = os.getenv("GROK_COOKIES", None)
if env_cookies:
    try:
        env_cookies = json.loads(env_cookies)
    except json.JSONDecodeError:
        logger.error("Invalid GROK_COOKIES format in environment variable. Expected JSON string.")
        env_cookies = None

try:
    grok_client = GrokClient(
        cookies=None,
        proxy=os.getenv("GROK_PROXY", None),
        timeout=120
    )
except Exception as e:
    logger.error(f"Failed to initialize GrokClient: {e}")
    raise

@app.post("/v1/chat/completions")
async def chat_completions(
        request: ChatCompletionRequest,
        authorization: Optional[str] = Header(None)
):
    """Эндпоинт для обработки чатовых запросов в формате OpenAI."""
    try:
        if request.stream:
            raise HTTPException(status_code=400, detail="Streaming is not supported.")

        cookies = None
        if authorization and authorization.startswith("Bearer "):
            api_key = authorization.replace("Bearer ", "").strip()
            if api_key and api_key != "dummy" and api_key != "auto":
                try:
                    cookies = json.loads(api_key)
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="Invalid API key format. Expected JSON string.")
        if cookies is None:
            cookies = env_cookies

        grok_client.cookies = cookies

        history_messages = []
        last_user_message = ""

        for msg in request.messages:
            if msg.role == "user" and not last_user_message:
                last_user_message = msg.content
            else:
                sender = "USER" if msg.role == "user" else "ASSISTANT" if msg.role == "assistant" else "SYSTEM"
                history_messages.append({"sender": sender, "message": msg.content})

        if history_messages:
            history_json = json.dumps(history_messages)
            message_payload = f"{history_json}\n{last_user_message}" if last_user_message else history_json
        else:
            message_payload = last_user_message

        if not message_payload.strip():
            raise HTTPException(status_code=400, detail="No user message provided.")

        response: GrokResponse = await grok_client.async_ask(
            message=message_payload,
            history_id=None,
            modelName=request.model,
            timeout=120,
            customInstructions="",
            disableSearch=False,
            enableImageGeneration=False,
            enableImageStreaming=False,
            enableSideBySide=False
        )

        if response.error or not response.modelResponse.message:
            raise HTTPException(
                status_code=500,
                detail=response.error or "No response from Grok API."
            )

        import time
        current_time = int(time.time())
        response_id = response.responseId or f"chatcmpl-{current_time}"

        chat_response = ChatCompletionResponse(
            id=response_id,
            created=current_time,
            model=request.model,
            choices=[
                Choice(
                    index=0,
                    message=Message(
                        role="assistant",
                        content=response.modelResponse.message
                    ),
                    finish_reason="stop"
                )
            ],
            usage={
                "prompt_tokens": len(message_payload.split()),
                "completion_tokens": len(response.modelResponse.message.split()),
                "total_tokens": len(message_payload.split()) + len(response.modelResponse.message.split())
            }
        )

        return chat_response

    except Exception as ex:
        logger.error(f"Error in chat_completions: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)