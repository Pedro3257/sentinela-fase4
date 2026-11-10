# Sentinela Multimodal

## Relatório técnico e científico

Monitoramento de pacientes com processamento de áudio, vídeo e texto, detecção de anomalias e fusão temporal de evidências

Tech Challenge Fase 4 • Pós-graduação em Inteligência Artificial para Desenvolvedores

Versão analisada: sentinela-multimodal 1.0.0

Data de consolidação: 3 de novembro de 2026

Natureza da entrega: protótipo acadêmico com avaliação funcional sintética e conectores externos parcialmente validados.

\page

## Resumo

Este trabalho apresenta o Sentinela Multimodal, um protótipo de monitoramento hospitalar que integra eventos de sinais vitais, prescrições, movimentação, texto e observações extraídas de áudio e vídeo. A solução adota uma arquitetura modular em Python, com contrato de eventos JSONL, detecção explicável por regras e estatística robusta, correlação temporal por paciente e persistência em SQLite. O processamento de vídeo utiliza um conector para YOLOv8 Pose e ByteTrack, enquanto o áudio combina características acústicas locais com conectores Azure Speech e Azure AI Language. A escolha de fusão tardia permite inspecionar a origem de cada achado, ao custo de não aprender relações multimodais a partir dos dados. A demonstração determinística contém 20 eventos sintéticos, produz 13 alertas e apresenta concordância integral com os códigos esperados desse conjunto. A suíte automatizada, novamente executada na consolidação deste relatório, contém 17 testes aprovados. Esses resultados evidenciam consistência funcional, sem sustentar estimativas de sensibilidade clínica, benefício assistencial ou desempenho real dos modelos externos. O trabalho explicita limitações, ameaças à validade e um protocolo futuro de avaliação por paciente e sessão. A principal contribuição é um fluxo reproduzível de integração e rastreabilidade de alertas, acompanhado de uma separação verificável entre implementação, evidência experimental e validação ainda necessária.

**Palavras-chave:** monitoramento multimodal; detecção de anomalias; estatística robusta; processamento de fala; estimação de pose; fusão temporal; engenharia de software.

### Organização do relatório

1. Contexto, problema e objetivos
2. Fundamentação e decisões metodológicas
3. Arquitetura e contrato de dados
4. Sinais vitais e estatística robusta
5. Áudio, texto e serviços Azure
6. Vídeo e análise postural
7. Prescrições, movimentação e fusão
8. Persistência e resposta ao alerta
9. Método experimental e resultados
10. Discussão e ameaças à validade
11. Protocolo de validação e evolução
12. Reprodutibilidade e rastreabilidade
13. Conclusões
14. Referências e apêndice operacional

\page

## 1. Contexto, problema e objetivos

O enunciado da Fase 4 propõe ampliar o apoio informacional em saúde para um cenário de monitoramento preventivo, integrando modalidades que apresentam estruturas e frequências distintas. Sinais vitais descrevem medidas numéricas, prescrições registram mudanças de tratamento, a fala fornece conteúdo verbal e características acústicas, e o vídeo pode representar padrões de movimentação. O problema de engenharia consiste em converter essas entradas em observações comparáveis no tempo e atribuídas ao paciente correto, preservando a explicação dos alertas [1].

Os exemplos MedAssist da Fase 3 orientam o formato acadêmico desta documentação. Contudo, o código da Fase 4 analisado é o pacote Sentinela Multimodal, independente do pipeline de RAG e fine-tuning dos exemplos. Não há evidência de integração de código com LangGraph, PostgreSQL/pgvector ou modelos de linguagem da Fase 3. Assim, a continuidade entre fases é temática, e não uma alegação de reutilização técnica ou de desempenho.

### 1.1 Objetivo geral

Desenvolver e demonstrar um fluxo reproduzível de análise de eventos multimodais, detecção de desvios e registro de alertas rastreáveis, com etapa explícita de revisão humana.

### 1.2 Objetivos específicos e questão de pesquisa

Os objetivos específicos são estabelecer um contrato de integração por paciente e instante, implementar detectores interpretáveis, disponibilizar conectores de mídia e nuvem, correlacionar evidências em janela temporal e verificar propriedades funcionais por testes. A questão investigada é: como integrar achados heterogêneos em um fluxo local auditável, preservando a origem e os limites de interpretação de cada evidência?

A hipótese de engenharia é que um contrato comum e uma fusão determinística permitem verificar consistência, isolamento de pacientes e persistência da revisão em um ambiente controlado. A hipótese clínica de que a fusão antecipa deterioração ou reduz falsos alertas permanece não testada.

### 1.3 Delimitação

