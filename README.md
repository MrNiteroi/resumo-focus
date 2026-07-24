# Focus BCB — Pipeline de Coleta e Resumo

Pipeline que baixa o boletim **Focus** do Banco Central do Brasil, extrai o
texto do PDF e — numa automação agendada — gera um **resumo executivo** e o
envia por e-mail.

## Como funciona

O projeto tem duas camadas com responsabilidades bem separadas:

- **Scripts Python (`src/`)**: apenas **baixam** o PDF e **extraem** o texto.
  Não interpretam conteúdo nem escrevem resumos.
- **Resumo executivo**: é escrito por um **agente** que lê o texto extraído.
  Regra de ouro: o agente nunca inventa números — toda mediana ou valor
  citado precisa estar presente no texto original do PDF.

Ou seja: o código cuida da mecânica (download + extração); a análise e a
redação do resumo são feitas pelo agente a partir do texto.

## Estrutura de pastas

```
.
├── src/                        # Código-fonte (download e extração)
│   ├── baixar_focus.py         # Baixa o PDF mais recente do Focus
│   └── extrair_texto.py        # Extrai o texto do PDF para .txt
├── tests/                      # Testes (unitários e de rede)
├── data/                       # PDFs e textos brutos baixados
├── output/
│   └── focus/                  # Resumos em markdown gerados (versionado)
├── .github/
│   └── workflows/              # Automação semanal (GitHub Actions)
├── demo.py                     # Roda o pipeline local (download + extração)
├── requirements.txt            # Dependências fixadas
└── pytest.ini                  # Config de testes (marker network, testpaths)
```

## Convenções

- **Arquivos**: `focus_AAAA-MM-DD.{pdf,txt,md}` (data ISO da publicação).
- **`data/`**: PDFs e textos brutos.
- **`output/focus/`**: resumos em markdown.

## Como rodar localmente

```bash
# 1. Crie e ative um ambiente virtual (recomendado)
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # PowerShell (Windows)
# source .venv/bin/activate         # bash/zsh (Linux/macOS)

# 2. Instale as dependências (versões fixadas)
python -m pip install -r requirements.txt

# 3. Rode o pipeline completo (baixa o PDF e extrai o texto)
python demo.py

# Opcional: abrir o .txt gerado no navegador ao final
python demo.py --abrir
```

> O `.venv/` é ignorado pelo git. Se a ativação falhar por política de
> execução no PowerShell, rode uma vez
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` — ou chame o
> interpretador direto sem ativar: `.\.venv\Scripts\python.exe demo.py`.

Também é possível rodar cada etapa isoladamente:

```bash
python src/baixar_focus.py                    # baixa o PDF mais recente
python src/extrair_texto.py                   # extrai o texto do PDF mais recente
python src/extrair_texto.py --pdf caminho.pdf # extrai de um PDF específico
```

## Como rodar os testes

```bash
# Testes offline (rápidos, sem rede)
pytest -m "not network"

# Apenas os testes de rede (fazem download real do BCB)
pytest -m network

# Todos
pytest
```

## Tratamento de feriados

Quando a segunda-feira é feriado, o BCB publica o Focus na terça (ou próximo
dia útil). O download parte da última segunda e **recua um dia por vez** até
encontrar o PDF, cobrindo esses casos automaticamente.
