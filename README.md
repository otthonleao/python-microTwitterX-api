# API Microblog Twitter/X
Essa API será um projeto de microblog inspirado no Twitter/X com as principais features de uma API.

### Funcionalidades

#### Usuários
- [ ] Cadastrar de novos usuários (POST)
- [ ] Autenticação e Login (JWT)
- [ ] Seguir outros usuários
- [ ] Perfil com bio e listagem de posts, seguidores e seguidos
- [ ] Postagens

#### Postagens
- [ ] Editar de postagem
- [ ] Deletar postagem
- [ ] Listagem de posts geral (home)
- [ ] Listagem de posts seguidos (timeline)
- [ ] Likes em postagens
- [ ] Postagem pode ser resposta a outra postagem

## Configuração de Ambiente

### Requisitos
1. Python 3 - `$ brew install python@3.12`
2. Gerenciador de Pacoter PIP -  `$ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py` e depois execute o arquivo baixado `$ python3 get-pip.py`.

### Dependências Iniciais
Para instalar as dependências do projetos, utiliza-se um ambiente virtual dentro do diretório que ficará o projeto.
````
python3 -m venv .venv
````
Para ativar a virtualenv
````
# Mac e Linux
source .venv/bin/activate

# Windows Power Shell
.\venv\Scripts\activate.ps1
````
Cria-se um arquivo `requitements-dev.txt` com as ferramentas de produtividade abaixo para ser instaladas em nosso ambiente:
````
ipython         # terminal
ipdb            # debugger
sdb             # debugger remoto
pip-tools       # lock de dependencias
pytest          # execução de testes
pytest-order    # ordenação de testes
httpx           # requests async para testes
black           # auto formatação
flake8          # linter
````
E para instalar as dependências iniciais acima devemos rodar o gerenciador **pip**
````
pip install --upgrade pip
pip install -r requirements-dev.txt
````
### Estrutura de Arquivos e Pastas
Script para criar arquivos do projeto
````
# Arquivos na raiz
touch setup.py
touch {settings,.secrets}.toml
touch {requirements,MANIFEST}.in
touch Dockerfile.dev docker-compose.yaml

# Imagem do banco de dados
mkdir postgres
touch postgres/{Dockerfile,create-databases.sh}

# Aplicação
mkdir -p microtwitterx/{models,routes}
touch microtwitterx/default.toml
touch microtwitterx/{__init__,cli,app,auth,db,security,config}.py
touch microtwitterx/models/{__init__,post,user}.py
touch microtwitterx/routes/{__init__,auth,post,user}.py

# Testes
touch test.sh
mkdir tests
touch tests/{__init__,conftest,test_api}.py
````
Para visualizar a estrutura no terminal pode utilizar o comando tree (`$ brew install tree`)
````
❯ tree -a --filesfirst -L 3 -I docs -I .venv -I .git
.
├── docker-compose.yaml        # Orquestração de containers
├── Dockerfile.dev             # Imagem principal
├── MANIFEST.in                # Arquivos incluidos na aplicação
├── requirements-dev.txt       # Dependencias de ambiente dev
├── requirements.in            # Dependencias de produção
├── .secrets.toml              # Senhas locais
├── settings.toml              # Configurações locais
├── setup.py                   # Instalação do projeto
├── test.sh                    # Pipeline de CI em ambiente dev
├── microtwitterx
│   ├── __init__.py
│   ├── app.py                 # FastAPI app
│   ├── auth.py                # Autenticação via token
│   ├── cli.py                 # Aplicação CLI `$ microtwitterx adduser` etc
│   ├── config.py              # Inicialização da config
│   ├── db.py                  # Conexão com o banco de dados
│   ├── default.toml           # Config default
│   ├── security.py            # Password Validation
│   ├── models
│   │   ├── __init__.py
│   │   ├── post.py            # ORM e Serializers de posts
│   │   └── user.py            # ORM e Serialziers de users
│   └── routes
│       ├── __init__.py
│       ├── auth.py            # Rotas de autenticação via JWT
│       ├── post.py            # CRUD de posts e likes
│       └── user.py            # CRUD de user e follows
├── postgres
│   ├── create-databases.sh    # Script de criação do DB
│   └── Dockerfile             # Imagem do SGBD
└── tests
    ├── conftest.py            # Config do Pytest
    ├── __init__.py
    └── test_api.py            # Tests da API
````
###  Adicionando as dependencias
No arquivo `requirements.in` adicionamos as depedências que iremos usar sem setar as suas versões, pois será sobrescrita com as versões atuais quando compilar.
```
fastapi                      # Framework pra desenvolver API
uvicorn                      # Servidor Web que funciona no protocolo ASGI
psycopg2-binary              # Driver para conectar com Postgres
sqlmodel                     # Classes do Python para descrever tabelas do DB SQL
typer                        # Permite utilizar linhas de comando para administrar o projeto
dynaconf                     # Gerencia as configurações e facilitar o uso de cloud e containers
jinja2                       # Biblioteca para fazer templates
python-jose[cryptography]    # Encriptação de tokens para JWT
passlib[bcrypt]              # Cria o Hash do password para salvar as senhas no DB
python-multipart             # Receber upload de imagens
alembic                      # Database Migration faz o statement entre as classes e a Linguagem SQL
rich                         # Criar tabela no terminal
```
Com isso iremos compilar esse arquivo no qual gerará o arquivo `requirements.txt` com os locks das versões pinadas garantidas.
````
pip-compile requirements.in
````
### API Base
Vamos editar o arquivo `microtwitterx/app.py`
```py
from fastapi import FastAPI;

app = FastAPI(
    title="Micro Twitter X",
    version="0.1.0",
    description="Microblog API developed with FastAPI Framework for Python to post texts like a Twitter/X",
)
```
### Tornando a aplicação instalável
`MANIFEST.in` pega tudo que está no diretório e transforma em pacote.
```
graft microtwitterx
```
`setup.py`
````py
import io
import os
from setuptools import find_packages, setup