O recorte visual considera fisioterapia com câmera frontal fixa. O software não avalia falhas cirúrgicas, não recomenda doses e não diagnostica condições pela voz. A interface é uma CLI local. O monitor acompanha eventos incrementais, enquanto os extratores de áudio e vídeo operam em arquivos. A notificação demonstrativa é a emissão no console com registro no banco, sem canal externo de comunicação. Essas delimitações condicionam a leitura dos requisitos e dos resultados.

\page

## 2. Fundamentação e decisões metodológicas

A literatura de aprendizado multimodal destaca problemas de representação, alinhamento, fusão e aprendizado entre modalidades [2]. Neste trabalho, a integração ocorre depois da extração e da classificação de achados. Trata-se de fusão tardia por regras, aplicada a observações heterogêneas, e não de uma rede neural multimodal treinada de ponta a ponta. O alinhamento depende de identificadores de paciente e timestamps fornecidos corretamente pelos produtores.

### 2.1 Explicabilidade e custo de complexidade

Regras determinísticas oferecem uma relação direta entre entrada, parâmetro e alerta. Essa propriedade favorece demonstração, depuração e inspeção. Em contrapartida, limites fixos e janelas temporais exigem calibração e não capturam automaticamente relações não lineares ou contexto terapêutico. A explicação da regra esclarece o mecanismo do software, mas não prova que o achado seja clinicamente relevante.

Para séries temporais curtas, mediana e desvio absoluto mediano, ou MAD, oferecem uma referência de centro e escala menos influenciada por extremos do que medidas quadráticas [3]. O protótipo combina esse mecanismo com limites absolutos. A seleção dos limiares é demonstrativa. Não houve otimização em amostra clínica nem comparação experimental com Isolation Forest, autoencoders ou modelos supervisionados.

### 2.2 Método de desenvolvimento e evidência

O desenvolvimento organiza-se em especificação do evento, implementação dos módulos, geração determinística de fixtures, testes de propriedades funcionais e análise dos artefatos produzidos. Essa sequência descreve o método de engenharia observado; não implica adoção formal de um framework de pesquisa ou certificação de processo.

| Nível de evidência | O que foi verificado | O que não se pode concluir |
|---|---|---|
| Regra local executada | Saídas correspondem aos eventos de teste | Acurácia clínica em novos pacientes |
| Contrato externo simulado | Código interage com objetos e callbacks esperados | Compatibilidade completa com serviço/modelo real |
| Integração real | Ainda pendente para Azure e YOLO | Desempenho, custo e latência reais |
| Uso assistencial | Não realizado | Benefício, segurança ou efetividade clínica |

Essa classificação orienta o restante do documento. As referências técnicas dos SDKs sustentam o desenho dos conectores [4-7], mas não substituem execução real ou estudos com pacientes.

\page

## 3. Arquitetura e contrato de dados

O sistema separa adaptação das entradas, processamento dos eventos e persistência. O módulo media.py contém os extratores de WAV e vídeo e os conectores Azure. core.py concentra validação, histórico, regras e fusão. cli.py implementa os comandos, a ingestão incremental e a exportação de relatórios. demo.py produz fixtures reproduzíveis. Essa divisão permite testar o motor sem carregar bibliotecas de visão ou acionar serviços externos [8].

| Camada | Entrada | Saída e responsabilidade |
|---|---|---|
| Adaptadores de mídia | WAV ou vídeo | Características, transcrição ou achado postural |
| Contrato de integração | Objeto por linha JSONL | Paciente, instante e modalidade normalizados |
| Motor de detecção | Evento validado | Códigos de achados e evidências |
| Fusão temporal | Achados recentes do paciente | Alerta adicional com IDs correlacionados |
| Persistência e consumo | Evento e alertas | SQLite, console e relatórios exportados |

### 3.1 Modelo do evento

Um evento pode ser representado por e = (id, p, t, m, d), em que p identifica o paciente, t representa o instante, m a modalidade e d seu conteúdo. id deve ser globalmente único e imutável. O timestamp deve conter fuso horário. Cada linha JSONL contém um objeto completo em UTF-8, sem array externo. Os campos de identificação são strings não vazias e data é um objeto.

```json
{"id":"vital-001","patient_id":"PAC-SINT-001",
 "timestamp":"2026-01-01T12:02:00Z","modality":"vitals",
 "data":{"heart_rate":145,"spo2":88}}
```

O exemplo está quebrado visualmente para leitura; o arquivo JSONL exige esse objeto em uma única linha. A validação rejeita modalidades desconhecidas, dados malformados e valores não finitos nos campos analisados. Há verificação de monotonicidade temporal por paciente. Eventos atrasados não são reordenados pelo monitor: a preparação deve ocorrer antes da ingestão.

