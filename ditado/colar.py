"""Cola o texto no app em foco pela área de transferência, preservando o que já estava nela."""

import time

import keyboard
import pyperclip


def colar(texto: str) -> None:
    anterior = pyperclip.paste()
    pyperclip.copy(texto)
    keyboard.send("ctrl+v")
    # ponytail: espera fixa antes de restaurar; apps lentos podem colar o conteúdo antigo, aumente se acontecer
    time.sleep(0.2)
    pyperclip.copy(anterior)
