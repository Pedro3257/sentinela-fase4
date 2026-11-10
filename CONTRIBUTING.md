# Contribuição

Use Python 3.11+ e uma branch por alteração. Instale o núcleo com `python -m pip install -e .`, execute `python -m unittest discover -s tests -v` e `python scripts/verificar_entrega.py` antes de propor a mudança.

Prefira alterações pequenas com explicação do problema, comportamento esperado e validação executada. Ao modificar uma regra, acrescente um caso que diferencie o comportamento correto do defeito e atualize config.json, default_config.json e documentação quando aplicável.

Utilize somente dados sintéticos ou arquivos cuja utilização esteja autorizada. Não inclua credenciais, dados identificáveis de pacientes, pesos baixados ou ambiente virtual. Descreva claramente se uma integração foi simulada ou executada de fato.

Não abra um PR alegando ganho clínico com base apenas nos fixtures de regressão. Alterações no contrato devem explicar compatibilidade e migração. Evite reutilizar um banco de experimento quando a configuração mudar.
