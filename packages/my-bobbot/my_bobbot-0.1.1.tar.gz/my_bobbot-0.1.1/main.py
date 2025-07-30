from fastapi import FastAPI
import logging

app = FastAPI()

@app.get("/")
async def root():
    logging.info("Hello World")
    return {"message": "Hello World"}