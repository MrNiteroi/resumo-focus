"""Testes para src/baixar_focus.py."""

import datetime
import pathlib
import sys

import pytest

# Insere src/ no path para importar os módulos do projeto (como no demo.py)
SRC = pathlib.Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC))

from baixar_focus import ultima_segunda, baixar  # noqa: E402


# ---------------------------------------------------------------------------
# Testes puros (sem rede) para ultima_segunda
# ---------------------------------------------------------------------------

def test_quinta_recua_para_segunda_da_mesma_semana():
    # Quinta 2026-07-16 -> segunda 2026-07-13
    hoje = datetime.date(2026, 7, 16)
    assert ultima_segunda(hoje) == datetime.date(2026, 7, 13)


def test_terca_recua_para_segunda_da_mesma_semana():
    # Terça 2026-07-14 -> segunda 2026-07-13
    hoje = datetime.date(2026, 7, 14)
    assert ultima_segunda(hoje) == datetime.date(2026, 7, 13)


def test_segunda_recua_uma_semana():
    # Segunda 2026-07-20 -> segunda anterior 2026-07-13 (estritamente anterior)
    hoje = datetime.date(2026, 7, 20)
    assert ultima_segunda(hoje) == datetime.date(2026, 7, 13)


def test_domingo_recua_para_segunda_anterior():
    # Domingo 2026-07-19 -> segunda 2026-07-13
    hoje = datetime.date(2026, 7, 19)
    assert ultima_segunda(hoje) == datetime.date(2026, 7, 13)


def test_varredura_60_dias_sempre_segunda_anterior():
    # Para 60 dias consecutivos, o retorno deve ser sempre uma segunda-feira
    # (weekday == 0) e estritamente anterior à data dada.
    base = datetime.date(2026, 1, 1)
    for i in range(60):
        hoje = base + datetime.timedelta(days=i)
        resultado = ultima_segunda(hoje)
        assert resultado.weekday() == 0, f"{resultado} não é segunda-feira"
        assert resultado < hoje, f"{resultado} não é anterior a {hoje}"
        # A distância nunca passa de 7 dias
        assert (hoje - resultado).days <= 7


# ---------------------------------------------------------------------------
# Teste de rede (download real) — pule com -m "not network"
# ---------------------------------------------------------------------------

@pytest.mark.network
def test_baixar_download_real(tmp_path):
    data_pub, caminho = baixar(tmp_path)

    # O arquivo foi criado
    assert caminho.exists(), "arquivo não foi criado"

    # Conteúdo começa com os bytes mágicos de PDF
    conteudo = caminho.read_bytes()
    assert conteudo[:4] == b"%PDF", "arquivo não começa com %PDF"

    # Tamanho plausível para o boletim (> 50 KB)
    assert caminho.stat().st_size > 50 * 1024, "arquivo menor que 50 KB"

    # Nome do arquivo bate com a data de publicação retornada
    assert caminho.name == f"focus_{data_pub.isoformat()}.pdf"

    # Data dentro da janela esperada: não no futuro e no máximo ~10 dias atrás
    hoje = datetime.date.today()
    assert data_pub <= hoje, "data de publicação está no futuro"
    assert (hoje - data_pub).days <= 10, "data de publicação muito no passado"
