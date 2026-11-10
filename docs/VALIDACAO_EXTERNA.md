# Procedimento para validação externa

**Status: pendente.** Este documento descreve o ensaio; não é um registro de execução real. Não há credenciais ou mídia clínica incluídas.

## Preparação

Instale os extras com `python -m pip install -e ".[azure,video]"`. Prepare WAV PCM mono 16 bits e vídeo frontal de um único paciente de interesse, autorizados para o uso. Guarde entradas reais fora dos arquivos versionados, em `dados-reais/`. Informe um identificador de demonstração e timestamps alinhados.

## Azure

Defina as quatro variáveis de `.env.example` no processo. Execute o comando abaixo em uma única linha:

```powershell
python -m sentinela audio dados-reais/consulta.wav --azure --patient PAC-DEMO --timestamp 2026-01-01T12:00:00Z --id consulta-real-001 --out resultados/real/audio.jsonl
```

Confira `transcription_source=azure_speech`, o texto transcrito, sentimento e frases-chave. Compare com anotação humana. Depois consuma o JSONL com `run` para verificar alertas. Registre versão dos SDKs, região, duração e erros, sem publicar chaves ou conteúdo sensível. O limite local de texto é de 5000 caracteres.

## Vídeo

```powershell
python -m sentinela video dados-reais/fisioterapia.mp4 --patient PAC-DEMO --timestamp 2026-01-01T12:00:00Z --id fisio-real-001 --out resultados/real/video.jsonl
```

Registre hash dos pesos e versões resolvidas. Abra o relatório `.report.json` e confira cada instante no vídeo original. Verifique também sessões sem desvio e oclusões. Uma inclinação correta do exercício não deve ser descrita como falha clínica. Se não houver achados, registre esse resultado sem adulterar a saída.

## Fusão e revisão

Reúna os eventos de todas as fontes para o mesmo paciente, ordene por timestamp e use uma pasta de saída nova. Verifique evidências do alerta de fusão e execute `ack` em um alerta. Não reutilize IDs do ensaio sintético.

## Registro a produzir após o ensaio

Acrescente data, responsável, ambiente, versões, IDs, arquivos de entrada, configuração, resultado esperado, resultado observado e limitações. A avaliação pública deve usar material anonimizado/autorizado. Manter o status pendente até haver evidência. Uma execução operacional real também não substitui a avaliação clínica com dados independentes.