### 3.2 Fronteiras de responsabilidade

O produtor assegura unidade, identidade, origem e alinhamento temporal. O motor não converte unidades, não identifica pacientes no vídeo nem verifica a autenticidade da fonte. A associação errada de patient_id pode produzir uma fusão formalmente válida e clinicamente incorreta. Ausência de dados não equivale a normalidade e não gera, nesta versão, um alerta específico de perda de sensor.

\page

## 4. Detecção em sinais vitais

O motor suporta frequência cardíaca, saturação periférica de oxigênio e pressão arterial sistólica. Cada métrica passa por duas verificações: um intervalo absoluto e um desvio em relação ao histórico normal anterior do paciente. A avaliação relativa só começa após oito valores aceitos; o histórico retém no máximo trinta. Os parâmetros residem em config.json [8].

### 4.1 Formulação

Para um histórico H de n medidas, definem-se a mediana m e o MAD como a mediana das distâncias absolutas à mediana. O escore usa uma escala mínima específica da métrica:

```text
m = mediana(H)
MAD = mediana(|h - m|), para h em H
s = max(1,4826 x MAD, piso_da_metrica)
z_robusto = |x - m| / s
```

O fator 1,4826 é o ajuste convencional do MAD para uma escala comparável ao desvio padrão sob normalidade. Sua utilização não torna normal a distribuição observada nem transforma o escore em uma probabilidade clínica. O piso evita divisão por zero e sensibilidade excessiva em séries constantes. Um escore de pelo menos quatro gera um achado relativo.

| Métrica | Intervalo absoluto configurado | Piso da escala |
|---|---|---|
| Frequência cardíaca | 45 a 130 bpm | 3 bpm |
| SpO2 | 92 a 100% | 1 ponto percentual |
| Pressão sistólica | 90 a 180 mmHg | 5 mmHg |

Esses números descrevem a configuração do protótipo, sem constituir recomendação médica. Os extremos dos intervalos são aceitos pela regra absoluta. Um valor pode disparar simultaneamente a regra de limite e a regra relativa; o sistema preserva códigos diferentes para explicitar as duas razões.

### 4.2 Atualização e exemplo observado

Valores classificados como anormais não entram na baseline. Essa política evita contaminar a referência com um salto, mas pode congelar uma baseline desatualizada após mudança persistente de estado. Na demonstração, a mediana anterior de frequência cardíaca é 76 bpm. Uma medida de 145 bpm produz escore 23,0 com piso de 3 bpm e gera os dois códigos correspondentes. Essa aritmética é rastreável no alerta, sem provar deterioração real.

Não há tratamento de cadência irregular, interpolação, tempo máximo de validade do histórico ou ajuste por características do paciente. O histórico tem tamanho em amostras, não em minutos. Portanto, a mesma configuração pode representar horizontes temporais distintos em produtores com frequências diferentes.

\page

## 5. Áudio, texto e serviços Azure

O processamento acústico local aceita WAV PCM mono de 16 bits. O arquivo é dividido em janelas de aproximadamente 30 ms. Para cada janela, calcula-se a raiz da média dos quadrados da amplitude, normalizada por 32768. Uma energia inferior a 0,015 define a janela como silenciosa. O resultado inclui duração, energia média, razão de silêncio e maior sequência silenciosa [8].

```text
RMS_j = raiz(media(amplitude_i^2)) / 32768
razao_silencio = janelas_silenciosas / total_de_janelas
```

Razão de silêncio superior a 0,55 gera observação de pausas prolongadas. A duração da maior pausa é aproximada pela contagem de janelas, sujeita à discretização e à última janela parcial. O método não separa locutores, não mede articulação e não estima disartria. Entrevistas silenciosas, pausas do profissional e falhas do microfone são explicações alternativas para o mesmo resultado.

### 5.1 Transcrição e análise linguística

O conector Azure Speech configura pt-BR e usa reconhecimento contínuo com callbacks. Os segmentos reconhecidos são concatenados. A sessão termina por evento de conclusão ou cancelamento; a espera possui limite de 600 segundos. Cancelamentos com erro e ausência de fala não geram uma transcrição fictícia [4].

Azure AI Language retorna sentimento e frases-chave por chamadas analyze_sentiment e extract_key_phrases [5]. No código atual, o conector impõe limite de 5000 caracteres e rejeita transcrições maiores, sem segmentação interna. As credenciais são lidas de variáveis de ambiente separadas para Speech e Language. O arquivo .env.example não é carregado automaticamente.

### 5.2 Termos críticos e papel do sentimento

