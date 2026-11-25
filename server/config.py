from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Gemini APIキー(Google AI Studioで発行)。.env または環境変数で渡す
    GOOGLE_API_KEY: str = ""
    # LangChainのinit_chat_modelに渡す "プロバイダ:モデル名"。
    # 例: "openai:<モデル名>" / "anthropic:<モデル名>" に変えれば他社モデルにも切り替えられる
    # (対応する langchain-openai / langchain-anthropic 等の追加インストールとAPIキーが必要)
    MODEL: str = "google_genai:gemini-3.5-flash-lite"
    TEMPERATURE: float = 0.7

    model_config = {"env_file": ".env"}


settings = Settings()
