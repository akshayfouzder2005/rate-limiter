from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.limiters.fixed_window import fixed_window
from app.limiters.sliding_window import sliding_window_log
from app.limiters.token_bucket import token_bucket
from app.config import settings

app = FastAPI(title="Rate Limiter API", version="1.0.0")
app.mount("/static", StaticFiles(directory="frontend"), name="static")

def get_client_id(request: Request) -> str:
    return request.headers.get("X-API-Key") or request.client.host

def rate_limit_response(result: dict, algorithm: str):
    if not result["allowed"]:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "algorithm": algorithm,
                "retry_after": result.get("reset_in", 60)
            },
            headers={"Retry-After": str(result.get("reset_in", 60))}
        )
    return None

# --- Demo endpoints, one per algorithm ---

@app.get("/api/fixed-window")
async def fixed_window_route(request: Request):
    client_id = get_client_id(request)
    result = fixed_window(client_id, settings.DEFAULT_MAX_REQUESTS, settings.DEFAULT_WINDOW_SECONDS)
    err = rate_limit_response(result, "fixed_window")
    if err: return err
    return {"message": "Request allowed", "algorithm": "fixed_window", **result}

@app.get("/api/sliding-window")
async def sliding_window_route(request: Request):
    client_id = get_client_id(request)
    result = sliding_window_log(client_id, settings.DEFAULT_MAX_REQUESTS, settings.DEFAULT_WINDOW_SECONDS)
    err = rate_limit_response(result, "sliding_window_log")
    if err: return err
    return {"message": "Request allowed", "algorithm": "sliding_window_log", **result}

@app.get("/api/token-bucket")
async def token_bucket_route(request: Request):
    client_id = get_client_id(request)
    result = token_bucket(client_id, capacity=10, refill_rate=0.2)
    err = rate_limit_response(result, "token_bucket")
    if err: return err
    return {"message": "Request allowed", "algorithm": "token_bucket", **result}

@app.get("/")
async def serve_ui():
    return FileResponse("frontend/index.html")