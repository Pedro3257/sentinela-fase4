"""Extratores locais e conectores Azure. Importações opcionais sob demanda."""
from array import array
import math
import os
import sys
import threading
import wave


def acoustic_features(path):
    with wave.open(str(path), "rb") as audio:
        if audio.getsampwidth() != 2 or audio.getnchannels() != 1 or audio.getcomptype() != "NONE":
            raise ValueError("Use WAV PCM mono de 16 bits")
        rate = audio.getframerate()
        values = array("h", audio.readframes(audio.getnframes()))
        if sys.byteorder != "little":
            values.byteswap()
    if not values:
        raise ValueError("Áudio vazio")
    window = max(1, round(rate * 0.03))
    rms = [math.sqrt(sum(x*x for x in values[i:i+window]) / len(values[i:i+window])) / 32768
           for i in range(0, len(values), window)]
    silent = [v < 0.015 for v in rms]
    longest = current = 0
    for flag in silent:
        current = current + 1 if flag else 0
        longest = max(longest, current)
    return {"duration_seconds": round(len(values)/rate, 3), "silence_ratio": round(sum(silent)/len(silent), 4),
            "longest_pause_seconds": round(longest * window/rate, 3), "rms_mean": round(sum(rms)/len(rms), 5),
            "method": "RMS em janelas de 30 ms; limiar fixo 0.015"}


def azure_transcribe(path, timeout=600):
    import azure.cognitiveservices.speech as speech
    config = speech.SpeechConfig(subscription=os.environ["AZURE_SPEECH_KEY"], region=os.environ["AZURE_SPEECH_REGION"])
    config.speech_recognition_language = "pt-BR"
    recognizer = speech.SpeechRecognizer(speech_config=config, audio_config=speech.audio.AudioConfig(filename=str(path)))
    done, parts, errors = threading.Event(), [], []

    def recognized(evt):
        if evt.result.reason == speech.ResultReason.RecognizedSpeech:
            parts.append(evt.result.text)

    def canceled(evt):
        if evt.reason == speech.CancellationReason.Error:
            errors.append(f"Azure Speech: {evt.reason}; código {evt.error_code}")
        done.set()

    recognizer.recognized.connect(recognized)
    recognizer.canceled.connect(canceled)
    recognizer.session_stopped.connect(lambda evt: done.set())
    recognizer.start_continuous_recognition_async().get()
    try:
        if not done.wait(timeout):
            raise TimeoutError("Tempo limite de transcrição; resultado parcial descartado")
    finally:
        recognizer.stop_continuous_recognition_async().get()
    if errors:
        raise RuntimeError("; ".join(errors))
    if not parts:
        raise ValueError("Nenhuma fala reconhecida")
    return " ".join(parts)


def azure_language(text):
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    if len(text) > 5000:
        raise ValueError("Texto excede 5000 caracteres; divida por trechos antes de enviar ao Language")
    client = TextAnalyticsClient(endpoint=os.environ["AZURE_LANGUAGE_ENDPOINT"], credential=AzureKeyCredential(os.environ["AZURE_LANGUAGE_KEY"]))
    try:
        sentiment = client.analyze_sentiment([text], language="pt")[0]
        phrases = client.extract_key_phrases([text], language="pt")[0]
        if sentiment.is_error or phrases.is_error:
            raise RuntimeError("Azure Language não conseguiu analisar o documento")
        return {"provider": "azure", "sentiment": sentiment.sentiment,
                "confidence": dict(positive=sentiment.confidence_scores.positive, neutral=sentiment.confidence_scores.neutral, negative=sentiment.confidence_scores.negative),
                "key_phrases": phrases.key_phrases}
    finally:
        client.close()


def analyze_audio(path, transcript=None, azure=False):
    features = acoustic_features(path)
    text = azure_transcribe(path) if azure else transcript
    if not text:
        raise ValueError("No modo local informe --transcript; não há STT local implícito")
    return {"transcript": text, "acoustic": features,
            "language": azure_language(text) if azure else {"provider": "local", "sentiment": "not_evaluated", "key_phrases": []},
            "transcription_source": "azure_speech" if azure else "user_supplied"}


def analyze_video(path, config, weights="yolov8n-pose.pt"):
    import cv2
    from ultralytics import YOLO
    model = YOLO(weights)
    capture = cv2.VideoCapture(str(path))
    fps = capture.get(cv2.CAP_PROP_FPS)
    if not capture.isOpened() or not math.isfinite(fps) or fps <= 0:
        capture.release()
        raise ValueError("Vídeo inválido ou FPS indisponível")
    findings, consecutive, reported = [], {}, set()
    index = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            # IDs persistentes evitam misturar pessoas em cenas com múltiplos pacientes.
            result = model.track(frame, persist=True, verbose=False, tracker="bytetrack.yaml")[0]
            visible = set()
            if result.keypoints is not None and result.boxes is not None and result.boxes.id is not None:
                points = result.keypoints.xy.cpu().tolist()
                confidences = result.keypoints.conf.cpu().tolist()
                ids = result.boxes.id.int().cpu().tolist()
                for track, xy, conf in zip(ids, points, confidences):
                    if min(conf[k] for k in (5, 6, 11, 12)) < 0.5:
                        continue
                    visible.add(track)
                    shoulder = [(xy[5][i] + xy[6][i])/2 for i in (0, 1)]
                    hip = [(xy[11][i] + xy[12][i])/2 for i in (0, 1)]
                    angle = math.degrees(math.atan2(abs(shoulder[0]-hip[0]), abs(shoulder[1]-hip[1])))
                    consecutive[track] = consecutive.get(track, 0)+1 if angle > config["video_trunk_angle_degrees"] else 0
                    if not consecutive[track]:
                        reported.discard(track)
                    duration = consecutive[track] / fps
                    if duration >= config["video_persistence_seconds"] and track not in reported:
                        findings.append({"offset_seconds": round(index/fps, 3), "track_id": track,
                                         "trunk_angle_degrees": round(angle, 2), "duration_seconds": round(duration, 3),
                                         "posture_deviation": True, "model": weights})
                        reported.add(track)
            for track in set(consecutive)-visible:
                consecutive.pop(track)
                reported.discard(track)
            index += 1
    finally:
        capture.release()
    if not index:
        raise ValueError("Nenhum frame decodificado")
    return {"model": weights, "frames": index, "fps": fps, "duration_seconds": index/fps, "findings": findings,
            "scope": "Inclinação de tronco em vídeo frontal de fisioterapia; não avalia falhas cirúrgicas"}
