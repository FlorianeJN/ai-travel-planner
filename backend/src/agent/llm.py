from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()


def get_llm():
    return init_chat_model(
        "gemini-3.5-flash-lite", model_provider="google_genai", temperature=0.2
    )
