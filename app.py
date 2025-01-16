import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from g4f.client import Client
import json
from typing import List, Dict
from starlette.requests import Request

# Если вы на Windows, оставьте строку ниже; если нет, можно удалить:
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Инициализация FastAPI
app = FastAPI()

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Инициализация шаблонов
templates = Jinja2Templates(directory="templates")

# Все доступные модели
MODELS = [
    "gpt-4", "gpt-4o", "gpt-4o-mini", "claude-3.5-sonnet"
]

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Класс для управления соединениями и историей чата
class ConnectionManager:
    def __init__(self):
        # Храним для каждого WebSocket список сообщений: [{role: "...", content: "..."}]
        self.active_connections: Dict[WebSocket, List[Dict]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = []

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]

    def get_history(self, websocket: WebSocket) -> List[Dict]:
        return self.active_connections.get(websocket, [])

    def add_message(self, websocket: WebSocket, role: str, content: str):
        if websocket in self.active_connections:
            # Защита от дублирующихся подряд сообщений
            if (not self.active_connections[websocket] or
               self.active_connections[websocket][-1]['content'] != content):
                self.active_connections[websocket].append({"role": role, "content": content})

manager = ConnectionManager()

# WebSocket-обработчик
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    client = Client()

    try:
        while True:
            try:
                data = await websocket.receive_text()
                request = json.loads(data)
                model = request.get("model")
                prompt = request.get("prompt")

                if model not in MODELS:
                    await websocket.send_text("Ошибка: неподдерживаемая модель.")
                    continue

                # Добавляем сообщение пользователя
                manager.add_message(websocket, "user", prompt)

                chat_history = manager.get_history(websocket)
                # Берём последние 10 сообщений, чтобы контекст не разрастался бесконечно
                messages = [
                    {"role": "system", "content": "Ты — русскоязычный ассистент. Всегда отвечай на русском языке."}
                ] + chat_history[-10:]

                # Сообщаем фронтенду о том, что сейчас пойдёт поток (индикатор печатания)
                await websocket.send_text("TYPING")
                
                full_response = ""
                try:
                    # Получаем стрим-ответ от модели
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        stream=True
                    )

                    # Читаем чанки и отправляем их пользователю
                    for chunk in response:
                        # Убедитесь, что g4f действительно возвращает поле в формате chunk.choices[0].delta.content
                        # Иначе придётся адаптировать под реальную структуру chunk
                        if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            await websocket.send_text(content)
                    
                    # После завершения стриминга весь ответ готов
                    if full_response:
                        manager.add_message(websocket, "assistant", full_response)

                except Exception as e:
                    print(f"Ошибка при генерации: {str(e)}")
                    await websocket.send_text(f"Ошибка: {str(e)}")

                # Сообщаем фронтенду, что печать завершена
                await websocket.send_text("DONE_TYPING")

            except json.JSONDecodeError:
                await websocket.send_text("Ошибка: неверный формат данных")
            except WebSocketDisconnect:
                manager.disconnect(websocket)
                break
            except Exception as e:
                print(f"Ошибка: {str(e)}")
                await websocket.send_text(f"Ошибка: {str(e)}")
                continue

    finally:
        manager.disconnect(websocket)
        await websocket.close()

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        loop="asyncio",
        timeout_keep_alive=0,  # Отключаем таймаут
    )
    server = uvicorn.Server(config)
    server.run()
