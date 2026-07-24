"""Módulo para download do boletim Focus do Banco Central do Brasil."""

import datetime
import pathlib
import requests

URL_BASE = "https://www.bcb.gov.br/content/focus/focus/R{data}.pdf"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
MAX_TENTATIVAS = 7


def ultima_segunda(hoje: datetime.date) -> datetime.date:
    """Retorna a segunda-feira mais recente ESTRITAMENTE anterior a `hoje`.

    Se hoje já é segunda, recua para a segunda da semana passada.
    """
    # weekday(): segunda=0, ..., domingo=6
    # Dias a recuar para chegar à última segunda (nunca zero)
    dias = hoje.weekday() or 7  # se weekday==0 (segunda), recua 7 dias
    return hoje - datetime.timedelta(days=dias)


def baixar(dest: str | pathlib.Path) -> tuple[datetime.date, pathlib.Path]:
    """Baixa o PDF mais recente do Focus para a pasta `dest`.

    Parte da última segunda-feira e recua dia a dia até 7 tentativas,
    cobrindo feriados em que o BCB publica na terça (ou outro dia útil).

    Valida que o conteúdo começa com b'%PDF' antes de aceitar.

    Retorna (data_da_publicacao, caminho_do_arquivo).
    Levanta RuntimeError se nenhuma tentativa obtiver o PDF.
    """
    dest = pathlib.Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    sessao = requests.Session()
    sessao.headers.update({"User-Agent": USER_AGENT})

    data_candidata = ultima_segunda(datetime.date.today())

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        data_str = data_candidata.strftime("%Y%m%d")  # AAAAMMDD sem hífens
        url = URL_BASE.format(data=data_str)

        print(f"Tentativa {tentativa}: {url}")
        resposta = sessao.get(url, timeout=30)

        if resposta.status_code == 200 and resposta.content[:4] == b"%PDF":
            # Conteúdo válido: salva com a convenção focus_AAAA-MM-DD.pdf
            nome_arquivo = dest / f"focus_{data_candidata.isoformat()}.pdf"
            nome_arquivo.write_bytes(resposta.content)
            return data_candidata, nome_arquivo

        # PDF não encontrado nesta data; recua um dia
        data_candidata -= datetime.timedelta(days=1)

    raise RuntimeError(
        f"PDF do Focus não encontrado após {MAX_TENTATIVAS} tentativas."
    )


def main() -> None:
    """Baixa o Focus para data/ e exibe o caminho e tamanho."""
    pasta_dados = pathlib.Path(__file__).parent.parent / "data"
    data_pub, caminho = baixar(pasta_dados)
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"\nArquivo salvo: {caminho}")
    print(f"Data de publicação: {data_pub.isoformat()}")
    print(f"Tamanho: {tamanho_kb:.1f} KB")


if __name__ == "__main__":
    main()
