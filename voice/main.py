import logging
import uuid
import vosk
import json

from fastapi import FastAPI
from fastapi.websockets import (
    WebSocket,
    WebSocketDisconnect,
)

# Get logger
logger = logging.getLogger(__name__)

# Vosk model object
model = vosk.Model(model_path='vosk-model-small-ja-0.22')

# Fast API application
application = FastAPI()


@application.websocket("ws-voice/{voice_id}/")
async def onconnect(websocket: WebSocket, voice_id: uuid.UUID):
    
    # Awaiting connection
    await websocket.accept()

    # Recognizer
    recognizer = vosk.KaldiRecognizer(model, 16000)
    
    try:
        # Mainloop
        while True:
            
            # Get audio chunk-stream
            data = await websocket.receive_bytes()

            if recognizer.AcceptWaveform(data):

                # Case where voice-message is not completed
                result = recognizer.Result()
                result_dict = json.loads(result)
                
                # Check key of result dict
                if "text" in result_dict:
                    await websocket.send_text({"text": result_dict["text"], "is_completed": True})
                    await websocket.close()

            else:
                # Case where voice-message is not partial
                partial = recognizer.PartialResult()
                partial_dict = json.loads(partial)

                # Check key of partial result dict
                if "partial" in partial_dict:
                    await websocket.send_text({"text": partial_dict["partial"], "is_completed": False})
    
    except WebSocketDisconnect:
        ...