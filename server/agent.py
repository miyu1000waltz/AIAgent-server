"""エージェントの組み立て

このファイルが「拡張の入口」。create_agent の各引数が、そのまま拡張ポイントになっている。
詳しくは README の「拡張のヒント」を参照。
"""

from typing import Literal

from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

from config import settings

# LLMに人格・出力内容を指示するシステムプロンプト。
# 出力フォーマット(JSON)は response_format で強制するため、ここでは書かない。
SYSTEM_PROMPT = (
    "あなたはユーザーと会話する、桃瀬ひよりです。フレンドリーかつ簡潔な日本語で応答してください。\n"
    "text にはセリフ本文、expression にはセリフに合う表情を入れてください。"
)


class LLMOutput(BaseModel):
    """LLMが返す構造化出力。Unity側(AIAgentController)のLLMOutputと項目を一致させる。

    expressionの取りうる値はUnity側 Live2DExpressionController.Exp3s のメンバー名と一致させる。
    """

    text: str = Field(description="セリフ本文")
    expression: Literal["normal", "smile"] = Field(description="セリフに合う表情")


def build_agent():
    model = init_chat_model(
        settings.MODEL,
        temperature=settings.TEMPERATURE,
        # 空文字ならNoneにし、ライブラリ側の環境変数(GOOGLE_API_KEY)読み込みに任せる
        api_key=settings.GOOGLE_API_KEY or None,
    )
    return create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        # ProviderStrategy: Gemini標準の構造化出力(responseSchema)を使う。LLM呼び出しは1回で済む。
        # (ToolStrategyにするとツール呼び出し経由になり、構造化出力非対応のモデルでも動くが往復が増える)
        response_format=ProviderStrategy(LLMOutput),
        # --- ここから下が拡張ポイント。現状はすべて空(=会話履歴なし・ツールなし) ---
        tools=[],            # 関数ツール / RAGの検索 / MCPツール
        middleware=[],       # ガードレール / 会話の要約 / 人間の承認
        checkpointer=None,   # 会話メモリ(短期記憶)。InMemorySaver / Redis / Postgres
        store=None,          # ユーザーごとの長期記憶
    )
