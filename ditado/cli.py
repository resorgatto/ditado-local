"""Linha de comando: `ditado ouvir` para ditar e os demais comandos para editar o glossário."""

import argparse
import sys
import time

from .glossario import Glossario

DURACAO_MINIMA = 0.3  # segundos; toques acidentais no atalho são ignorados


def ouvir(args: argparse.Namespace) -> None:
    import keyboard
    import winsound

    from .audio import TAXA, Gravador
    from .colar import colar
    from .transcricao import Transcritor

    print(f"Carregando o modelo '{args.modelo}' (o primeiro uso baixa o modelo)...")
    transcritor = Transcritor(args.modelo, args.dispositivo, args.idioma)
    gravador = Gravador()
    print(f"Pronto. Segure [{args.atalho}] enquanto fala. Ctrl+C para sair.")

    while True:
        keyboard.wait(args.atalho)
        gravador.iniciar()
        winsound.Beep(880, 60)
        while keyboard.is_pressed(args.atalho):
            time.sleep(0.02)
        audio = gravador.parar()
        winsound.Beep(660, 60)

        if len(audio) < DURACAO_MINIMA * TAXA:
            continue
        glossario = Glossario()  # relê a cada ditado para pegar edições feitas em outro terminal
        texto = transcritor.transcrever(audio, glossario.vocabulario())
        if not texto:
            continue
        texto = glossario.aplicar(texto)
        glossario.salvar()
        colar(texto)
        print(f"> {texto}")


def termo(args: argparse.Namespace) -> None:
    glossario = Glossario()
    glossario.adicionar(args.termo, favorito=args.favorito)
    glossario.salvar()
    print(f"Vocabulário: {args.termo}")


def trocar(args: argparse.Namespace) -> None:
    glossario = Glossario()
    glossario.adicionar(args.de, args.para)
    glossario.salvar()
    print(f"Substituição: {args.de} → {args.para}")


def remover(args: argparse.Namespace) -> None:
    glossario = Glossario()
    if not glossario.remover(args.termo):
        sys.exit(f"'{args.termo}' não está no glossário.")
    glossario.salvar()
    print(f"Removido: {args.termo}")


def listar(_: argparse.Namespace) -> None:
    glossario = Glossario()
    if not glossario.entradas:
        print("Glossário vazio. Comece com: ditado termo \"SeuTermo\"")
    for e in sorted(glossario.entradas, key=lambda e: e.termo.casefold()):
        estrela = "★ " if e.favorito else "  "
        destino = f" → {e.substituto}" if e.substituto else ""
        print(f"{estrela}{e.termo}{destino}  ({e.usos} usos)")
    print(f"\nArquivo: {glossario.arquivo}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="ditado", description="Ditado por voz offline com glossário pessoal.")
    sub = parser.add_subparsers(dest="comando")

    p = sub.add_parser("ouvir", help="segure o atalho, fale e o texto é colado no app em foco (padrão)")
    p.add_argument("--atalho", default="right ctrl", help='tecla ou combinação a segurar (padrão: "right ctrl")')
    p.add_argument("--modelo", default="small", help="modelo Whisper: tiny, base, small, medium, large-v3, turbo")
    p.add_argument("--dispositivo", default="cpu", choices=["cpu", "cuda"])
    p.add_argument("--idioma", default="pt")
    p.set_defaults(func=ouvir)

    p = sub.add_parser("termo", help="adiciona uma palavra ao vocabulário reconhecido")
    p.add_argument("termo")
    p.add_argument("--favorito", action="store_true", help="sempre envia este termo ao Whisper primeiro")
    p.set_defaults(func=termo)

    p = sub.add_parser("trocar", help="troca um trecho por outro depois da transcrição")
    p.add_argument("de")
    p.add_argument("para")
    p.set_defaults(func=trocar)

    p = sub.add_parser("remover", help="remove um termo do glossário")
    p.add_argument("termo")
    p.set_defaults(func=remover)

    sub.add_parser("listar", help="mostra o glossário").set_defaults(func=listar)

    args = parser.parse_args(sys.argv[1:] or ["ouvir"])
    args.func(args)


if __name__ == "__main__":
    main()
