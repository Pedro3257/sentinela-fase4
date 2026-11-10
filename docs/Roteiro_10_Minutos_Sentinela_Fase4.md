# Roteiro de apresentação - Sentinela Multimodal

Tech Challenge Fase 4 - Apresentação de 18 slides

**Tempo planejado: 8min35s. Margem até dez minutos: 1min25s.** Os tempos são estimativas para ensaio. Este roteiro substitui as durações mais longas das notas originais da apresentação. Use um cronômetro e mantenha a fala natural. O slide 16 explica os comandos, sem acrescentar execução ao vivo a este roteiro.

## Cronograma

| Slide | Tema | Tempo | Acumulado |
|---|---|---|---|
| 1 | Abertura | 20 s | 00:20 |
| 2 | Problema | 25 s | 00:45 |
| 3 | Arquitetura | 30 s | 01:15 |
| 4 | Contrato | 25 s | 01:40 |
| 5 | Sinais vitais | 40 s | 02:20 |
| 6 | Áudio e texto | 30 s | 02:50 |
| 7 | Azure | 30 s | 03:20 |
| 8 | Vídeo | 40 s | 04:00 |
| 9 | Prescrição e movimento | 25 s | 04:25 |
| 10 | Fusão temporal | 35 s | 05:00 |
| 11 | Revisão | 25 s | 05:25 |
| 12 | Resultados | 35 s | 06:00 |
| 13 | Avaliação | 35 s | 06:35 |
| 14 | Limitações | 30 s | 07:05 |
| 15 | Validação futura | 25 s | 07:30 |
| 16 | Reprodução | 35 s | 08:05 |
| 17 | Conclusão | 25 s | 08:30 |
| 18 | Referências | 5 s | 08:35 |

## Slide 1. Sentinela Multimodal

**00:00 a 00:20.** Apresente o objetivo, olhando para a audiência.

“Olá. Vou apresentar o Sentinela Multimodal, desenvolvido para o Tech Challenge da Fase 4. O projeto reúne diferentes dados de pacientes para detectar alterações e gerar alertas rastreáveis. A proposta é demonstrar esse fluxo de engenharia com revisão humana, utilizando um protótipo acadêmico reproduzível.”

## Slide 2. Problema e recorte do projeto

**00:20 a 00:45.** Aponte a relação entre paciente e instante.

“O problema central é integrar informações que chegam em formatos diferentes. Uma medida de saturação, uma fala e um movimento precisam estar associados ao mesmo paciente e ao instante correto. Neste projeto, o recorte de vídeo é a fisioterapia com câmera frontal fixa. O resultado esperado é um alerta explicado para avaliação humana.”

## Slide 3. Arquitetura da solução

**00:45 a 01:15.** Percorra a tabela sem ler todas as células.

“A arquitetura separa os adaptadores de mídia do motor de análise. Os adaptadores extraem informações de áudio e vídeo. Essas informações se tornam eventos padronizados em JSONL. O motor aplica regras, consulta o histórico e realiza a fusão temporal. Por fim, o SQLite armazena os eventos e alertas, que podem ser consultados e confirmados pela equipe.”

## Slide 4. Contrato de eventos e alinhamento

**01:15 a 01:40.** Destaque patient_id e timestamp.

“Cada evento contém um identificador único, o paciente, o instante com fuso horário, a modalidade e os dados. Esse contrato permite integrar fontes diferentes sem misturar históricos. O monitor exige ordem temporal por paciente e ignora IDs repetidos. A identidade e as unidades corretas continuam sendo responsabilidade de quem produz o evento.”

## Slide 5. Sinais vitais e estatística robusta

**01:40 a 02:20.** Explique a ideia da fórmula, sem recitá-la.

