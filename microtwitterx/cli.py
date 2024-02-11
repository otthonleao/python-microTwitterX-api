import typer

from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select

from .config import settings
from .db import engine
from .models import User

main = typer.Typer(name="Micro Twitter/X CLI")

@main.command()
def shell():
    """Abrir microtwitterx shell interativo"""
    _vars = {
        "settings": settings,
        "engine": engine,
        "select": select,
        "session": Session(engine),
        "User": User,
    }
    typer.echo(f"Auto imports: {list(_vars.keys())}")
    try:
        from IPython import start_ipython

        start_ipython(
            argv=["--ipython-dir=/tmp", "--no-banner"], user_ns=_vars
        )
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()


# Listar Usuários
@main.command()
def user_list():
    """Lista todos os usuários"""
    table = Table(title="Micro Twitter/X - Users")
    fields = ["username", "email"]
    for header in fields:
        table.add_column(header, style="magenta")

    with Session(engine) as session:
        users = session.exec(select(User))
        for user in users:
            table.add_row(user.username, user.email)

    Console().print(table)

# Criar Usuário
@main.command()
def create_user(email: str, username: str, password: str):
    """Criar um usuário"""
    with Session(engine) as session:
        user = User(email=email, username=username, password=password)
        session.add(user)
        session.commit()
        session.refresh(user)
        typer.echo(f"created {username} user")
        return user
