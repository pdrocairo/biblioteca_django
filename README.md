# 📚 BiblioTech

Sistema de gerenciamento de biblioteca, desenvolvido como projeto de estudo
migrando de uma aplicação CLI em Python puro para uma API REST completa em
Django REST Framework, com autenticação JWT, perfis de acesso e um front-end
simples em HTML/CSS/JavaScript para demonstração.

> Projeto em evolução contínua — parte de um roteiro de aprendizado que
> passou por: CLI Python (DAO/View) → Django → PostgreSQL → Django REST
> Framework → autenticação JWT → refatoração (segurança, testes, Docker).

---

## ✨ Funcionalidades

- CRUD de livros, autores, categorias, editoras, exemplares e usuários
- Registro de empréstimos, com validação de duplicidade e disponibilidade
- Registro de devoluções, com data de devolução e atualização automática do exemplar
- Regra de negócio transacional: se qualquer passo falhar, nada é gravado pela metade
- Autenticação via JWT (tokens de acesso e renovação)
- Perfis de acesso: qualquer usuário logado consulta o catálogo, mas só **bibliotecários** alteram dados, registram empréstimos/devoluções e gerenciam usuários
- Senhas guardadas com hash (nunca aparecem na API) e configuração sensível em `.env`
- Histórico preservado: não é possível apagar um usuário ou exemplar que já tenha empréstimos
- Front-end mínimo para visualizar o catálogo e testar o fluxo de empréstimo/devolução

## 🛠️ Tecnologias

- **Backend:** Python 3.14, Django 6.1, Django REST Framework
- **Banco de dados:** PostgreSQL
- **Autenticação:** JWT (`djangorestframework-simplejwt`)
- **Infra:** Docker, Docker Compose e deploy no Render (`gunicorn` + `whitenoise`)
- **Front-end:** HTML, CSS e JavaScript puro (sem frameworks)
- **Outras libs:** `django-cors-headers`, `psycopg2-binary`, `python-decouple`

## 📁 Estrutura do projeto

```
biblioteca_django/
├── biblioteca/             # App Django
│   ├── models.py           # Modelos (Livro, Exemplar, Emprestimo, Usuario...)
│   ├── services.py         # Regra de negócio de empréstimo e devolução
│   ├── permissions.py      # IsBibliotecario
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── bibliotech_django/      # Configuração do projeto (settings, urls raiz)
├── frontend/               # Front-end estático (HTML/CSS/JS)
├── Dockerfile
├── render.yaml             # Blueprint de deploy (Render)
├── build.sh                # Build da API no Render
├── docker-compose.yml
├── .env.example            # Modelo das variáveis de ambiente
├── manage.py
└── requirements.txt
```

---

## 🐳 Como rodar com Docker (recomendado)