“Nos sinais vitais, combinamos limites absolutos com comparação ao histórico do próprio paciente. O histórico usa a mediana e o desvio absoluto mediano, chamado MAD, para construir uma referência menos influenciada por extremos. O escore relativo começa após oito medidas normais e usa até trinta medidas anteriores. O piso da escala evita divisão por zero. Assim, uma alteração pode gerar tanto um alerta de limite quanto um de mudança de padrão. Todos os parâmetros apresentados são demonstrativos e ainda não receberam calibração clínica.”

## Slide 6. Áudio e texto: o que o sistema observa

**02:20 a 02:50.** Diferencie características acústicas e conteúdo verbal.

“No áudio, o sistema calcula energia e pausas em arquivos WAV. No texto, procura expressões como falta de ar e dor no peito, com uma heurística simples de negação. Isso permite desconsiderar alguns casos como ‘nega falta de ar’. Essas observações exigem interpretação: uma pausa pode decorrer da gravação ou da entrevista e não permite diagnosticar uma condição.”

## Slide 7. Integração Azure implementada

**02:50 a 03:20.** Distinga implementação e validação real.

“O conector Azure Speech implementa transcrição contínua em português. O Azure AI Language fornece sentimento e frases-chave, enquanto o léxico local identifica termos críticos. O sentimento permanece como contexto e não aumenta a gravidade. Nesta entrega, os conectores passaram por testes simulados. A chamada real aos serviços com gravações autorizadas ainda está pendente de validação.”

## Slide 8. Vídeo: pose e persistência temporal

**03:20 a 04:00.** Aponte ângulo, confiança e persistência.

“No vídeo, o YOLOv8 Pose estima pontos corporais e o ByteTrack acompanha os rastros entre frames. A regra usa ombros e quadris com confiança mínima de zero vírgula cinco. Uma inclinação do tronco superior a quarenta graus por pelo menos dois segundos gera um achado. Essa medida é bidimensional e pode representar um exercício correto. Além disso, o rastro não identifica clinicamente a pessoa. O extrator está implementado, mas a demonstração apresentada usa uma observação postural sintética, sem inferência real do YOLO.”

## Slide 9. Prescrições e movimentação

**04:00 a 04:25.** Mantenha o foco nos gatilhos das regras.

“Nas prescrições, o programa compara a dose diária do mesmo medicamento e sinaliza quando ela dobra ou cai à metade. Uma mudança de unidade gera revisão separada. Na movimentação, recebe de um produtor externo a duração de imobilidade e sinaliza a partir de trinta minutos. Essas regras apontam alterações e não determinam erro de tratamento.”

## Slide 10. Fusão temporal por paciente

**04:25 a 05:00.** Use os horários do slide para conectar as evidências.

“A fusão temporal é o ponto de integração do projeto. Quando duas ou mais modalidades apresentam achados para o mesmo paciente em até cinco minutos, o motor gera um alerta adicional. No exemplo, primeiro surgem alterações nos sinais vitais, depois termos críticos no áudio e uma observação postural. O alerta preserva os IDs dessas evidências. É uma correlação por regras, sem calcular probabilidade de risco ou assumir que as evidências sejam independentes.”

## Slide 11. Registro e revisão do alerta

**05:00 a 05:25.** Aponte a mudança de estado.

“O alerta nasce como pendente de revisão. A equipe consulta a evidência e usa o comando ack para registrar sua confirmação. O estado passa para acknowledged e permanece no SQLite após o encerramento. Essa confirmação representa revisão, sem declarar resolução clínica. O protótipo ainda não registra a identidade do profissional e não envia notificações externas.”

## Slide 12. Resultados da demonstração sintética

**05:25 a 06:00.** Destaque o total e um exemplo do gráfico.

“A demonstração processou vinte eventos sintéticos e gerou treze alertas, sem rejeições. Quatro alertas vieram das alterações de frequência cardíaca e saturação. Os demais refletem áudio, postura, prescrição e imobilidade, incluindo quatro alertas adicionais de fusão. Portanto, treze alertas não significam treze problemas clínicos independentes. Esse resultado mostra que o fluxo local reproduz o cenário programado.”

