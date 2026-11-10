# Verificação do projeto — 20/10/2026

**Resultado: fluxo local aprovado nos cenários executados; integrações reais pendentes.**

- 17 testes automatizados passaram. Registro: `testes.txt`.
- Demonstração: 20 eventos armazenados, 13 alertas, zero rejeitados.
- CLI de áudio: WAV sintético analisado, transcrição fornecida e dois alertas gerados.
- Reexecução no mesmo banco sem duplicar alertas.
- Confirmação de alerta persistida e consultada em outro processo.
- `--follow` aguardou a quebra de linha antes de processar um registro parcial e emitiu alerta quando ele foi completado.
- Arquivo inexistente retornou código 1 e mensagem de erro sem traceback.

## Correção aplicada

Algumas entradas malformadas poderiam gerar erro não tratado, como texto nulo, `acoustic` nulo ou nome de medicamento numérico. Foi adicionada validação antes da análise. Também são rejeitados booleanos em campos numéricos, razões de silêncio fora de 0–1 e marcadores posturais que não sejam booleanos. O teste de integração confirma que um evento inválido não impede o processamento do seguinte.

## Limites da verificação

Azure Speech, Azure Language e o extrator de vídeo passaram por testes com objetos simulados. Não houve chamada real ao Azure ou inferência real do YOLO. Este runtime não possui torch, opencv ou ultralytics. Não foram fornecidas credenciais nem mídia clínica. Portanto, não é possível afirmar que o sistema inteiro esteja validado ponta a ponta ou clinicamente.

Os arquivos `verificacao-cli.json`, `summary.json`, `metrics.json`, `alerts.json` e `report.md` contêm os resultados locais. As métricas dos fixtures sintéticos verificam regressão, não desempenho clínico.
