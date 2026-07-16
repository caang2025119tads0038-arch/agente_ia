# app/routes.py
from flask import render_template, request, jsonify
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.adk.apps import App as ADKApp
from google.genai import types
from app import app
from app.agent import root_agent

# 1. Instancia o serviço de sessões em memória de forma global
session_service = InMemorySessionService()

# 2. Define o objeto App do ADK (mantendo "app" para alinhar com a pasta física)
adk_app = ADKApp(
    name="app", 
    root_agent=root_agent
)

# 3. Inicializa o Runner
runner = Runner(
    app=adk_app,
    session_service=session_service
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
async def chat():
    data = request.json or {}
    user_message = data.get("message")
    session_id = data.get("session_id", "default_session")
    user_id = data.get("user_id", "default_user")

    if not user_message:
        return jsonify({"error": "Por favor, digite uma mensagem."}), 400

    try:
        # Garante que a sessão exista
        session = await session_service.get_session(
            app_name="app",
            user_id=user_id,
            session_id=session_id
        )
        if session is None:
            await session_service.create_session(
                app_name="app",
                user_id=user_id,
                session_id=session_id
            )

        response_text = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=user_message)]
            )
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        return jsonify({
            "response": response_text,
            "session_id": session_id
        })

    except Exception as e:
        error_msg = str(e)

        # 🔍 Identifica erro de cota (429) e retorna mensagem amigável
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            user_friendly = (
                "📚 Ops! Atingimos o limite de requisições da IA. "
                "Aguarde alguns instantes e tente novamente."
            )
            return jsonify({"error": user_friendly}), 429

        # Para outros erros inesperados, mensagem genérica (mas logamos no terminal)
        print(f"Erro inesperado: {error_msg}")  # visível no console do Flask
        return jsonify({"error": "Ocorreu um erro inesperado. Tente novamente mais tarde."}), 500