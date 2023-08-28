from fastapi import FastAPI, Request, Header, HTTPException
import pprint

app = FastAPI()

from fastapi import FastAPI
from structures import SyncItems

@app.post("/docs/")
async def upload_bytes_or_json(
    request: Request,
    content_type: str = Header(None)
):
    match content_type:
        case "application/json":
            json_payload = await request.json()
            try:
                sync_items = SyncItems(**json_payload)
                for item in sync_items.items:
                    pprint.pprint(item)
                    
                return {"message": "Hello World"}
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")
            
        case "application/octet-stream":
            raw_data = await request.body()
            return {"message": "Received Bytes", "length": len(raw_data)}

        case _:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported Content-Type header: {content_type}",
            )
