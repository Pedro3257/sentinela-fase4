# Publicar o repositório

Esta pasta reúne os arquivos do repositório público [Pedro3257/sentinela-fase4](https://github.com/Pedro3257/sentinela-fase4), publicado em 10 de novembro de 2026. A cópia local tem remoto configurado e histórico Git. O ZIP distribuído anteriormente contém os arquivos, sem histórico `.git`. As instruções abaixo também servem para publicar uma cópia própria.

## 1. Validar

```powershell
python -m pip install .
python -m unittest discover -s tests -v
python scripts/verificar_entrega.py
```

Leia `evidencias/VERIFICACAO_REPOSITORIO.md`. O teste local não comprova execução da CI remota nem validação de serviços Azure/YOLO reais.

## 2. Iniciar histórico e revisar arquivos

Dentro da pasta extraída do ZIP, execute `git init -b main` se ainda não houver repositório. Na cópia local já inicializada, pule esse comando. Confira o estado e prepare o commit:

```powershell
git status
git add .
git diff --cached --stat
```

Revise os arquivos preparados. `.env`, bancos, resultados, ambientes e dados reais estão ignorados. O `.env.example` sem chaves, fixtures sintéticas e documentos devem ser incluídos. Um `.gitignore` não remove segredos já enviados anteriormente; esta entrega não contém histórico anterior.

Se seu Git ainda não tiver nome e email configurados, configure sua identidade local antes do commit, usando seus próprios dados. Nenhuma identidade foi inventada ou configurada pela entrega.

```powershell
git commit -m "Organiza entrega academica Sentinela Fase 4"
```

## 3. Criar o remoto e enviar

Crie um repositório vazio na sua conta do GitHub e copie a URL real. Nos comandos abaixo, substitua URL_DO_SEU_REPOSITORIO; ela é um marcador, não um endereço pronto:

```powershell
git remote add origin URL_DO_SEU_REPOSITORIO
git push -u origin main
```

Se já existe um remoto, confira `git remote -v` e a relação entre históricos antes de enviar. Não use `--force` para substituir um repositório existente.

## 4. Conferir a entrega publicada

Abra o README, os documentos e a aba Actions. A CI prevista testa Python 3.11/3.12 em Windows e Linux. Ela usa somente o núcleo local e não precisa de segredos. Os SDKs externos são simulados na suíte.

Quando gravar/publicar a apresentação, adicione ao README o link real e a data. O roteiro de até dez minutos está em `docs/Roteiro_10_Minutos_Sentinela_Fase4.pdf`. As validações externas pendentes estão em `VALIDACAO_EXTERNA.md`.

Referência da CI: [GitHub Docs - Building and testing Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python).
