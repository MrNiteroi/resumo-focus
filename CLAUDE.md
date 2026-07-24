# Projeto Focus BCB - Briefing

## Objetivo
Automatizar o download semanal do boletim Focus do Banco Central, extrair o texto de seus PDFs e preparar um resumo executivo.

## Fonte de Dados
- **Página do Focus**: https://www.bcb.gov.br/publicacoes/focus
- **Padrão de URL do PDF**: `https://www.bcb.gov.br/content/focus/focus/R{AAAAMMDD}.pdf`
  - Onde `{AAAAMMDD}` é a data de publicação (ex: R20260623.pdf para 23/06/2026)

## Estrutura de Pastas

```
.
├── src/                        # Código-fonte do projeto
├── tests/                      # Testes unitários e integração
├── data/                       # PDFs e textos brutos baixados
├── output/
│   └── focus/                  # Resumos em markdown gerados
└── .github/
    └── workflows/              # Workflows de automação (GitHub Actions)
```

## Convenções de Nomenclatura
- **Arquivos**: `focus_AAAA-MM-DD.{ext}` (formato ISO para a data de publicação)
  - Exemplo: `focus_2026-06-23.pdf`, `focus_2026-06-23.txt`, `focus_2026-06-23.md`
- **Diretórios de dados**: PDFs e textos brutos são armazenados em `data/`
- **Diretórios de saída**: Resumos markdown são salvos em `output/focus/`

## Regras Importantes

### 1. Integridade de Dados
- **Nunca inventar números**: Toda mediana ou valor citado no resumo deve estar presente no texto original do PDF
- Sempre referenciar a fonte ao incluir números

### 2. Tratamento de Feriados
- Quando a segunda-feira é feriado, o BCB publica o Focus na **terça-feira**
- O script de download deve:
  - Tentar baixar a URL da data da segunda-feira
  - Se falhar (HTTP 404), retroceder um dia por vez (domingo, sábado, etc.)
  - Parar ao encontrar o PDF ou após N tentativas (máximo 7 dias atrás)

### 3. Fluxo de Processamento
1. Download do PDF
2. Extração de texto
3. Geração do resumo executivo (em desenvolvimento)
4. Armazenamento respeitando as convenções de nomenclatura

## Estrutura do Código
- **`src/`**: módulos para download, extração de texto, geração de resumos
- **`tests/`**: testes para validação de lógica
- **`.github/workflows/`**: automação semanal (GitHub Actions)