O léxico local procura falta de ar, dor no peito, desmaio e dificuldade para respirar. A normalização remove acentos e reduz diferenças de caixa. Uma heurística considera palavras como nega, não e sem nas quatro palavras anteriores dentro da oração. Essa regra cobre os exemplos de teste, mas não resolve escopo complexo de negação, hipótese, fala de terceiros ou histórico familiar.

O sentimento permanece como contexto no evento e não altera gravidade. A detecção dos termos críticos é local; não se atribui ao Azure uma inferência que o código não realiza. No modo local, a transcrição vem de um TXT fornecido, sem reconhecimento de voz. A fixture WAV contém tom e silêncio, portanto sua associação com uma frase é deliberadamente demonstrativa.

\page

## 6. Vídeo e análise postural

O extrator utiliza OpenCV para decodificar frames, YOLOv8n Pose para estimar pontos corporais e ByteTrack para manter rastros ao longo da sequência [6,7]. O modelo padrão é yolov8n-pose.pt. Não houve treinamento ou ajuste fino com vídeos da instituição, nem inferência real do modelo documentada nesta entrega.

### 6.1 Medida geométrica e persistência

O algoritmo usa os keypoints de ombros e quadris no esquema COCO. Exige confiança mínima de 0,5 nesses pontos, calcula o ponto médio dos ombros S e dos quadris Q e estima o ângulo do tronco em relação à vertical da imagem:

```text
S = (ombro_esquerdo + ombro_direito) / 2
Q = (quadril_esquerdo + quadril_direito) / 2
theta = atan2(|Sx - Qx|, |Sy - Qy|), em graus
duracao = frames_consecutivos / FPS
```

Ângulo superior a 40 graus por pelo menos dois segundos produz um achado. Há um registro por episódio contínuo. Voltar ao intervalo esperado permite novo episódio. Perda de confiança ou de visibilidade interrompe a persistência. O timestamp do achado corresponde ao instante em que a persistência é satisfeita, acrescido ao início informado da gravação.

### 6.2 Interpretação e validade

O ângulo é uma característica bidimensional da imagem. Rotação da câmera, oclusão, postura prevista no exercício e perspectiva podem modificar seu significado. A regra demonstra detecção de uma condição geométrica, sem comprovar execução inadequada do procedimento. O sistema não mede qualidade da fisioterapia nem verifica protocolo prescrito.

O rastreador diferencia rastros, mas não reconhece identidades clínicas. Todos os achados da sessão recebem o patient_id passado no comando. A presença de acompanhante ou profissional pode associar um movimento de terceiro ao paciente. O uso demonstrativo pressupõe um único paciente de interesse visível e câmera frontal fixa.

O relatório de vídeo preserva FPS, número de frames, duração e achados com deslocamento temporal, ângulo, duração e ID de trilha. Não há vídeo anotado exportado. Decodificação parcial do arquivo também exige investigação, pois fim de leitura e falha de decodificação podem ser indistinguíveis no laço atual. A validade real requer vídeos anotados e inspeção dos instantes detectados.

\page

## 7. Prescrições, movimentação e fusão temporal

### 7.1 Alterações em prescrições

O sistema mantém, por paciente e nome de medicamento normalizado apenas quanto à caixa, a dose diária anterior e a unidade. Para unidades idênticas, calcula r = dose_atual / dose_anterior. Razão de pelo menos dois ou de no máximo 0,5 gera um alerta. Se a unidade muda, registra uma observação específica sem comparar numericamente quantidades potencialmente incompatíveis.

O mecanismo não interpreta dose por tomada, frequência, equivalência entre medicamentos, indicação ou interação. Uma alteração pode ser correta e planejada. A ausência de contexto clínico exige revisão humana. A grafia inconsistente do medicamento pode iniciar uma série nova e impedir comparação.

### 7.2 Movimentação

Eventos de movement recebem immobility_seconds já calculado por um produtor externo. Duração maior ou igual a 1800 segundos gera um achado. O projeto não entrega um sensor físico nem calcula toda a imobilidade de internação a partir do vídeo. Esse limite de integração deve permanecer explícito na demonstração.

### 7.3 Definição da fusão

Para paciente p e instante t, o motor mantém somente eventos com achados na janela de 300 segundos anterior. O conjunto de modalidades ativas é:

```text
M_p(t) = {modalidade(e): paciente(e)=p,
          e tem achado e 0 <= t - tempo(e) <= 300 s}
```

Um novo evento com achado gera fusion:concurrent_evidence se o conjunto contém pelo menos duas modalidades. A evidência do alerta inclui as modalidades e os IDs dos eventos. A revisão de um alerta anterior não o retira retroativamente da janela do motor.

