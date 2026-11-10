# Sentinela Multimodal — Fase 4

Protótipo acadêmico em Python para processar sinais vitais, prescrições, movimentação, áudio, texto e vídeo. Gera alertas explicáveis, cruza achados por paciente em janela de cinco minutos e permite confirmação pela equipe via CLI e SQLite.

## Entrega e documentos

Versão de manutenção do repositório: **1.0.1**. As regras e os resultados da versão 1.0.0 permanecem os mesmos. Veja [CHANGELOG](CHANGELOG.md).

- [Relatório técnico final em PDF](docs/Relatorio_Tecnico_Sentinela_Fase4.pdf) e [fonte em Markdown](docs/Relatorio_Tecnico_Sentinela_Fase4.md).
- [Apresentação PowerPoint](docs/Apresentacao_Sentinela_Fase4.pptx) e [apresentação em PDF](docs/Apresentacao_Sentinela_Fase4.pdf).
- [Roteiro de até 10 minutos](docs/Roteiro_10_Minutos_Sentinela_Fase4.pdf), que substitui os tempos mais longos das notas originais dos slides.
- [Guia completo de execução no VS Code](docs/GUIA_COMPLETO_SENTINELA.pdf).
- [Arquitetura e fluxo multimodal](docs/ARQUITETURA.md).
- [Modelos, parâmetros e limites](docs/MODELOS_E_LIMITES.md).
- [Matriz de requisitos e evidências](docs/REQUISITOS_E_EVIDENCIAS.md).
- [Contrato de eventos](docs/CONTRATO_DE_DADOS.md) e [schema JSON](schemas/event.schema.json).
- [Como publicar este repositório](docs/PUBLICACAO.md).
- [Validação real de Azure e YOLO](docs/VALIDACAO_EXTERNA.md).

O código-fonte está em `sentinela/`; os testes em `tests/`; os dados de demonstração e resultados em `evidencias/`. Todos os dados fornecidos são sintéticos. Não há repositório remoto ou vídeo publicado automaticamente.

## Execução local

Requer Python 3.11+. Abra o terminal nesta pasta:

```powershell
python -m sentinela demo
python -m unittest discover -s tests -v
```

Para instalar o núcleo e verificar também o pacote instalado:

```powershell
python -m pip install .
python scripts/verificar_entrega.py
```

Em uma instalação fora da pasta do repositório, a CLI usa a configuração padrão incluída no pacote. Na raiz, `config.json` local tem precedência. `--config` explícito prevalece sobre ambos e deve vir antes do subcomando. A pasta de resultados é relativa ao diretório atual do terminal.

Para depuração no VS Code, selecione seu interpretador em **Python: Select Interpreter**, escolha **Sentinela: demonstração guiada** e pressione F5. A configuração `.vscode/launch.json` usa o interpretador selecionado, sem caminhos de outro computador.

O workflow `.github/workflows/ci.yml` prevê testes em Python 3.11/3.12 no Windows e Linux após a publicação. A execução dessa matriz no GitHub ainda não foi verificada; os testes locais estão descritos em `evidencias/VERIFICACAO_REPOSITORIO.md`.

A demonstração não requer pacotes externos. Gera 20 eventos sintéticos e 13 alertas em `resultados/demo`. As evidências da verificação realizada estão em `evidencias/`.

## Monitoramento e confirmação

```powershell
python -m sentinela run evidencias/fixtures/events.jsonl --out resultados/monitor --interval 0.2
python -m sentinela alerts --db resultados/monitor/monitor.db
python -m sentinela ack ID_DO_ALERTA --db resultados/monitor/monitor.db
```

`--follow` acompanha novas linhas completas em JSONL a cada 250 ms; Ctrl+C encerra. O arquivo não deve ser rotacionado ou truncado durante a execução. Eventos precisam ter IDs globalmente únicos e imutáveis e timestamps com fuso, ordenados por paciente. Repetições são ignoradas; entradas inválidas são rejeitadas sem impedir a leitura das seguintes. O processo retorna código 1 se houver rejeições. Execute apenas um consumidor por banco. O estado é reconstituído do SQLite após reinício.

