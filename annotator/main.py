import openai
import json

from decouple import config
from pydantic import BaseModel
from fastapi import FastAPI, Body
from fastapi.exceptions import HTTPException


class Request(BaseModel):

    # OpenAI role
    description: str

    # OpenAI content
    content: str


# Create FastAPI application
application = FastAPI()

# Create OpenAI API client
client = openai.Client(api_key=config("ANNOTATOR_OPENAI_API_KEY"))

# Create OpenAI tools
functions = [
    {
        "name": "annotate",
        "type": "function",
        "description": "議論内容を分析し、要約、提案、批判、評価、ポリシー違反の警告を提供します。",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "議論全体の簡潔な要約。",
                    "maxLength": 255,
                },
                "suggestion": {
                    "type": "string",
                    "description": "議論の方向性や内容に関する提案。",
                    "maxLength": 255
                },
                "criticism": {
                    "type": "string",
                    "description": "論理的な洞察や発話内容の間違いに関する批判。",
                    "maxLength": 255
                },
                "evaluation": {
                    "type": "string",
                    "description": "発話内容に対する批判を踏まえた評価。",
                    "maxLength": 255
                },
                "warning": {
                    "type": "string",
                    "description": "ポリシー違反やメンバーの行動に関する警告。",
                    "maxLength": 255
                }
            },
            "required": ["summary", "suggestion", "evaluation"]
        }
    }
]


@application.post("/ai/annotate/")
async def onannotate(request: Request = Body(...)):
    """
    Annotate meeting contents
    """

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "あなたは議長です。"
                        "以下のポリシーに従って議論中の発言を分析し、注釈を生成してください。"
                        "- 感情的にならず、中立的であること。"
                        "- 論理的で批判的な視点を持つこと。"
                        "- 議論メンバーの意見を適切に要約、批判、評価すること。"
                        "- 議題から外れた発言があれば指摘すること。"
                        "- 議論に協力的な態度で注釈を生成すること。"
                        "- 批判や指摘は明確に行うようにすること。"
                        "- 警告が過度に厳格にならないように注釈を生成すること。"
                        "- 批判と警告に関しては、必要のない場合は省略すること。"
                        "- 常に日本語で回答すること。"
                        "- 注釈のテキストにはHTMLタグを含めないこと。"
                        "以下が議論内容です。"
                        "<TOPIC>{}</TOPIC>"
                    ).format(request.description)
                },
                {
                    "role": "user",
                    "content": (
                        "以下の発言の注釈を生成してください。"
                        "<MESSAGE>{}</MESSAGE>"
                    ).format(request.content)
                }
            ],
            functions=functions,
            function_call={"name": "annotate"},
            temperature=1.0,
        ).choices[0].message.function_call.arguments

        # Parse response and return
        return json.loads(response)

    except Exception as e:

        # Return error
        raise HTTPException(status_code=500)