A regra é uma correlação temporal, sem estimativa probabilística ou ponderação de qualidade. Áudio e texto podem derivar da mesma fala. Prescrição e movimentação são tratadas como modalidades de evento, embora a literatura use definições mais estritas de modalidade sensorial. Eventos sucessivos podem gerar alertas de fusão repetidos para a mesma situação; não há cooldown ou agrupamento de incidentes. Essa escolha facilita rastreabilidade no protótipo, mas pode aumentar o volume de alertas.

\page

## 8. Persistência e resposta ao alerta

O banco SQLite contém tabelas events e alerts. Cada uma usa id como chave primária e armazena um payload JSON; alerts mantém também o status operacional em coluna separada. O sistema grava evento e alertas em uma transação por evento. Consultas usam parâmetros, evitando composição de SQL com os dados recebidos [8,9].

### 8.1 Identidade e reexecução

O ID do alerta deriva dos primeiros 24 caracteres hexadecimais de SHA-256 sobre ID do evento e código da regra. Isso estabiliza a identidade da ocorrência, mas não constitui assinatura, criptografia ou trilha inviolável. O motor mantém IDs já vistos em memória e ignora repetições. A chave primária também impede duplicação de registros no banco.

Após reinício, o processo reproduz os eventos na ordem de ingestão para reconstruir baseline, prescrições e janela temporal. A estratégia favorece simplicidade e recuperação funcional em pequena escala. Entretanto, o tempo de inicialização cresce com o histórico, e o conjunto de IDs em memória não é limitado. Alterar config.json e reutilizar o banco recompõe estado com regras novas, preservando alertas antigos, sem versionamento de configuração.

### 8.2 Ciclo de resposta

| Estado ou operação | Efeito no protótipo | Restrição |
|---|---|---|
| pending_review | Alerta aguarda revisão | Não equivale a emergência confirmada |
| alerts | Lista o estado atual do banco | Não oferece painel web |
| ack | Altera para acknowledged | Não registra identidade ou justificativa do profissional |
| acknowledged | Marca confirmação de revisão | Não significa tratamento ou resolução |
| run/demo | Exporta relatório e JSON | Exportações não acompanham ack automaticamente |

O console e o banco representam a caixa de entrada demonstrativa da equipe. Não há disparo de SMS, email, webhook ou integração com prontuário. Também não há política de escalonamento para alertas não lidos.

O fluxo pressupõe um consumidor por banco. Falhas de gravação ou interrupção entre o cálculo em memória e a transação não possuem uma política completa de retentativa; reiniciar e reconstruir o estado é a via disponível. Não se reivindica processamento exatamente uma vez de ponta a ponta. Para produção, seriam necessários controle de concorrência, versionamento e auditoria mais completos.

\page

## 9. Método experimental e resultados

### 9.1 Material e protocolo de reprodução

A avaliação usa fixtures geradas por demo.py com semente 42. O conjunto contém 20 eventos de dois pacientes fictícios: doze medidas de baseline, uma prescrição inicial e uma sequência de mudanças, seguida de controles. Os rótulos expected_codes são definidos junto aos casos. O cenário representa uma verificação funcional construída, sem amostragem de pacientes ou obtenção de desfechos clínicos.

Na consolidação, a suíte de testes foi novamente executada e aprovou 17 testes. Os registros disponíveis confirmam o fluxo local, a reexecução sem duplicação, a persistência de ack e o acompanhamento de linha completa com --follow. A duração de 0,327 s da nova suíte é apenas tempo de testes nessa execução, não latência do sistema em condições assistenciais.

### 9.2 Alertas da demonstração

| Cenário sintético | Achados simples | Alertas de fusão | Total |
|---|---:|---:|---:|
| FC 145 bpm e SpO2 88% após baseline | 4 | 0 | 4 |
| Termos críticos e razão de silêncio 0,7 | 2 | 1 | 3 |
| Observação postural sintética | 1 | 1 | 2 |
| Dose demonstrativa 10 para 30 | 1 | 1 | 2 |
| Imobilidade de 2100 segundos | 1 | 1 | 2 |
| Total | 9 | 4 | 13 |

O texto com negação e o evento normal do segundo paciente não geram novos alertas. Na extração local do WAV sintético de oito segundos, a razão de silêncio observada é aproximadamente 0,7491 e a maior pausa calculada é de seis segundos. Esse WAV difere da razão 0,7 fornecida diretamente no evento de demonstração: são duas evidências sintéticas distintas, não resultados intercambiáveis.

### 9.3 Métricas e unidade de análise

