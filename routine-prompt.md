Você está executando a Routine de resumo semanal do Focus.

O download do PDF e a extração do texto já foram feitos por um GitHub
Action mais cedo (segunda 9h15 BRT). Os arquivos
`data/focus_AAAA-MM-DD.{pdf,txt}` já estão commitados em `main` quando
a Routine inicia. Sua tarefa é ler o `.txt` mais recente, gerar um
resumo em HTML e publicá-lo (commit + push em `main`) — é esse push que
dispara o Action de envio por e-mail.

## Passos

1. **Localize o `.txt` mais recente.** Liste `data/focus_*.txt` e pegue
   o de data mais alta. Se não houver nenhum, pare sem commitar o HTML — o
   Action não rodou.

2. **Verifique frescor.** Extraia a data do nome e compare com hoje:
   - 0 a 3 dias: está fresco, siga.
   - 4 a 7 dias: siga, mas escreva `[REVISAR]` no início do assunto.
   - Mais de 7 dias: pare sem commitar o HTML.

3. **Sanity check do texto.** Confirme: pelo menos 2 000 caracteres e
   presença das palavras `IPCA`, `Selic`, `PIB`. Se falhar, o layout do
   PDF pode ter mudado — pare sem commitar o HTML.

4. **Leia o texto** e escreva o conteúdo do resumo:
   - **Resumo executivo** em até 200 palavras, em prosa corrida.
     Comece pelas medianas das principais variáveis (IPCA do ano,
     Selic fim de ano, PIB, câmbio). Cite literalmente entre aspas
     quando houver número-chave.
   - **Três principais revisões da semana** em bullets no formato:
     `Variável (ano): anterior → atual. Hipótese: motivo.`
   - Nunca invente número. Se não houver hipótese sólida, escreva
     "sem hipótese clara — pode ser ruído amostral".

5. **Monte o HTML** do e-mail em `output/focus/focus_AAAA-MM-DD.html`, com
   esta estrutura:
   - Um título `Focus — AAAA-MM-DD`.
   - O resumo executivo em parágrafo e as três revisões em lista.
   - Use as cores da marca: azul `#282f6b` nos títulos.

6. **Inspecione** o HTML gerado: as medianas batem com o `.txt`, há ao
   menos uma citação literal entre aspas.

7. **Publique o HTML.** Faça o commit e o push do arquivo para `main`:

   ```bash
   git add output/focus/focus_AAAA-MM-DD.html
   git commit -m "Resumo Focus AAAA-MM-DD"
   git push origin main
   ```

   É esse push que **dispara o Action de envio** (`.github/workflows/focus-enviar.yml`),
   que monta e envia o e-mail a partir do HTML publicado.

   O destinatário, o remetente e a senha de app **ficam nos Secrets do
   repositório** (ex.: `FOCUS_EMAIL_DEST`, `FOCUS_SMTP_USER`,
   `FOCUS_SMTP_APP_PASSWORD`) — **nunca** no arquivo HTML nem neste prompt.
   Não escreva credenciais nem endereço de destino no conteúdo commitado.

## Falhas

Em qualquer cenário abaixo, pare sem commitar o HTML (assim nada é
enviado). O motivo aparece no transcript da Routine.

- Nenhum `.txt` em `data/` (Action não rodou).
- `.txt` com mais de 7 dias (Action quebrado).
- Sanity check do texto falhou (mudança de layout do PDF).

Nunca invente número.
