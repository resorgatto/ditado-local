"""Glossário pessoal guardado num arquivo JSON.

Cada entrada é um termo. Termos sem substituto viram vocabulário para o Whisper
reconhecer melhor (nomes próprios, siglas, jargões). Termos com substituto são
trocados no texto depois da transcrição.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

ARQUIVO_PADRAO = Path(os.environ.get("APPDATA", Path.home())) / "ditado" / "glossario.json"


@dataclass
class Entrada:
    termo: str
    substituto: str | None = None
    favorito: bool = False
    usos: int = 0
    ultimo_uso: str | None = None
    criado: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


class Glossario:
    def __init__(self, arquivo: Path = ARQUIVO_PADRAO):
        self.arquivo = Path(arquivo)
        dados = json.loads(self.arquivo.read_text("utf-8")) if self.arquivo.exists() else []
        self.entradas = [Entrada(**item) for item in dados]

    def salvar(self) -> None:
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        dados = [asdict(entrada) for entrada in self.entradas]
        self.arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), "utf-8")

    def buscar(self, termo: str) -> Entrada | None:
        chave = termo.casefold()
        return next((e for e in self.entradas if e.termo.casefold() == chave), None)

    def adicionar(self, termo: str, substituto: str | None = None, favorito: bool = False) -> Entrada:
        termo = termo.strip()
        if not termo:
            raise ValueError("O termo não pode ser vazio.")
        entrada = self.buscar(termo)
        if entrada:
            entrada.substituto, entrada.favorito = substituto, favorito or entrada.favorito
        else:
            entrada = Entrada(termo, substituto, favorito)
            self.entradas.append(entrada)
        return entrada

    def remover(self, termo: str) -> bool:
        entrada = self.buscar(termo)
        if entrada:
            self.entradas.remove(entrada)
        return entrada is not None

    def vocabulario(self, limite: int = 50, agora: datetime | None = None) -> list[str]:
        """Termos sem substituto, dos mais relevantes para os menos.

        Ordem: favoritos, depois os usados há menos tempo (até 1 dia, até 14 dias,
        resto), depois os mais usados e, por fim, ordem alfabética.
        """
        agora = agora or datetime.now()

        def recencia(entrada: Entrada) -> int:
            if not entrada.ultimo_uso:
                return 2
            idade = agora - datetime.fromisoformat(entrada.ultimo_uso)
            return 0 if idade <= timedelta(days=1) else 1 if idade <= timedelta(days=14) else 2

        termos = [e for e in self.entradas if not e.substituto]
        termos.sort(key=lambda e: (not e.favorito, recencia(e), -e.usos, e.termo.casefold()))
        return [e.termo for e in termos[:limite]]

    def aplicar(self, texto: str, agora: datetime | None = None) -> str:
        """Troca os termos que têm substituto e marca o uso dos termos encontrados.

        Se o ditado inteiro for só um termo com substituto (ignorando pontuação),
        devolve apenas o substituto. É assim que funcionam os atalhos de texto:
        dite "meu email" e o endereço completo é colado.
        """
        quando = (agora or datetime.now()).isoformat(timespec="seconds")
        substituicoes = {e.termo.casefold(): e for e in self.entradas if e.substituto}

        inteiro = substituicoes.get(_sem_pontuacao(texto).casefold())
        if inteiro:
            _marcar_uso(inteiro, quando)
            return inteiro.substituto

        if substituicoes:
            termos = sorted(substituicoes, key=len, reverse=True)
            padrao = re.compile(r"(?<!\w)(?:" + "|".join(map(re.escape, termos)) + r")(?!\w)", re.IGNORECASE)

            def trocar(achado: re.Match) -> str:
                entrada = substituicoes[achado.group(0).casefold()]
                _marcar_uso(entrada, quando)
                return entrada.substituto

            texto = padrao.sub(trocar, texto)

        minusculo = texto.casefold()
        for entrada in self.entradas:
            if not entrada.substituto and re.search(r"(?<!\w)" + re.escape(entrada.termo.casefold()) + r"(?!\w)", minusculo):
                _marcar_uso(entrada, quando)
        return texto


def _sem_pontuacao(texto: str) -> str:
    return re.sub(r"[^\w\s]", "", texto).strip()


def _marcar_uso(entrada: Entrada, quando: str) -> None:
    entrada.usos += 1
    entrada.ultimo_uso = quando
