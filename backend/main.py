import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router

app = FastAPI(
    title="OFS Photomatrix",
    description="Organizational Framework System",
    version="0.1.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    # Явно указываем разрешенные источники
    allow_origins=[
        "http://localhost:5173", # Адрес фронтенда Vite
        "http://localhost:8000"  # Адрес самого API (на всякий случай, для Swagger)
        # Добавить сюда URL для продакшена, когда он появится
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API роутеров
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "OFS Photomatrix API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 