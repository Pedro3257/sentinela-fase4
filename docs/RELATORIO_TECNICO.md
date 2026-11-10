# Relatório técnico — Sentinela Multimodal

## Escopo e arquitetura

Solução acadêmica da Fase 4 para monitoramento multimodal. O recorte do vídeo é fisioterapia frontal em câmera fixa; não há avaliação de falhas cirúrgicas. O fluxo é:

```text
WAV -> Azure Speech + características acústicas -> Azure Language
Vídeo -> YOLOv8 Pose + ByteTrack -> observações posturais
Sinais vitais / prescrições / sensor de movimento -> eventos normalizados
Todos -> JSONL por paciente e instante -> regras -> fusão temporal
      -> alertas no console + SQLite -> revisão e confirmação pela equipe
```

O consumidor pode acompanhar um arquivo em crescimento (`--follow`). Os extratores de áudio e vídeo são em lote; não há captura de mídia ao vivo nem garantia de latência hospitalar.

## Métodos aplicados

| Entrada | Método | Limitação principal |
|---|---|---|
| Vídeo | YOLOv8n Pose e ByteTrack; pontos médios de ombros/quadris, ângulo do tronco >40 graus por 2 s, confiança >=0,5 | Perspectiva, oclusão e exercício correto podem alterar a interpretação |
| Áudio | RMS em janelas de 30 ms, silêncio abaixo de 0,015, proporção de silêncio >0,55 | Pausas não classificam fadiga, disartria ou condição respiratória |
| Fala | Azure Speech, reconhecimento contínuo pt-BR | Requer credenciais, rede e áudio adequado |
| Texto | Azure Language para sentimento/frases-chave; termos críticos locais com negação simples | Negação complexa não é resolvida; sentimento não aumenta gravidade |
| Sinais vitais | Limites absolutos e desvio robusto contra baseline | Parâmetros demonstrativos, sem calibração clínica |
| Prescrição | Razão entre doses diárias >=2 ou <=0,5; revisão em mudança de unidade | Não converte unidades nem detecta interações medicamentosas |
| Movimentação | Duração de imobilidade >=1800 s | Duração vem de sensor externo, não é inferida do vídeo neste fluxo |

O escore robusto é `abs(x - mediana) / max(1,4826 * MAD, piso_da_escala)`. Usa até 30 medidas normais anteriores e exige 8 para iniciar o escore. Valores anômalos não entram na baseline; esta pode se tornar desatualizada se o estado mudar permanentemente. Os limites absolutos atuam desde a primeira amostra.

A fusão tardia sinaliza achados de duas ou mais modalidades em 300 segundos para o mesmo paciente. Não estima probabilidade clínica, nem assume independência entre modalidades. Cada alerta inclui código, paciente, instante, ID do evento, evidências e estado de revisão.

Eventos e alertas são gravados por transação no SQLite. Após reinício, baseline e janela temporal são reconstituídos. IDs devem ser únicos e imutáveis. Entradas inválidas ou atrasadas por paciente são rejeitadas e listadas em `errors.json`. A confirmação `ack` persiste o estado `acknowledged`; não representa resolução clínica. O protótipo prevê um consumidor por banco.

## Resultados efetivamente obtidos

`python -m sentinela demo --out evidencias` processou 20 eventos sintéticos e gerou 13 alertas, sem rejeições:

| Cenário | Alertas |
|---|---:|
| FC 145 e SpO2 88 após baseline | 4 |
| Termos críticos e pausas de áudio, com fusão | 3 |
| Observação postural sintética e fusão | 2 |
| Dose de demonstração de 10 para 30 e fusão | 2 |
| Imobilidade de 2100 s e fusão | 2 |

Texto negado e sinais normais do segundo paciente não geraram alertas. A avaliação por evento/código apresenta precisão, recall e F1 de 1,0 apenas nos fixtures construídos a partir das regras. Isso é regressão determinística, não acurácia clínica ou validação dos modelos de mídia.

A fixture de vídeo já contém a observação postural. O WAV contém tom e silêncio, com transcrição fornecida separadamente. Não são apresentados como vídeo clínico inferido pelo YOLO ou fala transcrita pelo Azure.

A suíte verifica isolamento de pacientes, fusão/expiração, repetição de eventos, baseline, negação simples, validação de entrada, persistência e confirmação. Azure Speech/Language e vídeo têm testes de contrato com substitutos simulados. Veja `evidencias/testes.txt` e `evidencias/verificacao-cli.json` para a execução registrada.

## Avaliação real e etapas pendentes

Não foram fornecidos credenciais Azure, áudio de consulta nem vídeo clínico. As dependências de vídeo não estão instaladas no runtime usado. Portanto, Azure e inferência YOLO reais ainda precisam de validação ponta a ponta. Também faltam gravação/publicação da apresentação e publicação do repositório na conta da equipe.

Para avaliar generalização, obter sessões e consultas autorizadas, rotuladas por profissionais. Separar ajuste e teste por paciente/sessão. Medir precisão/recall por episódio, erro de transcrição, acerto de termos com negação, falsos alertas por paciente/hora e latência. Incluir oclusões, falhas de áudio, movimentos corretos e dados faltantes. PhysioNet e AudioSet são sugestões do enunciado, não datasets utilizados nesta entrega.

O armazenamento local está em claro, não há autenticação, auditoria por profissional, fila distribuída ou integração com prontuário. Não foi entregue infraestrutura de nuvem. Antes de uso assistencial seriam necessárias revisão institucional, proteção de dados e validação clínica. Os limiares são escolhas de demonstração e não protocolos médicos.

## Referências de implementação

- [SpeechRecognizer e reconhecimento contínuo](https://learn.microsoft.com/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.speechrecognizer)
- [SDK Azure AI Text Analytics](https://learn.microsoft.com/python/api/overview/azure/ai-textanalytics-readme)
- [Ultralytics Pose](https://docs.ultralytics.com/tasks/pose/)

As referências documentam interfaces de software, não fundamentam limiares clínicos.