É o caminho mais curto: só precisa de [Docker](https://docs.docker.com/engine/install/)
com o plugin Compose e do [Git](https://git-scm.com/).

### 1. Clonar e configurar o `.env`

```bash
git clone https://github.com/pdrocairo/biblioteca_django.git
cd biblioteca_django
cp .env.example .env
```

Abra o `.env` e preencha `SECRET_KEY` e `DB_PASSWORD`. Para gerar uma chave:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

> ⚠️ Mantenha a `SECRET_KEY` entre aspas simples, como no exemplo: ela pode
> conter `$`, que o Docker Compose interpretaria como variável.

Os valores de `DB_HOST` e `DB_PORT` do `.env` valem só para rodar **sem** Docker;
o Compose já aponta o Django para o serviço `db` por conta própria.

### 2. Subir os serviços

```bash
docker compose up --build
```

Isso sobe o PostgreSQL e o Django, e aplica as migrations automaticamente.
A API fica em `http://127.0.0.1:8000/api/`.

### 3. Criar o primeiro bibliotecário

Em outro terminal:

```bash
docker compose exec web python manage.py createsuperuser
```

Todo superusuário já nasce com perfil de **bibliotecário**.

### 4. Rodar o front-end

O front-end é estático e fica fora do Compose. Em outro terminal, na raiz do projeto:

```bash
python3 -m http.server 5500 --directory frontend
```

Acesse `http://127.0.0.1:5500` e faça login com o usuário do passo 3.

### Comandos úteis

| Comando | O que faz |
|---|---|
| `docker compose up -d` | Sobe em segundo plano |
| `docker compose logs -f web` | Acompanha os logs do Django |
| `docker compose exec web python manage.py test` | Roda os testes |
| `docker compose down` | Para os serviços (mantém os dados) |
| `docker compose down -v` | Para e **apaga** o banco do container |

O PostgreSQL do container fica exposto na porta **5433** do seu computador, para
não colidir com um Postgres local na 5432. Dá para conectar com qualquer cliente
(DBeaver, `psql`) usando o banco, usuário e senha do `.env`.

---

## 💻 Como rodar sem Docker

### Pré-requisitos

- [Python 3.12+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/) rodando localmente
- [Git](https://git-scm.com/)

### 1. Clonar e criar o ambiente virtual

```bash
git clone https://github.com/pdrocairo/biblioteca_django.git
cd biblioteca_django
python3 -m venv .venv
source .venv/bin/activate        # Linux / WSL / macOS
# .venv\Scripts\activate         # Windows (PowerShell)
pip install -r requirements.txt
```

### 2. Criar o banco no PostgreSQL

```bash
sudo -u postgres psql
```

Dentro do `psql`:

```sql
CREATE DATABASE bibliotech_db;
ALTER USER postgres PASSWORD 'sua_senha_aqui';
\q
```

### 3. Configurar o `.env`

```bash
cp .env.example .env
```

Preencha o `.env` com a `SECRET_KEY` e os dados do banco criado no passo anterior
(`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST=localhost`, `DB_PORT=5432`).

### 4. Migrations, superusuário e servidor

```bash
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
```

A API estará em `http://127.0.0.1:8000/api/`. Para o front-end, siga o passo 4
da seção do Docker.

> ⚠️ O front-end espera a API em `http://127.0.0.1:8000`. Se mudar a porta do
> Django, ajuste o endereço em `frontend/config.js`.

---

## 🧪 Testes

A suíte cobre empréstimo, bloqueio por empréstimo ativo, livro sem exemplar,
devolução (incluindo exemplar que não está emprestado), acesso sem token (401),
permissões por perfil (403), escrita restrita ao bibliotecário, ausência de senha nas respostas, login JWT e a
proteção do histórico de empréstimos.

```bash
python3 manage.py test                                # sem Docker
docker compose exec web python manage.py test         # com Docker
```

---

## 🔑 Autenticação e perfis

A API usa JWT. Para obter um token:

```
POST /api/token/
Content-Type: application/json

{
    "username": "seu_usuario",
    "password": "sua_senha"
}
```

A resposta traz dois tokens:

```json
{
    "refresh": "...",
    "access": "..."
}
```

Use o `access` no header das requisições seguintes:

```
Authorization: Bearer SEU_ACCESS_TOKEN
```

Quando o `access` expirar, renove sem precisar logar de novo:

```
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "SEU_REFRESH_TOKEN"
}
```

### Perfis

Cada `Usuario` está ligado a um `User` do Django (um único cadastro) e tem um
`perfil`:

| Perfil | Pode |
|---|---|
| `leitor` | Apenas consultar o catálogo (livros, autores, categorias, editoras, exemplares) |
| `bibliotecario` | Tudo do leitor, mais cadastrar/alterar/remover itens do catálogo, ver e registrar empréstimos/devoluções e gerenciar usuários |

Um superusuário criado com `createsuperuser` já é bibliotecário. Os demais
usuários são cadastrados por um bibliotecário em `POST /api/usuarios/`.

## 📡 Endpoints

Todos exigem o header `Authorization: Bearer <token>`, exceto os de `/api/token/`.

| Método | Endpoint | Descrição | Quem |
|---|---|---|---|
| POST | `/api/token/` | Login (gera os tokens JWT) | público |
| POST | `/api/token/refresh/` | Renova o token de acesso | público |
| GET | `/api/livros/`, `/api/autores/`, `/api/categorias/`, `/api/editoras/`, `/api/exemplares/` | Lista (e detalha em `/{id}/`) | autenticado |
| POST, PUT, PATCH, DELETE | os mesmos endpoints | Cadastra / altera / remove | bibliotecário |
| GET | `/api/emprestimos/` e `/api/emprestimos/{id}/` | Consulta os empréstimos (somente leitura) | bibliotecário |
| POST | `/api/emprestimos/registrar_emprestimo/` | Registra um empréstimo | bibliotecário |
| PATCH | `/api/emprestimos/registrar_devolucoes/` | Registra uma devolução | bibliotecário |
| GET, POST | `/api/usuarios/` | Lista / cadastra usuários | bibliotecário |
| GET, PUT, PATCH, DELETE | `/api/usuarios/{id}/` | Detalha / altera / remove um usuário | bibliotecário |

Empréstimos não podem ser criados nem alterados pela rota genérica (`POST /api/emprestimos/`
responde `405`): eles só nascem e terminam pelas duas ações acima, que passam pela regra de negócio.

### Empréstimo e devolução

```
POST /api/emprestimos/registrar_emprestimo/
{ "id_usuario": 2, "id_livro": 1 }

PATCH /api/emprestimos/registrar_devolucoes/
{ "id_usuario": 2, "id_exemplar": 1 }
```

| Status | Quando |
|---|---|
| `201` / `200` | Empréstimo / devolução registrados |
| `400` | Campos ausentes ou inválidos (ids precisam ser inteiros positivos) |
| `401` | Sem token ou token expirado |
| `403` | Usuário autenticado que não é bibliotecário |
| `404` | Usuário, livro ou exemplar inexistente |
| `409` | Usuário já tem empréstimo ativo, livro sem exemplar disponível, ou devolução de um exemplar que o usuário não tem emprestado |

Erros de regra de negócio vêm como `{"erro": "mensagem"}`.

### Cadastrar um usuário

```
POST /api/usuarios/
{
    "nome": "Maria Silva",
    "email": "maria@exemplo.com",
    "perfil": "leitor",
    "username": "maria",
    "password": "uma-senha-forte-123"
}
```

A senha é validada pelos validadores do Django e guardada com hash. Ela nunca
é devolvida pela API.

---

## ☁️ Deploy no Render

O arquivo [`render.yaml`](render.yaml) descreve tudo (API, front-end estático e
PostgreSQL), então o deploy é um "Blueprint":

1. Suba o projeto para o GitHub e crie uma conta em [render.com](https://render.com).
2. No painel: **New → Blueprint**, escolha este repositório e confirme.
3. Quando o Render pedir as variáveis marcadas para preenchimento manual, informe:

   | Variável | Serviço | Valor |
   |---|---|---|
   | `DJANGO_SUPERUSER_USERNAME` | `bibliotech-api` | login do primeiro bibliotecário |
   | `DJANGO_SUPERUSER_EMAIL` | `bibliotech-api` | e-mail dele |
   | `DJANGO_SUPERUSER_PASSWORD` | `bibliotech-api` | uma senha forte (nesse modo o Django **não** valida a senha, então escolha uma boa) |
   | `CORS_ALLOWED_ORIGINS` | `bibliotech-api` | URL do front-end, ex.: `https://bibliotech-web.onrender.com` |
   | `API_URL` | `bibliotech-web` | URL da API, ex.: `https://bibliotech-api.onrender.com` |

4. Aguarde o build. A `SECRET_KEY` é gerada pelo Render, e a `DATABASE_URL` vem do banco.

> Se o nome `bibliotech-api` ou `bibliotech-web` já estiver em uso, o Render
> acrescenta um sufixo à URL. Nesse caso, corrija `CORS_ALLOWED_ORIGINS` e `API_URL`
> com as URLs reais (em **Environment**) e faça um novo deploy dos dois serviços.

O primeiro bibliotecário é criado na subida da API com as variáveis
`DJANGO_SUPERUSER_*`, porque o plano gratuito não oferece Shell. Depois, ele
cadastra os demais usuários em `POST /api/usuarios/`.

**Limites do plano gratuito** (confira as condições atuais no site do Render):
a API "dorme" após alguns minutos sem uso e a primeira requisição depois disso
demora cerca de um minuto; o PostgreSQL gratuito expira depois de 30 dias.
Serve para portfólio, mas não para dados que você precise manter.

---

## 🗺️ Próximos passos

- [ ] Documentação automática da API (Swagger com `drf-spectacular`)
- [ ] Usar `gunicorn` também na imagem Docker (hoje ela usa o `runserver`, só para desenvolvimento)
- [ ] Migrar o front-end para React

> Dívida conhecida: `Usuario` ainda repete `nome` e `email` que o `User` do
> Django já guarda.

---

## 👤 Autor

**Pedro Cairo**
[LinkedIn](https://linkedin.com/in/pedro-cairo) · [GitHub](https://github.com/pdrocairo)
