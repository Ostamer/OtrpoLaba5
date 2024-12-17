from fastapi import FastAPI
from routes import router
from database import close_driver

app = FastAPI(title="Neo4j FastAPI Service")

# Подключение маршрутов
app.include_router(router)

@app.on_event("shutdown")
def shutdown_event():
    close_driver()

@app.get("/")
def root():
    return {"message": "Neo4j FastAPI Service is running"}