A unidade da avaliação é o par evento/código. Obtêm-se TP=13, FP=0 e FN=0. Precisão = TP/(TP+FP), revocação = TP/(TP+FN) e F1 = 2PR/(P+R) são iguais a 1,0 nesse conjunto. Não se calcula uma especificidade clínica, pois a avaliação não define um universo de verdadeiros negativos por condição e desfecho. Um alerta de fusão também conta como código, embora dependa de outros achados.

\page

## 10. Discussão e ameaças à validade

O experimento demonstra concordância entre implementação e expectativa nos fixtures. A principal ameaça à validade interna é a construção dos rótulos a partir das próprias regras: um resultado perfeito é compatível com ausência de generalização. Os testes são úteis contra regressão, mas não constituem um estudo independente de detecção de risco.

### 10.1 Validade de construto e validade externa

As variáveis observadas são proxies. Silêncio não é fadiga, inclinação não é falha de procedimento, mudança de dose não é erro terapêutico e simultaneidade não é causalidade. O construto risco clínico não recebe um desfecho de referência, uma definição operacional de deterioração ou avaliação por profissionais nesta entrega.

O conjunto inclui dois pacientes fictícios e não representa variabilidade de idade, idioma, voz, mobilidade, equipamentos ou contexto assistencial. Não se pode estimar desempenho em outro hospital, câmera ou protocolo. Também não há dados para inferir melhoria de desfechos ou redução do tempo de resposta da equipe.

### 10.2 Dependência entre achados

Um único salto de sinal vital pode disparar limite e escore relativo. Um texto pode ser derivado do áudio. A fusão usa esses achados sem modelar dependência ou confiança. Assim, 13 alertas não representam 13 episódios independentes nem podem ser tratados como amostra clínica de tamanho treze. O número de alertas é uma propriedade da execução, não uma estimativa de incidência.

### 10.3 Tempo real e cobertura

O polling de 250 ms controla a frequência de leitura de novas linhas; não mede a latência total. Transcrição remota, inferência de vídeo, rede e preparação de eventos podem dominar o atraso. O sistema é incremental na ingestão, mas não implementa captura contínua de mídia ou uma garantia de prazo. O --interval adiciona uma pausa artificial entre registros e não simula fielmente os intervalos do paciente.

| Evidência presente | Interpretação admissível | Inferência não sustentada |
|---|---|---|
| 17 testes aprovados | Propriedades testadas permanecem consistentes | Ausência de todos os defeitos |
| 13 códigos concordantes | Fixtures reproduzem a saída esperada | Sensibilidade clínica de 100% |
| Testes simulados de SDK/modelo | Contratos programados funcionam no substituto | Azure/YOLO reais validados |
| Histórico e evidências no banco | Decisão pode ser inspecionada | Auditoria clínica completa ou inviolável |

\page

## 11. Protocolo de validação e evolução

A próxima etapa deve separar calibração, teste técnico de integração e avaliação clínica. Uma execução real de Azure ou YOLO comprovaria um caminho operacional, mas ainda não validaria o uso assistencial. Antes de coletar dados, é necessário definir desfechos, condições de uso e critérios de aceitação com a instituição.

### 11.1 Desenho experimental proposto

Coletar sessões autorizadas de fisioterapia, consultas com fala em português e séries temporais acompanhadas de contexto. Anotações devem identificar episódios e intervalos temporais, com revisão de divergências entre profissionais. Separar desenvolvimento e teste por paciente e sessão, evitando que frames ou trechos do mesmo atendimento apareçam em conjuntos distintos. Quando aplicável, realizar validação em outra unidade e em período posterior.

Comparar três configurações no mesmo conjunto reservado: regras isoladas, regras com fusão atual e uma variante com agrupamento de incidentes e qualidade de sinal. Essa ablação permitiria investigar o efeito incremental da fusão, sem atribuir antecipadamente um ganho. Não houve esse experimento na versão atual.

| Eixo | Medida futura | Unidade e atenção metodológica |
|---|---|---|
| Vídeo | Precisão e revocação de episódios | Janela de tolerância temporal pré-definida |
| Fala | WER e acerto de termos críticos | Separar erro de transcrição e erro semântico |
| Alertas | Falsos alertas e episódios detectados | Por paciente-hora e por episódio, não por frame |
| Tempo | Atraso de detecção e revisão | Percentis e definição do início do episódio |
| Equidade e robustez | Desempenho por condições de captura | Subgrupos com suporte amostral adequado |

### 11.2 Segurança e governança propostas

