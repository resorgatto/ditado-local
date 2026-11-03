"""Gravação do microfone no formato que o Whisper espera: 16 kHz, mono, float32."""

import numpy as np
import sounddevice as sd

TAXA = 16_000


class Gravador:
    def __init__(self, taxa: int = TAXA):
        self.taxa = taxa
        self._blocos: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None

    def iniciar(self) -> None:
        self._blocos = []
        self._stream = sd.InputStream(
            samplerate=self.taxa,
            channels=1,
            dtype="float32",
            callback=lambda dados, *_: self._blocos.append(dados.copy()),
        )
        self._stream.start()

    def parar(self) -> np.ndarray:
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if not self._blocos:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(self._blocos).flatten()
