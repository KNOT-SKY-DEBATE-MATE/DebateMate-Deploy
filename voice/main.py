import logging
import uuid
import vosk
import json

from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect

# ロガーの取得
logger = logging.getLogger(__name__)

# Vosk モデルの初期化
model = vosk.Model(model_path='vosk-model-small-ja-0.22')

# FastAPI アプリケーションの作成
application = FastAPI()

@application.websocket("/ws-voice/{voice_id}/")
async def onconnect(websocket: WebSocket, voice_id: uuid.UUID):
    await websocket.accept()
    recognizer = vosk.KaldiRecognizer(model, 16000)
    
    try:
        while True:
            data = await websocket.receive_bytes()

            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                result_dict = json.loads(result)
                
                if "text" in result_dict:
                    await websocket.send_text(
                        json.dumps({
                            "text": result_dict["text"],
                            "is_completed": True,
                        })
                    )
                    # 接続終了の呼び出しはここでは行わない
            else:
                partial = recognizer.PartialResult()
                partial_dict = json.loads(partial)

                if "partial" in partial_dict:
                    await websocket.send_text(
                        json.dumps({
                            "text": partial_dict["partial"],
                            "is_completed": False,
                        })
                    )
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # 最終的に接続を閉じる
        await websocket.close()