O banco atual armazena dados em claro e a CLI não possui autenticação. Não há redator de dados pessoais, gestão de consentimento, controle de acesso por profissional ou retenção automática. Chaves de ambiente reduzem a necessidade de gravar segredos no código, mas não implementam um cofre de segredos. Não se afirma conformidade legal a partir dessas escolhas.

Uma implantação futura exigiria avaliação institucional do tratamento dos dados, autenticação e autorização, criptografia, trilha de acesso e decisões, segregação de ambientes, retenção e resposta a incidentes. A arquitetura proposta pode usar filas duráveis e armazenamento gerenciado, mas esses componentes não foram provisionados. A decisão de uso clínico exige uma avaliação própria, externa ao escopo deste relatório.

\page

## 12. Reprodutibilidade e rastreabilidade

O núcleo exige Python 3.11 ou superior e biblioteca padrão. O ambiente registrado usa Python 3.12.14. Os extras Azure e vídeo estão declarados no pyproject.toml, mas sem lockfile validado. Reproduzir integrações externas exige registrar versões resolvidas, pesos utilizados, região dos serviços, configuração e características dos arquivos de entrada. Sem esse registro, mudanças no SDK ou modelo podem alterar resultados.

| Requisito da Fase 4 | Componente correspondente | Situação demonstrada |
|---|---|---|
| Processamento de vídeo | media.analyze_video, YOLOv8 Pose/ByteTrack | Implementado, teste simulado, sem inferência real documentada |
| Áudio e transcrição Azure | WAV local e azure_transcribe | WAV sintético executado, Speech real pendente |
| Termos e sentimento | Léxico local e azure_language | Regras executadas, Language real pendente |
| Sinais vitais | Engine e histórico robusto | Executado com fixtures |
| Evolução de prescrições | Comparação de doses/unidades | Executado com fixtures |
| Movimentação | Evento de imobilidade | Regra executada, sensor externo ausente |
| Alertas automáticos | Console, SQLite, alerts e ack | Fluxo local executado |
| Relatório e apresentação | Este relatório e apresentação associada | Documentação consolidada |
| Vídeo publicado e Git remoto | Ações externas da equipe | Não comprovados nesta entrega |

### 12.1 Artefatos de evidência

summary.json registra os totais, alerts.json expõe cada evidência, metrics.json permite comparação por evento/código e testes.txt registra a suíte anterior. Os arquivos verificacao-cli.json e VERIFICACAO.md descrevem os ensaios de comandos. A nova execução da suíte na consolidação confirmou os mesmos 17 testes aprovados. Os registros são evidência de engenharia, sem assinatura ou controle de integridade institucional.

Para testar configurações diferentes, deve-se utilizar uma pasta de saída nova. A reconstrução do histórico a partir do banco não preserva a versão da regra, portanto misturar experimentos compromete a interpretação. Dados clínicos reais também não devem ser incluídos indiscriminadamente no repositório.

\page

## 13. Conclusões

O Sentinela Multimodal materializa um fluxo local de integração de eventos, detecção explicável, correlação temporal e registro de revisão. A contribuição técnica está na composição de módulos com fronteiras identificáveis e em uma demonstração que torna inspecionável a relação entre entrada, regra e alerta. Os resultados obtidos respondem à questão de integração funcional em condições controladas.

A avaliação disponível não responde à hipótese de benefício clínico. Os 20 eventos sintéticos e 13 alertas confirmam o comportamento esperado do cenário construído. Os 17 testes aprovados protegem propriedades selecionadas do software. Os conectores Azure e YOLO permanecem em um nível diferente de evidência, pois os substitutos de teste não reproduzem todas as condições dos serviços e dos modelos reais.

Do ponto de vista de pós-graduação, a interpretação relevante não é o valor isolado de F1, mas a adequação entre método, unidade de análise e afirmação sustentada. O relatório demonstra por que a avaliação funcional é necessária e insuficiente para decisões clínicas. Expõe também os compromissos de uma arquitetura simples: reprodutibilidade e inspeção do mecanismo em troca de dependência de limiares, alinhamento externo e restrições de escala.

A evolução prioritária envolve executar integrações reais com mídia autorizada, registrar versões e configurações, estabelecer anotações independentes, comparar variantes de fusão e avaliar o custo operacional dos alertas. Em paralelo, a persistência precisa de versão de regras, auditoria por profissional e controle de acesso. Somente após essas etapas seria justificável discutir implantação institucional e desempenho assistencial.

### Síntese das contribuições e dos limites

| Contribuição entregue | Limite que permanece |
|---|---|
| Contrato comum e isolamento por paciente | Identidade e sincronização dependem do produtor |
| Detectores com evidência explícita | Proxies e parâmetros não calibrados clinicamente |
| Conectores de nuvem e vídeo | Validação ponta a ponta ainda pendente |
| Registro e confirmação persistentes | Auditoria e governança incompletas |
| Demonstração reproduzível | Generalização e efetividade não medidas |