def read(*paths, **kwargs):
    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content

def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]

setup(
    name="microtwitterx",
    version="0.1.0",
    description="Microblog API to post texts like a Twitter/X",
    url="microtwitterx.io",
    python_requires=">=3.8",
    long_description="Microblog API developed with FastAPI Framework for Python to post texts like a Twitter/X",
    long_description_content_type="text/markdown",
    author="Otthon Leao",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": ["microtwitterx = microtwitterx.cli:main"]
    }
)
````
### Instalação
O objetivo é instalar a aplicação dentro do container, porém é recomendável que instale também no ambiente local pois desta maneira auto complete do editor irá funcionar.
````
pip install -e .
`````
Para verificar se o entry_point está funcionando como um comando no terminal pode verificar no VSCode > Preferencias > Python: Select Interpreter

## Execução no Docker
No `dockerfile.dev` vamos escrever a imagem do container do projeto que será inicializado.
````docker
# Build the app image
FROM python:3.10

# Create directory for the app user
RUN mkdir -p /home/app

# Create the app user
RUN groupadd app && useradd -g app app

# Create the home directory
ENV APP_HOME=/home/app/api
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# install
COPY . $APP_HOME
RUN pip install -r requirements-dev.txt
RUN pip install -e .

RUN chown -R app:app $APP_HOME
USER app

CMD ["uvicorn","microtwitterx.app:app","--host=0.0.0.0","--port=8000","--reload"]

````
No terminal buildamos o container, no mesmo caminho do arquivo `Dockerfile.dev` e depois executamos:
```
$ docker build -f Dockerfile.dev -t microtwitterx:latest .
$ docker run --rm -it -v $(pwd):/home/app/api -p 8000:8000 microtwitterx
```
Após iniciar o container acesse: http://0.0.0.0:8000/docs ou http://0.0.0.0:8000/redoc para te acesso a documentação

### Rodando o database em um container
Vamos utilizar o Postgres como banco de dados dentro de um container.
Para isso usaremos o script de inicialização abaixo no arquivo `postgres/create-database.sh` que vai ser executado quando o Postgres startar teremos certeza de que o banco de dados está criado.
````bash
#!/bin/bash

set -e
set -u

function create_user_and_database() {
	local database=$1
	echo "Creating user and database '$database'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
	    CREATE USER $database PASSWORD '$database';
	    CREATE DATABASE $database;
	    GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
EOSQL
}

if [ -n "$POSTGRES_DBS" ]; then
	echo "Creating DB(s): $POSTGRES_DBS"
	for db in $(echo $POSTGRES_DBS | tr ',' ' '); do
		create_user_and_database $db
	done
	echo "Multiple databases created"
fi
````
Para rodar o SGDB Postgres crie uma imagem com o seguinte spript no arquivo `postgres/Dockerfile`
````
FROM postgres:alpine3.14
COPY create-databases.sh /docker-entrypoint-initdb.d/
````
### Docker-Compose
Para iniciar a API + o Banco de dados precisaremos de um orquestrador de containers, em produção isso será feito com Kubernetes mas no ambiente de desenvolvimento podemos usar o docker compose.

Edite o arquivo `docker-compose.yaml`

- Definimos 2 serviços `api` e `db`
- Informamos os parametros de build com os dockerfiles
- Na `api` abrimos a porta `8000`
- Na `api` passamos 2 variáveis de ambiente `MICROTWITTERX_DB__uri` e `MICROTWITTERX_DB_connect_args` para usarmos na conexão com o DB
- Marcamos que a `api` depende do `db` para iniciar.
- No `db` informamos o setup básico do postgres e pedimos para criar 2 bancos de dados, um para a app e um para testes.
````docker
version: '3.9'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      MICROTWITTERX_DB__uri: "postgresql://postgres:postgres@db:5432/${MICROTWITTERX_DB:-microtwitterx}"
      MICROTWITTERX_DB__connect_args: "{}"
    volumes:
      - .:/home/app/api
    depends_on:
      - db
    stdin_open: true
    tty: true
  db:
    build: postgres
    image: microtwitterx_postgres-13-alpine-multi-user
    volumes:
      - $HOME/.postgres/microtwitterx_db/data/postgresql:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DBS=microtwitterx, microtwitterx_test
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
````
Agora usamos o `$ docker-compose build` para compilar e depois `$ docker-compose up` para iniciar os dois conteners e deixar o terminal aberto para visualizar os logs.