"""Envio do resumo HTML do Focus por e-mail via SMTP do Gmail.

As credenciais NUNCA ficam no código: são lidas de variáveis de ambiente.
  - FOCUS_SMTP_USER          remetente (e-mail Gmail)
  - FOCUS_SMTP_APP_PASSWORD  senha de app do Gmail (não a senha normal)
  - FOCUS_EMAIL_DEST         destinatários separados por vírgula
  - FOCUS_EMAIL_BCC          (opcional) cópias ocultas separadas por vírgula
"""

import argparse
import html
import os
import pathlib
import re
import smtplib
import ssl
import sys
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL


def html_mais_recente(pasta: str | pathlib.Path) -> pathlib.Path | None:
    """Retorna o focus_*.html mais recente da pasta, ou None se não houver."""
    pasta = pathlib.Path(pasta)
    htmls = sorted(pasta.glob("focus_*.html"))
    return htmls[-1] if htmls else None


def data_do_nome(caminho: pathlib.Path) -> str | None:
    """Extrai a data AAAA-MM-DD do nome focus_AAAA-MM-DD.html, ou None."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", caminho.name)
    return m.group(1) if m else None


def _html_para_texto(conteudo_html: str) -> str:
    """Fallback texto simples: remove tags e decodifica entidades HTML."""
    sem_tags = re.sub(r"<[^>]+>", "", conteudo_html)
    # Decodifica entidades (&ldquo; &rarr; etc.) para caracteres reais
    decodificado = html.unescape(sem_tags)
    # Colapsa linhas em branco excessivas
    return re.sub(r"\n\s*\n+", "\n\n", decodificado).strip()


def montar_email(
    html: str,
    assunto: str,
    remetente: str,
    destinatarios: list[str],
    bcc: list[str] | None = None,
) -> EmailMessage:
    """Monta a mensagem multipart (texto + HTML) pronta para envio."""
    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)
    if bcc:
        msg["Bcc"] = ", ".join(bcc)

    # Corpo em texto (fallback) e a versão HTML como alternativa
    msg.set_content(_html_para_texto(html))
    msg.add_alternative(html, subtype="html")
    return msg


def _lista_de_env(valor: str | None) -> list[str]:
    """Converte 'a@x.com, b@y.com' em ['a@x.com', 'b@y.com']."""
    if not valor:
        return []
    return [item.strip() for item in valor.split(",") if item.strip()]


def enviar(
    caminho_html: str | pathlib.Path,
    assunto: str | None = None,
    dest: list[str] | None = None,
) -> None:
    """Lê o HTML, monta o e-mail e envia via SMTP SSL do Gmail.

    Credenciais e destinatários vêm do ambiente, salvo se `dest` for passado.
    Levanta RuntimeError se faltar credencial ou destinatário.
    """
    caminho_html = pathlib.Path(caminho_html)
    html = caminho_html.read_text(encoding="utf-8")

    # Assunto padrão derivado da data no nome do arquivo
    if assunto is None:
        data = data_do_nome(caminho_html) or "?"
        assunto = f"Resumo Focus — {data}"

    remetente = os.environ.get("FOCUS_SMTP_USER")
    senha = os.environ.get("FOCUS_SMTP_APP_PASSWORD")
    destinatarios = dest or _lista_de_env(os.environ.get("FOCUS_EMAIL_DEST"))
    bcc = _lista_de_env(os.environ.get("FOCUS_EMAIL_BCC"))

    # Validações — falha clara antes de tentar conectar
    if not remetente or not senha:
        raise RuntimeError(
            "Credenciais ausentes: defina FOCUS_SMTP_USER e "
            "FOCUS_SMTP_APP_PASSWORD no ambiente."
        )
    if not destinatarios:
        raise RuntimeError(
            "Sem destinatários: defina FOCUS_EMAIL_DEST ou use --dest."
        )

    msg = montar_email(html, assunto, remetente, destinatarios, bcc)

    # Conexão SSL na porta 465
    contexto = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=contexto) as servidor:
        servidor.login(remetente, senha)
        servidor.send_message(msg)

    print(f"E-mail enviado: '{assunto}' para {', '.join(destinatarios)}")


def main() -> int:
    """CLI: envia o resumo mais recente ou o indicado; --dry-run não envia."""
    parser = argparse.ArgumentParser(
        description="Envia o resumo HTML do Focus por e-mail (Gmail SMTP)."
    )
    parser.add_argument(
        "--html",
        help="Caminho do HTML. Se omitido, usa o mais recente de output/focus/.",
    )
    parser.add_argument(
        "--dest",
        help="Destinatários separados por vírgula (sobrepõe FOCUS_EMAIL_DEST).",
    )
    parser.add_argument("--assunto", help="Assunto do e-mail (sobrepõe o padrão).")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Monta e mostra o e-mail SEM enviar e sem exigir credenciais.",
    )
    args = parser.parse_args()

    # Resolve o HTML: --html ou o mais recente de output/focus/
    if args.html:
        caminho_html = pathlib.Path(args.html)
    else:
        pasta = pathlib.Path(__file__).parent.parent / "output" / "focus"
        caminho_html = html_mais_recente(pasta)
        if caminho_html is None:
            print(
                "Erro: nenhum focus_*.html em output/focus/.\n"
                "Gere o resumo antes (Routine) ou passe --html.",
                file=sys.stderr,
            )
            return 1

    dest = _lista_de_env(args.dest) if args.dest else None

    if args.dry_run:
        # Modo teste: monta e mostra, sem credenciais e sem enviar
        html = caminho_html.read_text(encoding="utf-8")
        assunto = args.assunto or f"Resumo Focus — {data_do_nome(caminho_html) or '?'}"
        destinatarios = dest or _lista_de_env(os.environ.get("FOCUS_EMAIL_DEST")) or ["(defina FOCUS_EMAIL_DEST)"]
        print("=== DRY-RUN (nada foi enviado) ===")
        print(f"Arquivo:      {caminho_html}")
        print(f"Assunto:      {assunto}")
        print(f"Destino:      {', '.join(destinatarios)}")
        print(f"Tamanho HTML: {len(html)} caracteres")
        print("--- prévia do texto (fallback) ---")
        preview = _html_para_texto(html)
        print(preview[:500] + ("..." if len(preview) > 500 else ""))
        return 0

    try:
        enviar(caminho_html, assunto=args.assunto, dest=dest)
    except RuntimeError as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
