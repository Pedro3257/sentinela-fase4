# Verificação da entrega do repositório

Data: 10 de novembro de 2026. Versão de manutenção: 1.0.1.

## Executado localmente

- **20 testes aprovados** em Python 3.12.14 no Windows. Registro em `testes_repositorio.txt`.
- Wheel construído com sucesso e instalado em ambiente virtual novo, sem extras de Azure/vídeo.
- CLI do pacote instalado executada em diretório temporário fora do código, usando a configuração incluída no pacote.
- Comando de entrada `sentinela.exe demo` executado fora do repositório: **20 eventos, 13 alertas e zero rejeições**.
- Estrutura de entrega, links locais do README e arquivos JSON verificados por `scripts/verificar_entrega.py`. Registro em `verificacao_instalacao.json`.
- Roteiro de até dez minutos recomposto, incluído e renderizado para revisão visual.
- Configuração do VS Code utiliza o interpretador selecionado, sem caminho particular desta máquina.

As três verificações de configuração/portabilidade se somam aos 17 testes históricos. Os relatórios e slides anteriores continuam sendo registros da versão funcional 1.0.0. A revisão não mudou os critérios de detecção.

## Não executado

- A matriz GitHub Actions de Python 3.11/3.12 em Windows/Linux ainda depende da publicação e execução remota. A validação local não comprova todos os ambientes da matriz.
- Conectores Azure e inferência YOLO reais continuam pendentes; os testes desses contratos são simulados.
- O Dockerfile do núcleo foi fornecido, mas a imagem não foi construída/executada nesta verificação.
- Não houve validação clínica, gravação/publicação de vídeo ou publicação de remoto GitHub.

## Rastreabilidade

O relatório final, a apresentação, o roteiro e o guia estão em `docs/`. Os dados sintéticos e resultados históricos ficam nesta pasta. O banco não é distribuído como artefato versionado: a demonstração o recria. O arquivo `.gitignore` exclui bancos, chaves, ambientes, resultados e dados reais, sem excluir as fixtures sintéticas.
