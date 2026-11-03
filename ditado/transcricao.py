"""Transcrição offline com faster-whisper.

O vocabulário do glossário entra como `hotwords`: o Whisper recebe esses termos
como contexto e passa a preferir essas grafias quando o som é parecido.
"""

import numpy as np
from faster_whisper import WhisperModel


class Transcritor:
    def __init__(self, modelo: str = "small", dispositivo: str = "cpu", idioma: str = "pt"):
        precisao = "int8" if dispositivo == "cpu" else "float16"
        self.modelo = WhisperModel(modelo, device=dispositivo, compute_type=precisao)
        self.idioma = idioma

    def transcrever(self, audio: np.ndarray, vocabulario: list[str] | None = None) -> str:
        segmentos, _ = self.modelo.transcribe(
            audio,
            language=self.idioma,
            hotwords=", ".join(vocabulario) if vocabulario else None,
            vad_filter=True,
            beam_size=5,
        )
        return " ".join(segmento.text.strip() for segmento in segmentos).strip()