O projeto constitui uma base acadêmica reproduzível para investigação e evolução, com limites documentados que impedem confundir uma demonstração de software com uma solução clínica validada.

\page

## 14. Referências

[1] FIAP. 8IADT - Fase 4 - Tech challenge. Enunciado fornecido pelo solicitante, 5 p. Requisitos de análise multimodal e entregáveis acadêmicos.

[2] BALTRUSAITIS, T.; AHUJA, C.; MORENCY, L.-P. Multimodal Machine Learning: A Survey and Taxonomy. Preprint arXiv:1705.09406, 2017. Disponível em: https://arxiv.org/abs/1705.09406. Acesso em: 3 nov. 2026.

[3] NIST. Median Absolute Deviation. Dataplot Reference Manual. Disponível em: https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/mad.htm. Acesso em: 3 nov. 2026.

[4] MICROSOFT. SpeechRecognizer class, Azure Cognitive Services Speech SDK for Python. Disponível em: https://learn.microsoft.com/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.speechrecognizer. Acesso em: 3 nov. 2026.

[5] MICROSOFT. Azure Text Analytics client library for Python. Disponível em: https://learn.microsoft.com/python/api/overview/azure/ai-textanalytics-readme. Acesso em: 3 nov. 2026.

[6] ULTRALYTICS. Pose Estimation. Disponível em: https://docs.ultralytics.com/tasks/pose/. Acesso em: 3 nov. 2026. A documentação corrente pode usar exemplos de versões posteriores; o código analisado seleciona explicitamente yolov8n-pose.pt.

[7] ULTRALYTICS. Multi-Object Tracking. Disponível em: https://docs.ultralytics.com/modes/track/. Acesso em: 3 nov. 2026. O rastreador é selecionado explicitamente como bytetrack.yaml.

[8] SENTINELA MULTIMODAL. Código-fonte versão 1.0.0 e evidências locais. Arquivos examinados: core.py, media.py, cli.py, demo.py, pyproject.toml, config.json, testes e pasta evidencias. Fonte primária dos resultados deste relatório.

[9] PYTHON SOFTWARE FOUNDATION. sqlite3 - DB-API 2.0 interface for SQLite databases. Disponível em: https://docs.python.org/3/library/sqlite3.html. Referência de implementação.

Os documentos MedAssit_Demo.pdf e Relatório Técnico Master - MedAssist V4 (Tech Challenge Fase 3).pdf, fornecidos pelo solicitante, orientaram a organização e o nível de detalhamento. Seus resultados, componentes e alegações de maturidade não foram transferidos para a Fase 4.

\page

## Apêndice A. Reprodução operacional

Execute os comandos na pasta que contém pyproject.toml, config.json e sentinela. No VS Code, abra essa raiz, selecione um interpretador Python 3.11+ e use o terminal integrado. Se o editor estiver em Modo Restrito, a pessoa responsável deve revisar e decidir sobre a confiança da pasta antes de depurar.

### Demonstração local e testes

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m sentinela demo --out resultados/defesa
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### Consulta e confirmação

```powershell
python -m sentinela alerts --db resultados/defesa/monitor.db
python -m sentinela ack ID_DO_ALERTA --db resultados/defesa/monitor.db
```

Nos dois últimos comandos, use o Python do ambiente virtual se ele não estiver ativado. ID_DO_ALERTA é um marcador a substituir por um ID real da listagem. A confirmação não atualiza automaticamente as exportações. Reexecutar run com a mesma entrada e saída renova report.md e alerts.json sem duplicar eventos já registrados.

### Extras e configuração externa

```powershell
python -m pip install -e ".[azure,video]"
```

O extra deve ser instalado no mesmo interpretador usado para executar. Defina AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, AZURE_LANGUAGE_KEY e AZURE_LANGUAGE_ENDPOINT no ambiente do processo. O comando audio com --azure exige WAV PCM mono de 16 bits e recursos válidos. O comando video exige arquivo decodificável, dependências e pesos. As chamadas podem consumir recursos da assinatura e não fazem parte da demonstração local sem credenciais.

### Sequência sugerida para defesa

Apresentar arquitetura, executar demo, mostrar um alerta com evidência, demonstrar a correlação por paciente e confirmar um ID com ack. Em seguida, abrir summary.json, report.md e os testes. A demonstração real de Azure e YOLO deverá ser acrescentada quando houver mídia e serviços preparados. Nenhum vídeo publicado ou repositório remoto é criado por esses comandos.
