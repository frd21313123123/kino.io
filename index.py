import asyncio
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from g4f.client import Client
import anyio

# Инициализация FastAPI
app = FastAPI()

# Все доступные модели
MODELS = [
    "gpt-4", "gpt-4o", "gpt-4o-mini", "claude-3.5-sonnet"
]

# HTML-интерфейс
html = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Model Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #212121;
            color: #f4f4f9;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }
        .header {
            width: 100%;
            background-color: #303030;
            padding: 10px 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #ececec;
            margin: 0;
            font-size: 1.5em;
        }
        .model-dropdown {
            position: relative;
        }
        .model-dropdown button {
            background-color: #303030;
            color: #ececec;
            border: none;
            padding: 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        .model-dropdown button:hover {
            background-color: #404040;
        }
        .dropdown-content {
            display: none;
            position: absolute;
            background-color: #404040;
            border-radius: 5px;
            box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.2);
            z-index: 1;
            min-width: 200px;
        }
        .dropdown-content a {
            color: #f4f4f9;
            padding: 10px;
            text-decoration: none;
            display: block;
        }
        .dropdown-content a:hover {
            background-color: #505050;
        }
        .model-dropdown:hover .dropdown-content {
            display: block;
        }
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            margin-bottom: 20px;
            display: flex;
            align-items: flex-start;
        }
        .message.user {
            justify-content: flex-end;
        }
        .message .content {
            max-width: 70%;
            padding: 10px;
            border-radius: 10px;
            font-size: 1em;
            line-height: 1.5;
        }
        .message.user .content {
            background-color: #404040;
            color: #f4f4f9;
        }
        .message.bot .content {
            background-color: #303030;
            color: #ececec;
        }
        .input-container {
            position: fixed;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            background-color: #303030;
            padding: 10px;
            border-radius: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            width: calc(100% - 40px);
            max-width: 800px;
            display: flex;
            align-items: center;
        }
        .input-container textarea {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 10px;
            background-color: #212121;
            color: #f4f4f9;
            resize: none;
            height: 50px;
            margin-right: 10px;
        }
        .input-container button {
            background-color: #ececec;
            color: #212121;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
        }
        .input-container button:hover {
            background-color: #d6d6d6;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>ChatGPT 4o</h1>
        <div class="model-dropdown">
            <button>Выберите модель</button>
            <div class="dropdown-content">
                <a href="#" onclick="setModel('gpt-4')">GPT-4</a>
                <a href="#" onclick="setModel('gpt-4o')">GPT-4o</a>
                <a href="#" onclick="setModel('gpt-4o-mini')">GPT-4o-mini</a>
                <a href="#" onclick="setModel('claude-3.5-sonnet')">Claude 3.5 Sonnet</a>
            </div>
        </div>
    </div>
    <div class="chat-container" id="chat-container"></div>
    <div class="input-container" id="input-container">
        <textarea id="prompt" placeholder="Сообщите ChatGPT..." onkeydown="checkEnter(event)"></textarea>
        <button onclick="sendMessage()">Отправить</button>
    </div>
    <script>
        let selectedModel = "gpt-4";

        function setModel(model) {
            selectedModel = model;
            document.querySelector('.header h1').textContent = model;
        }

        const ws = new WebSocket("ws://localhost:8000/ws");
        ws.onmessage = (event) => {
            const chatContainer = document.getElementById("chat-container");
            const botMessage = document.createElement("div");
            botMessage.className = "message bot";
            const botContent = document.createElement("div");
            botContent.className = "content";
            botContent.textContent = event.data;
            botMessage.appendChild(botContent);
            chatContainer.appendChild(botMessage);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        };

        function sendMessage() {
            const prompt = document.getElementById("prompt").value;
            if (!prompt.trim()) return;

            const chatContainer = document.getElementById("chat-container");

            // Add user message to chat
            const userMessage = document.createElement("div");
            userMessage.className = "message user";
            const userContent = document.createElement("div");
            userContent.className = "content";
            userContent.textContent = prompt;
            userMessage.appendChild(userContent);
            chatContainer.appendChild(userMessage);

            // Clear input field
            document.getElementById("prompt").value = "";

            // Send message to server
            ws.send(JSON.stringify({ model: selectedModel, prompt: prompt }));
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function checkEnter(event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }
    </script>
</body>
</html>
"""

# Главная страница
@app.get("/")
async def get_root():
    return HTMLResponse(html)

# WebSocket обработчик
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client = Client()
    message_history = []

    while True:
        try:
            data = await websocket.receive_text()
            request = eval(data)
            model = request.get("model")
            prompt = request.get("prompt")

            if model not in MODELS:
                await websocket.send_text("Ошибка: неподдерживаемая модель.")
                continue

            message_history.append({"role": "user", "content": prompt})

            def sync_stream():
                return client.chat.completions.create(
                    model=model,
                    messages=message_history,
                    stream=True,
                )

            stream = await anyio.to_thread.run_sync(sync_stream)
            
            assistant_message = ""
            buffer = ""
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    buffer += content
                    assistant_message += content
                    
                    # Отправляем текст, когда встречаем знак пунктуации или накопилось достаточно символов
                    if any(punct in buffer for punct in ['.', '!', '?', ',', '\n']) or len(buffer) > 50:
                        await websocket.send_text(buffer)
                        buffer = ""
            
            # Отправляем оставшийся текст в буфере
            if buffer:
                await websocket.send_text(buffer)
            
            message_history.append({"role": "assistant", "content": assistant_message})

        except Exception as e:
            await websocket.send_text(f"Ошибка: {str(e)}")
            break

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
