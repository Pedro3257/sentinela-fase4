# Publicação e primeira execução de CI

Data: 10 de novembro de 2026.

Repositório público: https://github.com/Pedro3257/sentinela-fase4

Execução verificada: https://github.com/Pedro3257/sentinela-fase4/actions/runs/42868052893

Commit testado: `88acfa3fb8250bd145a8450fb130000671ea5d99`.

## Resultado observado no GitHub Actions

**Success: 4 jobs completed.** A primeira matriz terminou em 33 segundos de duração total informada pelo GitHub.

| Ambiente | Resultado |
|---|---|
| ubuntu-latest / Python 3.11 | Aprovado |
| ubuntu-latest / Python 3.12 | Aprovado |
| windows-latest / Python 3.11 | Aprovado |
| windows-latest / Python 3.12 | Aprovado |

Cada job instala o núcleo, executa os 20 testes e verifica a estrutura documental e a CLI instalada fora da pasta do código. Nenhum segredo Azure foi fornecido à CI.

O tempo informado é o da execução de CI, não uma medida de latência clínica. O resultado comprova os checks desse commit; execuções posteriores devem ser consultadas na aba Actions. Azure/YOLO reais, avaliação clínica e vídeo publicado continuam pendentes.

Os registros locais anteriores que indicam CI pendente documentam o estado antes da publicação. Este arquivo registra a atualização após a primeira execução remota.
