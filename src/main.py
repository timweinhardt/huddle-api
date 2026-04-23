from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

@app.get("/test")
async def root():
    return {"message": "Hello, World!"}