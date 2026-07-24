"""Demo: roda o pipeline completo do Focus localmente (download + extração)."""

import argparse
import pathlib
import sys
import webbrowser

# Adiciona a pasta src/ ao path para importar os módulos do projeto
SRC = pathlib.Path(__file__).parent / "src"
sys.path.insert(0, str(SRC))

from baixar_focus import baixar  # noqa: E402
from extrair_texto import extrair  # noqa: E402


def main() -> None:
    """Executa o pipeline: baixa o PDF do Focus e extrai o texto."""
    parser = argparse.ArgumentParser(
        description="Roda o pipeline do Focus: baixa o PDF e extrai o texto."
    )
    parser.add_argument(
        "--abrir",
        action="store_true",
        help="Abre o .txt gerado no navegador padrão ao final.",
    )
    args = parser.parse_args()

    pasta_dados = pathlib.Path(__file__).parent / "data"

    # Etapa 1: download do PDF
    _data_pub, caminho_pdf = baixar(pasta_dados)
    tamanho_kb = caminho_pdf.stat().st_size / 1024
    print(f"[1/2] PDF baixado: {caminho_pdf.name} ({tamanho_kb:.1f} KB)")

    # Etapa 2: extração do texto
    caminho_txt = extrair(caminho_pdf)
    print(f"[2/2] Texto extraído: {caminho_txt}")

    # Abre o .txt no navegador se a flag --abrir foi passada
    if args.abrir:
        webbrowser.open(caminho_txt.resolve().as_uri())


if __name__ == "__main__":
    main()
