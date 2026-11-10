# Requisitos e evidências da entrega

| Requisito documental do Git | Onde encontrar |
|---|---|
| Código-fonte completo do protótipo | `sentinela/`, `config.json`, `pyproject.toml` e `tests/` |
| Descrição do fluxo multimodal | `ARQUITETURA.md` e capítulos 3 e 7 do relatório final |
| Modelos por tipo de dado | `MODELOS_E_LIMITES.md` e capítulos 4 a 7 do relatório |
| Resultados e anomalias detectadas | `evidencias/`, capítulo 9 do relatório e slides 12/13 |

## Resultados históricos reproduzíveis

20 eventos sintéticos, 13 alertas e nenhuma rejeição. Distribuição: 4 por sinais vitais, 3 por áudio/texto com fusão, 2 por postura com fusão, 2 por prescrição com fusão e 2 por imobilidade com fusão. Os 13 códigos incluem 4 alertas de fusão, não 13 episódios clínicos independentes.

`summary.json` contém os totais; `alerts.json`, as evidências; `metrics.json`, os códigos esperados e previstos. Os fixtures ficam em `evidencias/fixtures/`. O F1 de 1,0 só caracteriza esses casos determinísticos e não estima acurácia clínica.

O WAV contém tom/silêncio e o TXT é fornecido separadamente. A observação de vídeo é sintética. A suíte original tem 17 testes; a revisão de empacotamento inclui testes adicionais e seu registro está em `evidencias/VERIFICACAO_REPOSITORIO.md`.

## Pendências que a documentação não substitui

- Executar Azure Speech/Language reais com mídia autorizada.
- Executar YOLO real e verificar os instantes no vídeo original.
- Obter anotações independentes e avaliar pacientes/sessões separados.
- Publicação e primeira matriz de CI concluídas em 10/11/2026. Ver `evidencias/VERIFICACAO_CI.md` para o registro.
- Gravar/publicar o vídeo exigido pela avaliação e adicionar seu link.

Esses itens não são marcados como concluídos sem evidência. O relatório acadêmico descreve a versão funcional 1.0.0; o pacote 1.0.1 mantém as regras e acrescenta organização, portabilidade e documentação.
