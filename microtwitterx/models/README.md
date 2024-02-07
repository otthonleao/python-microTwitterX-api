# 2 - Models
É responsável pela lógica de negócios e pela manipulação dos dados armazenando os de modelos de dados ou classes que representam entidades no domínio da aplicação.

Esses modelos são frequentemente utilizados para representar dados estruturados, como registros de banco de dados, objetos JSON, respostas de API, etc.

## 
A modelagem do banco de dados definido é utilizando o SQLModel, que é uma biblioteca que integra o SQLAlchemy e o Pydantic que trabalham juntamente com o FastAPI.

### Modelagem de Usuários
No Arquivo `microtwitterx/models/user.py` mapeamos a classe como a entidade e os atributos como as colunas com as suas respectivas regras do campo(Field)
````python
from typing import Optional;
from sqlmodel import Field, SQLModel;

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    username: str = Field(unique=True, nullable=False)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: str = Field(nullable=False)
    
````
#### Adicionando a inicialização de usuário
Quando o projeto iniciar, precisamos que esta entidade esteja no contexto para que a ORM SQLModel crie essa tabela no banco de dados. Então apontamos a classe User no `microtwitterx/models/__init__.py`
````python
from sqlmodel import SQLModel
from .user import User

__all__ = ["SQLModel", "User"]
````
### Settings
Agora que temos pelo menos uma tabela mapeada para uma classe precisamos estabelecer conexão com o banco de dados e para isso precisamos carregar configurações.

No arquivo `microtwitterx/default.toml`, insira:
````
[default]

[default.db]
uri = ""
connect_args = {check_same_thread=false}
echo = false
````
O valor da `uri` está vindo da variável de ambiente `MICROTWITTERX_DB__uri` que está no `docker-compose.yaml` sendo acessada pelo `.db` e orquestrada pelo **dynaconf**. Dessa forma podemos trabalhar com outros docker-compose somente para testes podemos mudar a conexão URI para o banco de testes.

Quando quiser que a Query SQL seja exibida para debugar, utilize o `echo = true`
#### Dynaconf Lib
No arquivo `microtwitterx/config.py` definiremos que o objeto `settings` irá carregar variáveis do arquivo `default.toml` e em seguida dos arquivos `settings.toml` e `.secrets.toml`(esse deve ser incluído no `.gitignore` para que as senhas não suba para o github).

````python
import os

from dynaconf import Dynaconf

HERE = os.path.dirname(os.path.abspath(__file__))

settings = Dynaconf(
    envvar_prefix="microtwitterx",
    preload=[os.path.join(HERE, "default.toml")],
    settings_files=["settings.toml", ".secrets.toml"],
    environments=["development", "production", "testing"],
    env_switcher="microtwitterx_env",
    load_dotenv=False,
)
````
Assim, será possivel usar **`MICROTWITTERX_`** como prefixo nas variáveis de ambiente para sobrescrever os valores.

### Conectando com o Database
Utilizamos o _engine_ no `microtwitterx/db.py` que é o motor de conexão com o banco de dados para realizar um pull de conexões sync ou async.
````python
from sqlmodel import create_engine
from .config import settings

engine = create_engine(
    settings.db.uri,
    echo=settings.db.echo,
    connect_args=settings.db.connect_args,
)
````
Criamos um objeto engine que aponta para uma conexão com o banco de dados e para isso usamos as variáveis que lemos do settings.

## Database Migrations
Precisamos garantir que a estrtura da tabela exista dentro do banco de dados e para isso é utilizado a biblioteca `alembic` que gerencia as migrações, ou seja, gerando as SQL que alteram a estrtura das tabelas.

Na raiz do repositório utilizamos o `$ alembic init migrations` que criará um arquivo chamado `alembic.ini`e uma pasta chamada `migrations` que armazenará o histórico das alterações no banco de dados.

Para o migrations ser compatível com o `alembic` precisamos editar no `migrations/env.py` as seguintes instruções:
````python
# No topo do arquivo adicionamos a importação dos models 
from microtwitterx import models
from microtwitterx.db import engine
from microtwitterx.config import settings

# Perto da linha 23 mudamos de
# target_metadata = None
# para
target_metadata = models.SQLModel.metadata

# Na função `run_migrations_offline()` mudamos
# url = config.get_main_option("sqlalchemy.url")
# para
url = settings.db.uri

# Na função `run_migration_online` mudamos
# connectable = engine_from_config...
# para
connectable = engine
````
Agora precisamos fazer só mais um ajuste edite `migrations/script.py.mako` e em torno da linha 10 adicione
````py
#from alembic import op
#import sqlalchemy as sa
import sqlmodel  # linha NOVA
````
Agora podemos começar a usar o alembic para gerenciar as migrations, mas precisamos executar este comando dentro do container portando execute no terminal:
````bash
$ docker compose exec api /bin/bash
app@c5dd026e8f92:~/api$ # este é o shell dentro do container
````
E dentro do container rode o alembic (que é uma espécie de git para database), para "iniciar" a comparação do banco com as classes.
````
$ alembic revision --autogenerate -m "initial"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user'
  Generating /home/app/api/migrations/versions/ee59b23815d3_initial.py ...  done
````
O alembic identifica o model User e gera uma migration inicial que fará a criação desta tabela no banco de dados.

Podemos aplicar a migration rodando dentro do container:
````bash
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> ee59b23815d3, initial
````
E neste momento a tabela será criada no Postgres, podemos verificar se está funcionando ainda dentro do container:
````
$ ipython
>>>
````
Digite
````
from sqlmodel import Session, select
from microtwitterx.db import engine
from microtwitterx.models import User

with Session(engine) as session:
    print(list(session.exec(select(User))))
````
O resultado será uma lista vazia [] indicando que ainda não temos nenhum usuário no banco de dados.

Foi preciso muito boilerplate para conseguir se conectar ao banco de dados para facilitar a nossa vida vamos adicionar uma aplicação cli onde vamos poder executar tarefas administrativas no shell.