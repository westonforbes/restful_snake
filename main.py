import psycopg2
import os
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict
import uvicorn
from wf_console import Console as console
DEBUG = True

# Define connection parameters using environment variables from the venv.
connection_params = {
    'dbname': 'postgres',
    'user': os.getenv('USERNAME'),
    'password': os.getenv('PASSWORD'),
    'host': 'localhost',
    'port': 5432
}

console.clear()

def insert_data(connection_parameters: dict, table: str, temperature_f: float, humidity_percentage: float, heat_index: float) -> None:

    # Check that the user and password is set.
    if DEBUG: console.fancy_print(f"<INFO>checking environment variables...</INFO>")
    if not connection_parameters['user'] or not connection_parameters['password']:
        if DEBUG: console.fancy_print(f"<BAD>USERNAME and PASSWORD environment variables must be set.</BAD>")
        raise ValueError("USERNAME and PASSWORD environment variables must be set.")
    if DEBUG: console.fancy_print(f"<GOOD>environment variables checked.</GOOD>")
    
    # Try protect...
    try:

        # Round parameters to two decimal places.
        if DEBUG: console.fancy_print(f"<INFO>rounding values...</INFO>")
        temperature_f = round(temperature_f, 2)
        humidity_percentage = round(humidity_percentage, 2)
        heat_index = round(heat_index, 2)
        if DEBUG: console.fancy_print(f"rounded values: <DATA>{temperature_f}</DATA>, <DATA>{humidity_percentage}</DATA>, <DATA>{heat_index}</DATA>")

        # Establish connection.
        if DEBUG: console.fancy_print(f"<INFO>establishing connection...</INFO>")
        connection = psycopg2.connect(**connection_parameters)
        if DEBUG: console.fancy_print(f"<GOOD>connection established.</GOOD>")

        # Create a cursor object.
        if DEBUG: console.fancy_print(f"<INFO>creating cursor...</INFO>")
        cursor = connection.cursor()
        if DEBUG: console.fancy_print(f"<GOOD>cursor created.</GOOD>")

        # Insert query.
        if DEBUG: console.fancy_print(f"<INFO>preparing insert query...</INFO>")
        insert_query = f"""
            INSERT INTO {table} (temperature_f, humidity_percentage, heat_index_f)
            VALUES (%s, %s, %s)
        """
        if DEBUG: console.fancy_print(f"<GOOD>insert query prepared.</GOOD>")

        # Execute insert command.
        if DEBUG: console.fancy_print(f"<INFO>executing insert command...</INFO>")
        cursor.execute(insert_query, (temperature_f, humidity_percentage, heat_index))
        if DEBUG: console.fancy_print(f"<GOOD>insert command executed.</GOOD>")

        # Commit the transaction.
        if DEBUG: console.fancy_print(f"<INFO>committing transaction...</INFO>")
        connection.commit()
        if DEBUG: console.fancy_print(f"<GOOD>transaction committed.</GOOD>")

    except Exception as e:
        if DEBUG: console.fancy_print(f"<BAD>error inserting data: {e}</BAD>")

    finally:
        if cursor:
            if DEBUG: console.fancy_print(f"<INFO>closing cursor...</INFO>")
            cursor.close()
            if DEBUG: console.fancy_print(f"<GOOD>cursor closed.</GOOD>")
        if connection:
            if DEBUG: console.fancy_print(f"<INFO>closing connection...</INFO>")
            connection.close()
            if DEBUG: console.fancy_print(f"<GOOD>connection closed.</GOOD>")



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

    insert_data(connection_params,payload.name, payload.temperature_f, payload.humidity_percentage, payload.heat_index_f)

    return {"status": "success", "received": payload.model_dump()}

# Sample successful POST request:
# curl -X POST http://sql-server:8000/data -H "Content-Type: application/json" -d '{"name": "environmental_sensor_data", "temperature_f": 72.5, "humidity_percentage": 45.0,"heat_index_f": 75.0}'

# Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
