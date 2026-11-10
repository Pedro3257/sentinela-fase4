# Notas para apresentação oral

## Slide 1

Abertura sugerida: 30 segundos. O Sentinela é o pacote desenvolvido nesta conversa para a Fase 4. A continuidade com MedAssist é temática. Não há integração demonstrada com RAG ou LangGraph. A imagem de capa foi extraída de MedAssit_Demo.pdf, referência fornecida pelo solicitante. Sem uso como evidência clínica.

## Slide 2

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Duração sugerida: 40 s. Explicar que risco clínico é uma hipótese de aplicação. A avaliação desta entrega verifica integração funcional. O sistema não reutiliza o código de RAG da Fase 3.

## Slide 3

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Duração: 55 s. O contrato separa os extratores do motor. Áudio e vídeo são em lote, monitor acompanha JSONL incremental. Não há API HTTP ou dashboard.

## Slide 4

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Duração: 45 s. O evento JSON é exibido formatado, mas o arquivo JSONL contém um objeto por linha. Eventos precisam chegar em ordem por paciente. ID repetido é ignorado, inclusive se o conteúdo mudou.

## Slide 5

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Referência: NIST, Median Absolute Deviation, https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/mad.htm. Duração: 55 s. Limites são escolhas demonstrativas. Histórico de até 30 medidas normais, início após oito. Valores anômalos não atualizam a baseline. Um valor pode acionar dois códigos.

## Slide 6

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Duração: 50 s. A fixture tem tom e silêncio, não fala. Texto é fornecido separadamente. RMS não identifica paciente ou locutor. Não há diagnóstico de fadiga ou disartria. Negação considera as quatro palavras anteriores e tem cobertura limitada.

## Slide 7

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Referências: https://learn.microsoft.com/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.speechrecognizer e https://learn.microsoft.com/python/api/overview/azure/ai-textanalytics-readme. Duração: 45 s. SDKs simulados em testes. Nenhuma chamada real foi registrada. Sentimento não aumenta gravidade. .env.example não é carregado automaticamente.

## Slide 8

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Referências: https://docs.ultralytics.com/tasks/pose/ e https://docs.ultralytics.com/modes/track/. Duração: 55 s. O código usa explicitamente yolov8n-pose.pt e bytetrack.yaml. Não foi executado YOLO real nesta entrega. O ângulo é bidimensional e pode fazer parte de um exercício correto. Todos os rastros recebem o patient_id informado.

## Slide 9

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Duração: 40 s. Não há análise de interações medicamentosas nem conversão automática de unidades. A duração da imobilidade vem de produtor externo, não de um sensor implementado. Mudança de dose pode ser clinicamente correta.

## Slide 10

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Referência conceitual: Baltrusaitis et al., https://arxiv.org/abs/1705.09406. Duração: 55 s. Fusão tardia determinística sobre achados. Não é rede multimodal treinada nem probabilidade de risco. Modalidades correlacionadas e códigos repetidos não são observações independentes.

## Slide 11

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Duração: 40 s. ID estável deriva de SHA-256 truncado do ID do evento e do código da regra. Isso não é assinatura criptográfica. Confirmar um alerta não retira suas evidências da janela. Não há identidade do profissional nem notificação externa.

## Slide 12

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Duração: 55 s. Dados em summary.json e fixtures/events.jsonl. Contagem por cenário: vitais 4, áudio/texto 3, vídeo 2, prescrição 2, movimento 2. Total de 9 achados simples e 4 alertas de fusão. A observação de vídeo é fixture. A razão de silêncio do evento é 0,7, enquanto o WAV analisado produz 0,7491.

## Slide 13

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Duração: 55 s. Métricas por par evento/código. TP=13, FP=0, FN=0. Os rótulos expected_codes são construídos junto às regras e não representam anotação clínica independente. Não há especificidade clínica, curva ROC ou validação externa. A suíte foi novamente executada em 03/11/2026, com 17 testes aprovados.

## Slide 14

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Duração: 50 s. Diferenciar validade interna, de construto e externa. O monitor não trata perda de sensor como condição própria. O polling de 250 ms não é latência fim a fim. A quantidade de alertas pode aumentar por repetições de fusão sem cooldown.

## Slide 15

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Duração: 45 s. Plano proposto, não executado. Separação por paciente/sessão evita vazamento entre frames. Critérios de aceitação precisam de profissionais. Não definir amostra arbitrária nem prometer benefício sem estudo.

## Slide 16

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Duração: 60 s, ou reservar este slide para execução ao vivo. Rodar a partir da raiz. Se houver ambiente virtual sem ativação, usar seu python.exe. A apresentação completa com falas foi planejada para aproximadamente 13 a 15 minutos, incluindo demonstração curta.

## Slide 17

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Duração: 40 s. Evitar chamar a solução de pronta para produção. Evidenciar a contribuição de engenharia e as condições para evoluir. O Git remoto e o vídeo publicado não foram comprovados nesta entrega.

## Slide 18

Fonte primária: código sentinela-multimodal 1.0.0, config.json e evidencias/. Apêndice para consulta. Referências completas e discussão no relatório técnico. Fonte da imagem de capa: MedAssit_Demo.pdf fornecido pelo solicitante. Nenhuma métrica da Fase 3 foi reutilizada.