# Modelos, regras e limites

| Entrada | Modelo ou método | Parâmetros demonstrativos | Situação |
|---|---|---|---|
| Vídeo | YOLOv8n Pose e ByteTrack | Ombros/quadris com confiança ≥0,5, tronco >40°, persistência ≥2 s | Código e teste simulado |
| Áudio | Energia RMS e contagem de janelas silenciosas | Janela 30 ms, RMS <0,015, alerta se razão >0,55 | WAV sintético executado |
| Fala | Azure Speech contínuo pt-BR | Espera até 600 s | Conector e teste simulado |
| Texto | Léxico local e negação nas quatro palavras anteriores | Falta de ar, dor no peito, desmaio e dificuldade para respirar | Regras testadas |
| Contexto textual | Azure AI Language | Sentimento e frases-chave, texto até 5000 caracteres neste conector | Conector e teste simulado |
| Sinais vitais | Limiares e escore com mediana/MAD | Mínimo 8, janela 30, escore ≥4 | Fixtures executadas |
| Prescrição | Razão entre doses diárias anteriores/atuais | Razão ≥2 ou ≤0,5; unidade diferente gera revisão própria | Fixtures executadas |
| Movimentação | Imobilidade recebida de produtor externo | Duração ≥1800 s | Regra executada |
| Fusão | Correlação tardia determinística | Duas modalidades com achados em 300 s | Fixtures executadas |

Nenhum modelo foi treinado ou ajustado com dados clínicos neste projeto. Não há LLM, RAG ou fine-tuning incorporado ao código da Fase 4. A continuidade com os exemplos MedAssist da Fase 3 é temática.

Sentimento não aumenta a gravidade. Silêncio não diagnostica fadiga/disartria; inclinação não comprova falha terapêutica. Use um paciente visível por vídeo: o ID do rastreador não identifica uma pessoa clinicamente, e todos os rastros recebem o paciente informado no comando.

Os parâmetros são escolhas de demonstração e não recomendações clínicas. Não existe probabilidade de risco estimada. Um salto pode acionar regras diferentes e novas fusões podem repetir evidências do mesmo episódio.

## Dependências e referências

As faixas estão no `pyproject.toml`. O núcleo usa somente biblioteca padrão. Os extras Azure/vídeo não têm lockfile validado nesta entrega. Para uma execução real, registre `python -m pip freeze`, hash dos pesos, configuração, região e características da mídia.

- [Ultralytics Pose](https://docs.ultralytics.com/tasks/pose/)
- [Ultralytics Tracking](https://docs.ultralytics.com/modes/track/)
- [Azure SpeechRecognizer](https://learn.microsoft.com/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.speechrecognizer)
- [Azure Text Analytics](https://learn.microsoft.com/python/api/overview/azure/ai-textanalytics-readme)

O código seleciona explicitamente `yolov8n-pose.pt` e `bytetrack.yaml`, mesmo que a documentação corrente exemplifique modelos posteriores.
