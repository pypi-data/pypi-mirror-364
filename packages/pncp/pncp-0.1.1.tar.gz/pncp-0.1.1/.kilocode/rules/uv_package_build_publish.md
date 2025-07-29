# Instruções para Build e Publicação de Pacotes Python com `uv`

Este documento detalha o processo de construção e publicação de pacotes Python utilizando a ferramenta `uv`.

## 1. Construir o Pacote Python

O `uv` pode criar distribuições de código-fonte (`.tar.gz`) e distribuições binárias (wheels, `.whl`) do seu projeto. Essas distribuições são os arquivos que você publicará em um índice de pacotes como o PyPI.

**Comando:**
Você pode construir seu pacote executando o seguinte comando no diretório raiz do seu projeto (onde o `pyproject.toml` está localizado):

```bash
uv build
```

Por padrão, os artefatos construídos serão colocados em um subdiretório chamado `dist/`. Você pode verificar os arquivos gerados executando:

```bash
ls dist/
```

Isso listará os arquivos `.whl` e `.tar.gz` gerados para o seu projeto.

## 2. Publicar o Pacote Python

Para publicar seu pacote, você usará o comando `uv publish`.

**Autenticação:**
O `uv` suporta vários métodos de autenticação para publicar pacotes. A recomendação do PyPI é usar tokens de API ou editores confiáveis (Trusted Publishers), especialmente para fluxos de CI/CD como o GitHub Actions, pois a autenticação por nome de usuário/senha está depreciada.

*   **PyPI Token:** A forma mais segura e recomendada é usar um token de API do PyPI. Você pode fornecer o token diretamente via linha de comando (não recomendado para ambientes de produção) ou através de uma variável de ambiente.
    *   Via variável de ambiente (recomendado para CI/CD):
        ```bash
        export UV_PUBLISH_TOKEN="seu_token_aqui"
        uv publish
        ```
    *   Via argumento (apenas para testes locais e nunca em scripts):
        ```bash
        uv publish --token "seu_token_aqui"
        ```

*   **Editores Confiáveis (Trusted Publishers):** Se você estiver usando o GitHub Actions, o PyPI oferece um recurso de "Trusted Publishers" que permite que seus fluxos de trabalho se autentiquem diretamente com o PyPI sem a necessidade de armazenar tokens de API como segredos. O `uv` verifica automaticamente por editores confiáveis quando executado no GitHub Actions.

**Publicando para um Índice Personalizado (ex: TestPyPI ou registro privado):**
Se você precisar publicar para um índice diferente do PyPI padrão (como TestPyPI para testes ou um registro privado), você pode configurá-lo no seu `pyproject.toml` na seção `[[tool.uv.index]]`.

Exemplo de configuração para TestPyPI em `pyproject.toml`:
```toml
# pyproject.toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
```
Após configurar isso, você pode publicar para o índice específico usando a flag `--index`:
```bash
uv publish --index testpypi
```

**Comando de Publicação:**
Uma vez que sua autenticação esteja configurada (preferencialmente via `UV_PUBLISH_TOKEN` ou Trusted Publishers), você pode publicar seu pacote com um simples comando:
```bash
uv publish
```
Este comando procurará os artefatos na pasta `dist/` e os enviará para o índice configurado.

## 3. Boas Práticas e Considerações

*   **Versão do Pacote:** Certifique-se de que a versão do seu pacote no `pyproject.toml` seja atualizada antes de cada publicação para evitar conflitos de versão. O `uv` tem comandos para isso (ex: `uv version --bump patch`).
*   **CI/CD:** Para automação, integre `uv build` e `uv publish` em seu pipeline de CI/CD (ex: GitHub Actions) usando tokens de API ou Trusted Publishers para autenticação segura.
*   **`--check-url`:** Para registros não-PyPI, use a opção `--check-url` para evitar o upload de arquivos idênticos que já existem no índice.