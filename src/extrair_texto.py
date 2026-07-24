"""Módulo para extração de texto dos PDFs do boletim Focus."""

import argparse
import pathlib
import sys
import pdfplumber


def extrair(pdf_path: str | pathlib.Path) -> pathlib.Path:
    """Extrai o texto de todas as páginas do PDF e salva como .txt (UTF-8).

    O arquivo de saída tem o mesmo nome do PDF, trocando a extensão para .txt.
    Retorna o caminho do arquivo .txt gerado.
    """
    pdf_path = pathlib.Path(pdf_path)

    partes = []  # texto de cada página
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            # extract_text() pode retornar None em páginas sem texto
            texto = pagina.extract_text() or ""
            partes.append(texto)

    # Junta as páginas separando por quebra de linha
    texto_completo = "\n".join(partes)

    # Mesmo nome do PDF, com extensão .txt
    txt_path = pdf_path.with_suffix(".txt")
    txt_path.write_text(texto_completo, encoding="utf-8")

    return txt_path


def _pdf_mais_recente(pasta_dados: pathlib.Path) -> pathlib.Path | None:
    """Retorna o focus_*.pdf mais recente da pasta de dados, ou None."""
    pdfs = sorted(pasta_dados.glob("focus_*.pdf"))
    return pdfs[-1] if pdfs else None


def main() -> int:
    """CLI: extrai texto de um PDF específico (--pdf) ou do mais recente."""
    parser = argparse.ArgumentParser(
        description="Extrai o texto de um PDF do Focus e salva como .txt."
    )
    parser.add_argument(
        "--pdf",
        help="Caminho de um PDF específico. Se omitido, usa o mais recente de data/.",
    )
    args = parser.parse_args()

    if args.pdf:
        pdf_path = pathlib.Path(args.pdf)
    else:
        # Sem --pdf: procura o focus_*.pdf mais recente em data/
        pasta_dados = pathlib.Path(__file__).parent.parent / "data"
        pdf_path = _pdf_mais_recente(pasta_dados)
        if pdf_path is None:
            print(
                "Erro: nenhum PDF encontrado em data/.\n"
                "Rode 'python src/baixar_focus.py' primeiro para baixar o Focus.",
                file=sys.stderr,
            )
            return 1

    txt_path = extrair(pdf_path)
    tamanho_kb = txt_path.stat().st_size / 1024
    print(f"Texto extraído: {txt_path}")
    print(f"Tamanho: {tamanho_kb:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
