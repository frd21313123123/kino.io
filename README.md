# AI Model Interface

Это веб-приложение позволяет взаимодействовать с различными AI моделями через удобный интерфейс.

## Возможности

- Выбор модели из списка доступных
- Обмен сообщениями с моделью в реальном времени
- Индикация печатания ответа модели

## Технологии

- **Backend**: FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **WebSocket**: Для реального времени обмена сообщениями

## Установка

1. **Клонируйте репозиторий:**

    ```bash
    git clone https://github.com/ВашеИмяПользователя/my_project.git
    cd my_project
    ```

2. **Создайте виртуальное окружение и активируйте его:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Для Windows: venv\Scripts\activate
    ```

3. **Установите зависимости:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Запустите приложение локально:**

    ```bash
    python app.py
    ```

    Откройте браузер и перейдите по адресу `http://localhost:8000`.

## Развертывание на Heroku

1. **Установите Heroku CLI:** Следуйте инструкциям на [официальном сайте](https://devcenter.heroku.com/articles/heroku-cli).

2. **Войдите в Heroku:**

    ```bash
    heroku login
    ```

3. **Создайте приложение на Heroku:**

    ```bash
    heroku create ваше-имя-приложения
    ```

4. **Добавьте все файлы в Git и сделайте коммит:**

    ```bash
    git add .
    git commit -m "Initial commit"
    ```

5. **Разверните приложение на Heroku:**

    ```bash
    git push heroku main
    ```

6. **Откройте приложение:**

    ```bash
    heroku open
    ```

## Примечания

- **Переменные окружения:** Если ваше приложение требует секретных ключей или других переменных окружения, настройте их через панель управления Heroku или используя Heroku CLI:

    ```bash
    heroku config:set KEY=VALUE
    ```

- **Логи:** Для просмотра логов приложения используйте:

    ```bash
    heroku logs --tail
    ```

## Лицензия

Этот проект лицензирован под [MIT License](LICENSE).

