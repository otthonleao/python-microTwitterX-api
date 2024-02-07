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