## Slide 13. Avaliação funcional e seus limites

**06:00 a 06:35.** Explique a unidade de avaliação e a limitação.

“Precisão, revocação e F1 foram iguais a um na comparação entre os códigos previstos e os esperados. Porém, os próprios casos sintéticos foram construídos a partir das regras. Essa concordância verifica regressão e não mede desempenho em novos pacientes. A apresentação registra dezessete testes da versão funcional original. A revisão de empacotamento acrescentou três testes, totalizando vinte aprovados. A evidência obtida é de consistência funcional.”

## Slide 14. Ameaças à validade

**06:35 a 07:05.** Selecione as limitações centrais.

“As principais limitações são a origem sintética dos dados e o uso de indicadores indiretos de risco. Silêncio não determina fadiga e inclinação não determina falha no procedimento. Os códigos também podem depender da mesma ocorrência. Por fim, o monitor recebe eventos incrementalmente, mas processa arquivos de áudio e vídeo em lote. Ainda não medimos benefício clínico ou latência assistencial.”

## Slide 15. Próxima etapa de validação

**07:05 a 07:30.** Apresente como trabalho futuro.

“A próxima etapa é executar Azure e YOLO com mídia autorizada, registrando versões e configurações. Depois, obter anotações independentes e separar o teste por paciente e sessão. Também precisamos comparar a fusão com regras isoladas e medir falsos alertas por paciente-hora. Autenticação, proteção do banco e auditoria por profissional são requisitos para uma evolução institucional.”

## Slide 16. Demonstração reproduzível

**07:30 a 08:05.** Explique os comandos mantendo o slide visível.

“A reprodução começa na raiz do projeto, com Python três ponto onze ou superior. O primeiro comando gera e processa os dados sintéticos. O segundo executa os testes. Os arquivos report.md e summary.json mostram os resultados, enquanto alerts consulta o banco e ack confirma um alerta. A demonstração local não precisa de serviços externos. Para áudio com Azure ou vídeo real, são necessários os extras correspondentes e a preparação das entradas.”

## Slide 17. Contribuição e conclusão

**08:05 a 08:30.** Retome a contribuição de engenharia.

“A contribuição do Sentinela é um fluxo reproduzível para integrar fontes diferentes, explicar os alertas e preservar sua revisão. Os resultados sustentam o funcionamento desse mecanismo no cenário avaliado. A evolução depende de dados independentes, integrações reais e avaliação institucional antes de qualquer uso assistencial. Assim, o projeto estabelece uma base verificável para continuar a investigação.”

## Slide 18. Referências e evidências

**08:30 a 08:35.** Não leia a bibliografia.

“As referências e evidências estão no relatório. Obrigado.”

## Controle do tempo e perguntas

Ensaie incluindo as trocas de slide. Termine o slide 10 perto de cinco minutos e o slide 15 perto de sete minutos e meio. Se houver atraso, resuma os slides 4, 9 e 16 em uma frase cada. Preserve a explicação da avaliação sintética e das integrações reais pendentes.

Reserve perguntas para depois da exposição. O roteiro não inclui uma execução ao vivo dentro dos dez minutos. Os tempos precisam ser confirmados no seu ritmo de fala.

**Já faz diagnóstico?** Não. O protótipo gera achados para revisão humana.

**Azure e YOLO foram executados de verdade?** Os conectores têm testes simulados; a validação real permanece pendente na entrega documentada.

**F1 igual a um significa acerto clínico de 100%?** Não. É concordância com os códigos dos fixtures determinísticos.

**Como se relacionam os 17 e os 20 testes?** Os documentos acadêmicos registram 17 testes da versão 1.0.0. A manutenção 1.0.1 acrescenta três testes de configuração e portabilidade, sem mudar as regras clínicas demonstrativas.
