import os
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch

from sentinela.media import azure_transcribe, azure_language, analyze_video
from test_core import CONFIG


class Signal:
    def connect(self, callback):
        self.callback = callback


class MediaTests(unittest.TestCase):
    def speech(self, fail=False):
        module = ModuleType("azure.cognitiveservices.speech")
        module.SpeechConfig = lambda **kw: NS(**kw)
        module.audio = NS(AudioConfig=lambda **kw: NS(**kw))
        module.ResultReason = NS(RecognizedSpeech="recognized")
        module.CancellationReason = NS(Error="error")

        class Recognizer:
            def __init__(self, **kw):
                self.recognized, self.canceled, self.session_stopped = Signal(), Signal(), Signal()

            def start_continuous_recognition_async(self):
                if fail:
                    self.canceled.callback(NS(reason="error", error_code="auth"))
                else:
                    for text in ["Primeira frase.", "Segunda frase."]:
                        self.recognized.callback(NS(result=NS(reason="recognized", text=text)))
                    self.session_stopped.callback(None)
                return NS(get=lambda: None)

            def stop_continuous_recognition_async(self):
                return NS(get=lambda: None)

        module.SpeechRecognizer = Recognizer
        return {"azure": ModuleType("azure"), "azure.cognitiveservices": ModuleType("azure.cognitiveservices"),
                "azure.cognitiveservices.speech": module}

    def test_speech_continuous_keeps_multiple_segments(self):
        with patch.dict(sys.modules, self.speech()), patch.dict(os.environ, AZURE_SPEECH_KEY="fake", AZURE_SPEECH_REGION="fake"):
            self.assertEqual(azure_transcribe("fake.wav"), "Primeira frase. Segunda frase.")

    def test_speech_error_not_faked(self):
        with patch.dict(sys.modules, self.speech(True)), patch.dict(os.environ, AZURE_SPEECH_KEY="fake", AZURE_SPEECH_REGION="fake"):
            with self.assertRaises(RuntimeError):
                azure_transcribe("fake.wav")

    def test_language_result(self):
        module = ModuleType("azure.ai.textanalytics")
        class Client:
            def __init__(self, **kw): pass
            def analyze_sentiment(self, *args, **kw):
                return [NS(is_error=False, sentiment="negative", confidence_scores=NS(positive=.01, neutral=.09, negative=.9))]
            def extract_key_phrases(self, *args, **kw):
                return [NS(is_error=False, key_phrases=["falta de ar"])]
            def close(self): pass
        module.TextAnalyticsClient = Client
        credentials = ModuleType("azure.core.credentials")
        credentials.AzureKeyCredential = lambda key: key
        modules = {name: ModuleType(name) for name in ["azure", "azure.ai", "azure.core"]}
        modules.update({"azure.ai.textanalytics": module, "azure.core.credentials": credentials})
        with patch.dict(sys.modules, modules), patch.dict(os.environ, AZURE_LANGUAGE_KEY="fake", AZURE_LANGUAGE_ENDPOINT="https://example.invalid"):
            result = azure_language("Tenho falta de ar")
            self.assertEqual(result["sentiment"], "negative")
            self.assertEqual(result["key_phrases"], ["falta de ar"])

    def test_video_persistence_and_report(self):
        class Tensor:
            def __init__(self, data): self.data = data
            def cpu(self): return self
            def int(self): return self
            def tolist(self): return self.data
        xy = [[0, 0] for _ in range(17)]
        xy[5], xy[6], xy[11], xy[12] = [100, 10], [120, 10], [10, 40], [30, 40]
        result = NS(keypoints=NS(xy=Tensor([xy]), conf=Tensor([[.95]*17])), boxes=NS(id=Tensor([7])))
        class Capture:
            frames = 0
            def get(self, prop): return 10
            def isOpened(self): return True
            def read(self):
                self.frames += 1
                return (True, object()) if self.frames <= 30 else (False, None)
            def release(self): pass
        cv = ModuleType("cv2")
        cv.VideoCapture, cv.CAP_PROP_FPS = lambda path: Capture(), 5
        ultra = ModuleType("ultralytics")
        ultra.YOLO = lambda weights: NS(track=lambda *args, **kw: [result])
        with patch.dict(sys.modules, {"cv2": cv, "ultralytics": ultra}):
            report = analyze_video("fake.mp4", CONFIG)
        self.assertEqual(report["frames"], 30)
        self.assertEqual(len(report["findings"]), 1)
        self.assertEqual(report["findings"][0]["track_id"], 7)
        self.assertEqual(report["findings"][0]["duration_seconds"], 2)
