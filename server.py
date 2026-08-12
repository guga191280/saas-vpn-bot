from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
import os
import uvicorn

app = FastAPI()
DATA_DIR = "/opt/v1bot/data"

@app.get("/sub/{unique_id}", response_class=PlainTextResponse)
async def get_sub(unique_id: str, response: Response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    
    file_path = os.path.join(DATA_DIR, unique_id)
    if not os.path.exists(file_path):
        return "Subscription not found"
    
    with open(file_path, "r") as f:
        keys = f.read()
    
    subscription_header = (
        "#profile-title: Telegram: @HappVPN\n"
        "#profile-update-interval: 24\n"
        "#subscription-userinfo: upload=0; download=3161094701197; total=0; expire=0\n"
        "#support-url: https://t.me/HAPP_VPN_OFFICIAL\n"
        "#profile-web-page-url: https://t.me/HAPP_VPN_OFFICIAL\n\n"
    )
    
    return subscription_header + keys

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
