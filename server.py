
import os
print("CHARGly SERVER DOSYASI AÇILDI")
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

KEDY_API_KEY = os.getenv("KEDY_API_KEY")
KEDY_URL = "https://api.kedy.dev/v1/chat/completions"


class SuggestionRequest(BaseModel):
    message: str = "Chargly için üç pil tasarrufu önerisi ver. Türkçe cevapla."


@app.get("/")
def home():
    return {"status": "Chargly sunucusu çalışıyor"}


@app.post("/suggest")
async def suggest(request: SuggestionRequest):
    if not KEDY_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="KEDY_API_KEY ayarlanmamış."
        )

    headers = {
        "Authorization": f"Bearer {KEDY_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "novaq",
        "messages": [
            {
                "role": "user",
                "content": request.message,
            }
        ],
    }

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            response = await client.post(
                KEDY_URL,
                headers=headers,
                json=body,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=exc.response.text or "Kedy API hata döndürdü."
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=502,
                detail="Kedy API bağlantısı kurulamadı."
            )
