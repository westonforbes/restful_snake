from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict
import uvicorn

app = FastAPI()

# Define the expected post schema.
class DataPayload(BaseModel):

    name: str
    temperature_f: float
    humidity_percentage: float
    heat_index_f: float


@app.post("/data")
async def receive_data(payload: DataPayload):
    # Access individual keys: payload.key1, payload.key2, etc.
    print("received data:", payload.model_dump())

    # Process the data here
    # e.g., store in DB, log to file, trigger an action, etc.

    return {"status": "success", "received": payload.model_dump()}

# Sample successful POST request:
# curl -X POST http://sql-server:8000/data -H "Content-Type: application/json" -d '{"name": "sensor 1", "temperature_f": 72.5, "humidity_percentage": 45.0,"heat_index_f": 75.0}'

# Run with: uvicorn rest:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    uvicorn.run("rest:app", host="0.0.0.0", port=8000, reload=True)
    
