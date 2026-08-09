# 📚 BiblioTech

Sistema de gerenciamento de biblioteca, desenvolvido como projeto de estudo
migrando de uma aplicação CLI em Python puro para uma API REST completa em
Django REST Framework, com autenticação JWT e um front-end simples em
HTML/CSS/JavaScript para demonstração.

> Projeto em evolução contínua — parte de um roteiro de aprendizado que
> passou por: CLI Python (DAO/View) → Django → PostgreSQL → Django REST
> Framework → autenticação JWT → front-end de demonstração.

---

## ✨ Funcionalidades

- CRUD completo de livros, autores, categorias, editoras, exemplares e usuários
- Registro de empréstimos, com validação de duplicidade e disponibilidade
- Registro de devoluções, atualizando o estado do exemplar automaticamente
- Autenticação via JWT (tokens de acesso e renovação)
- Front-end mínimo para visualizar o catálogo e testar o fluxo de
  empréstimo/devolução pela interface

## 🛠️ Tecnologias

- **Backend:** Python, Django, Django REST Framework
- **Banco de dados:** PostgreSQL
- **Autenticação:** JWT (`djangorestframework-simplejwt`)
- **Front-end:** HTML, CSS e JavaScript puro (sem frameworks)
- **Outras libs:** `django-cors-headers`, `psycopg2-binary`

## 📁 Estrutura do projeto

```
biblioteca_django/
├── biblioteca/            # App Django: models, views, serializers, urls
├── bibliotech_django/      # Configuração do projeto (settings, urls raiz)
├── frontend/               # Front-end estático (HTML/CSS/JS)
├── manage.py
└── requirements.txt
```

---

## ✅ Pré-requisitos

Antes de começar, tenha instalado:

- [Python 3.11+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/) rodando localmente
- [Git](https://git-scm.com/)
- Extensão **Live Server** no VS Code (ou qualquer outro servidor estático
  simples) para rodar o front-end

---

## 🚀 Como rodar o projeto localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/pdrocairo/biblioteca.git
cd biblioteca
```

### 2. Criar e ativar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux / WSL / macOS
# .venv\Scripts\activate         # Windows (PowerShell)
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Criar o banco de dados no PostgreSQL

Com o PostgreSQL rodando, cria um banco vazio para o projeto:

```bash
sudo -u postgres psql
```

Dentro do `psql`:

```sql
CREATE DATABASE bibliotech_db;
ALTER USER postgres PASSWORD 'sua_senha_aqui';
\q
```

### 5. Configurar a conexão com o banco

Abre `bibliotech_django/settings.py` e confere/ajusta o bloco `DATABASES`
com o nome do banco, usuário e senha que você definiu no passo anterior:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bibliotech_db',
        'USER': 'postgres',
        'PASSWORD': 'sua_senha_aqui',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 6. Rodar as migrations

```bash
python3 manage.py migrate
```

### 7. Criar um superusuário

Esse usuário é o que você vai usar para logar na API (login via sistema de
autenticação padrão do Django):

```bash
python3 manage.py createsuperuser
```

### 8. Subir o servidor Django

```bash
python3 manage.py runserver
```

A API estará disponível em `http://127.0.0.1:8000/api/`.

### 9. Rodar o front-end

Com o servidor Django ativo, abre a pasta `frontend/` no VS Code, clica com
o botão direito em `index.html` → **Open with Live Server**. Ele deve abrir
em `http://127.0.0.1:5500/frontend/index.html`.

Faz login com o superusuário criado no passo 7.

> ⚠️ O front-end espera a API rodando em `http://127.0.0.1:8000`. Se você
> mudar a porta do Django, ajuste a constante `API_BASE` no arquivo
> `frontend/script.js`.

---

## 🔑 Autenticação

A API usa JWT. Para obter um token, faça um `POST` para:

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

## 📡 Principais endpoints

| Método | Endpoint                                     | Descrição                          |
|--------|-----------------------------------------------|-------------------------------------|
| GET    | `/api/livros/`                                | Lista todos os livros               |
| POST   | `/api/livros/`                                | Cadastra um novo livro              |
| GET    | `/api/exemplares/`                            | Lista todos os exemplares           |
| GET    | `/api/emprestimos/`                           | Lista todos os empréstimos          |
| POST   | `/api/emprestimos/registrar_emprestimo/`      | Registra um novo empréstimo         |
| PATCH  | `/api/emprestimos/registrar_devolucoes/`      | Registra a devolução de um exemplar |
| POST   | `/api/token/`                                 | Login (gera tokens JWT)             |
| POST   | `/api/token/refresh/`                         | Renova o token de acesso            |

Todos os endpoints (exceto `/api/token/` e `/api/token/refresh/`) exigem o
header `Authorization: Bearer <token>`.

---

## 🗺️ Próximos passos

- [ ] Migrar o front-end para React
- [ ] Deploy do backend (Render/Railway) e do front-end (Vercel)
- [ ] Variáveis sensíveis (senha do banco, `SECRET_KEY`) via `.env`

---

## 👤 Autor

**Pedro Cairo**
[LinkedIn](https://linkedin.com/in/pedro-cairo) · [GitHub](https://github.com/pdrocairo)