Os alertas saem no console e ficam no banco. `alerts` lê o estado atual; os relatórios exportados são fotografias da última execução e não são atualizados automaticamente por `ack`. Não há envio de email, SMS ou mensagens externas.

## Áudio local

```powershell
python -m sentinela audio evidencias/fixtures/audio-sintetico.wav --transcript evidencias/fixtures/transcricao.txt --patient PAC-DEMO --timestamp 2026-01-01T12:02:05Z --id audio-demo --out resultados/audio.jsonl
python -m sentinela run resultados/audio.jsonl --out resultados/audio-monitor
```

A fixture WAV contém tom e silêncio; a transcrição é fornecida separadamente, não reconhecida do tom. O extrator aceita WAV PCM mono de 16 bits e calcula energia e pausas. Pausas não constituem diagnóstico de fadiga ou dificuldade respiratória.

## Azure e vídeo opcionais

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[azure,video]"
```

Configure as variáveis de `.env.example` no ambiente; o arquivo não é carregado automaticamente. Para Azure, são necessários recursos Speech e Language e suas respectivas chaves/endpoint:

```powershell
python -m sentinela audio dados-reais/consulta.wav --azure --patient PAC-DEMO --timestamp 2026-01-01T12:00:00Z --id consulta-001 --out resultados/consulta.jsonl
python -m sentinela video dados-reais/fisioterapia.mp4 --patient PAC-DEMO --timestamp 2026-01-01T12:00:00Z --id fisio-001 --out resultados/video.jsonl
```

Azure Speech usa reconhecimento contínuo pt-BR. Language retorna sentimento e frases-chave, com limite local de 5000 caracteres por chamada. Textos maiores devem ser segmentados. O sentimento não altera gravidade clínica. Falhas não são substituídas por resultados fictícios.

Vídeo usa YOLOv8n Pose e ByteTrack: inclinação do tronco superior a 40 graus persistente por 2 segundos, confiança dos ombros/quadris de pelo menos 0,5. Use câmera frontal fixa e somente o paciente de interesse; todos os rastros são associados ao paciente informado. IDs de rastreamento não identificam pessoas clinicamente. O relatório `video.jsonl.report.json` registra instantes e evidências. Pesos podem ser baixados na primeira execução e o rastreador pode exigir dependência adicional. Não há avaliação de falhas cirúrgicas.

Áudio e vídeo são processados em lote. Seus eventos podem ser combinados e ordenados com os demais antes de `run`. O monitor é incremental, mas não captura câmera ou microfone ao vivo.

## Contrato JSONL

```json
{"id":"vital-001","patient_id":"PAC-DEMO","timestamp":"2026-01-01T12:00:00Z","modality":"vitals","data":{"heart_rate":145,"spo2":88,"systolic_bp":120}}
```

| Modalidade | Conteúdo de `data` |
|---|---|
| vitals | heart_rate (bpm), spo2 (%), systolic_bp (mmHg), todos numéricos |
| prescription | drug e unit como texto; daily_dose numérica positiva, dose diária total |
| movement | immobility_seconds numérico não negativo, recebido de sensor externo |
| text | text não vazio |
| audio | transcript não vazio, acoustic.silence_ratio entre 0 e 1 |
| video | posture_deviation booleano e evidências opcionais |

O programa não converte unidades. `config.json` contém parâmetros demonstrativos, sem validação clínica. O histórico guarda até 30 amostras normais e exige 8 antes de calcular desvio robusto. A detecção absoluta funciona desde a primeira amostra.

## Situação da entrega

Núcleo e áudio local foram executados. Conectores Azure e contrato do vídeo têm testes simulados; serviços reais, pesos YOLO e vídeos clínicos não foram executados neste ambiente. Não há credenciais ou dados clínicos fornecidos. O relatório técnico e o roteiro estão em `docs/`.

Ainda são necessários: validação com serviços Azure e mídia real autorizada; publicação do repositório na conta da equipe; gravação e publicação da apresentação. Este protótipo não tem autenticação, criptografia de banco ou auditoria profissional e não deve ser usado como sistema assistencial.
