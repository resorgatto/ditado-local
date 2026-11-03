<div align="center">

# 🎙️ ditado-local

**Segure uma tecla, fale e o texto aparece onde está o cursor. Tudo offline, no seu PC.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&logo=python&logoColor=white)
![Whisper](https://img.shields.io/badge/Whisper-offline-412991?style=flat-square)
![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078d4?style=flat-square&logo=windows&logoColor=white)
![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-f4c430?style=flat-square)

</div>

---

O `ditado-local` transforma voz em texto em qualquer programa: e-mail, Teams, VS Code, navegador. O reconhecimento roda no seu computador com [faster-whisper](https://github.com/SYSTRAN/faster-whisper). Depois que o modelo é baixado, nenhum áudio sai da máquina.

O diferencial é o **glossário pessoal**. Ele ensina o Whisper a escrever os nomes que você usa no dia a dia e corrige o que ele ainda erra.

## O glossário na prática

A mesma frase falada, transcrita três vezes:

| | Resultado |
| --- | --- |
| Whisper puro | Amanhã eu reviso as tarefas do LARN em 360 no **clique A** e mando o resumo para o **Nicolás Pellutimus**. |
| \+ vocabulário | Amanhã eu reviso as tarefas do LARNING 360 no **ClickUp** e mando o resumo para o **Nicolas** pelo **Teams**. |
| \+ substituição | Amanhã eu reviso as tarefas do **Learning360** no ClickUp e mando o resumo para o Nicolas pelo Teams. |

O glossário faz três coisas:

- 🧠 **Vocabulário:** palavras que o Whisper deve reconhecer (nomes, siglas, produtos). Elas vão para o modelo como contexto a cada ditado.
- 🔁 **Substituições:** trocas feitas no texto depois da transcrição, para o que o modelo insiste em errar.
- ⚡ **Atalhos de texto:** se o ditado inteiro for só o gatilho de uma substituição, o texto completo é colado no lugar. Dite "meu email" e sai `renato@exemplo.com`.

O vocabulário é enviado ao modelo em ordem de relevância: primeiro os favoritos, depois os usados recentemente e por fim os mais usados. Assim os termos que importam agora nunca ficam de fora.

## Instalação

Requer Windows 10 ou 11 e Python 3.10 ou mais recente.

```powershell
git clone https://github.com/resorgatto/ditado-local.git
cd ditado-local
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## Uso

```powershell
ditado
```

1. Na primeira vez, o modelo é baixado (cerca de 480 MB para o `small`).
2. Quando aparecer **Pronto**, coloque o cursor onde quer escrever.
3. **Segure o Ctrl direito**, fale e solte. Um bipe marca o início e outro o fim.
4. O texto é colado no app em foco, e o que estava na área de transferência é restaurado.

### Montando o glossário

```powershell
ditado termo "Learning360" --favorito     # vocabulário, sempre enviado primeiro
ditado termo "ClickUp"                    # vocabulário
ditado trocar "larning 360" "Learning360" # substituição
ditado trocar "meu email" "renato@exemplo.com"  # atalho de texto
ditado listar
ditado remover "ClickUp"
```

Os comandos funcionam com o ditado aberto: o glossário é relido a cada ditado.
Ele fica em `%APPDATA%\ditado\glossario.json`, um JSON simples que você pode editar ou versionar.

### Opções

```powershell
ditado ouvir --atalho "ctrl+shift+space" --modelo medium --idioma pt --dispositivo cpu
```

| Opção | Padrão | Descrição |
| --- | --- | --- |
| `--atalho` | `right ctrl` | Tecla ou combinação a segurar enquanto fala. |
| `--modelo` | `small` | `tiny`, `base`, `small`, `medium`, `large-v3` ou `turbo`. Maior é mais preciso e mais lento. |
| `--idioma` | `pt` | Idioma falado. |
| `--dispositivo` | `cpu` | Use `cuda` para placa NVIDIA (precisa de cuBLAS e cuDNN, veja a [documentação do faster-whisper](https://github.com/SYSTRAN/faster-whisper#gpu)). |

No `small` em CPU, uma frase de 7 segundos leva cerca de 4 segundos para transcrever.

## Como funciona

```text
segura o atalho ──► grava o microfone (16 kHz, mono)
solta o atalho  ──► Whisper transcreve, com o vocabulário como contexto
                ──► glossário aplica substituições e atalhos
                ──► cola no app em foco e registra o uso dos termos
```

| Módulo | Papel |
| --- | --- |
| [`ditado/audio.py`](ditado/audio.py) | Grava o microfone no formato do Whisper. |
| [`ditado/transcricao.py`](ditado/transcricao.py) | Carrega o modelo e transcreve com o vocabulário. |
| [`ditado/glossario.py`](ditado/glossario.py) | Guarda os termos, ordena o vocabulário e aplica as substituições. |
| [`ditado/colar.py`](ditado/colar.py) | Cola o texto e restaura a área de transferência. |
| [`ditado/cli.py`](ditado/cli.py) | Comandos de linha e o laço do ditado. |

## Problemas comuns

**`Error opening InputStream ... [MME error 1]` ao segurar o atalho.** O Windows está bloqueando o microfone para o Python. Abra *Configurações › Privacidade e segurança › Microfone* e ligue o acesso. Se o seu Python veio da Microsoft Store, ele aparece na lista de apps como **Python** e precisa ser ligado individualmente.

## Limites

- **Só Windows:** usa `winsound` para os bipes e o atalho global da biblioteca `keyboard`.
- **Sem formatação por IA:** o texto sai como o Whisper escreve, que já vem pontuado, mas não reescrito.
- **Colagem por Ctrl+V:** apps que bloqueiam colar não recebem o texto.
- **Substituições por palavra inteira:** "ação" não troca dentro de "ações".

## Desenvolvimento

```powershell
python -m unittest
```

## Licença

[MIT](LICENSE) © Renato Sorgatto
