# Contrato de eventos

Um objeto JSON por linha, UTF-8, com `id`, `patient_id`, `timestamp`, `modality` e `data`. O arquivo não é um array. Uma quebra de linha completa cada registro consumido por `--follow`.

```json
{"id":"vital-001","patient_id":"PAC-DEMO","timestamp":"2026-01-01T12:00:00Z","modality":"vitals","data":{"heart_rate":145,"spo2":88}}
```

| Modalidade | Conteúdo de data | Unidade |
|---|---|---|
| vitals | Pelo menos uma das chaves heart_rate, spo2, systolic_bp | bpm, %, mmHg |
| prescription | drug e unit não vazios; daily_dose positiva | Dose total diária, unidade consistente |
| movement | immobility_seconds numérico não negativo | segundos |
| text | text não vazio | Português |
| audio | transcript não vazio; acoustic opcional com silence_ratio de 0 a 1 | Razão e texto |
| video | posture_deviation booleano e evidências adicionais | Saída do extrator, não pixels |

IDs devem ser globalmente únicos e imutáveis; paciente é informado pelo produtor. O timestamp deve ter fuso. Eventos atrasados em relação ao último aceito do paciente são rejeitados. Não há conversão automática de unidades.

`schemas/event.schema.json` é a especificação descritiva em JSON Schema. O motor não carrega esse arquivo: a validação de execução é implementada em `core.py`. Constraints de negócio, monotonicidade, IDs e valores finitos não ficam integralmente representadas no schema. Campos de metadados como `expected_codes` são permitidos para fixtures.

Para combinar fontes, atribua IDs distintos, mantenha o patient_id e ordene os eventos por instante antes de `run`. A fusão só combina achados dentro do mesmo consumidor/banco. Use pasta de saída nova para outra configuração ou ensaio.
