from pathlib import Path

ARQUIVO_ENTRADA = Path(r"C:\LabKeylogger\eventos.txt")
ARQUIVO_SAIDA = Path(r"C:\LabKeylogger\eventos_processados.txt")


def processar():
    if not ARQUIVO_ENTRADA.exists():
        print("Arquivo de eventos não encontrado.")
        return

    resultado = []

    with ARQUIVO_ENTRADA.open("r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()

            if not linha:
                continue

            # Mantém cada evento, mas deixa o formato mais fácil de analisar.
            if "KEY_DOWN:" in linha:
                horario, evento = linha.split("] KEY_DOWN: ", 1)
                resultado.append(
                    f"{horario}] DOWN -> {evento}"
                )

            elif "KEY_UP:" in linha:
                horario, evento = linha.split("] KEY_UP: ", 1)
                resultado.append(
                    f"{horario}] UP   -> {evento}"
                )

    ARQUIVO_SAIDA.write_text(
        "\n".join(resultado),
        encoding="utf-8"
    )

    print("Processamento concluído.")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")
    print("\n===== EVENTOS PROCESSADOS =====\n")

    for linha in resultado:
        print(linha)


if __name__ == "__main__":
    processar()