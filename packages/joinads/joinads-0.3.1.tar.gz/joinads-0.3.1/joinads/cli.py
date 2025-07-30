import typer
import ast
from typing import List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from pathlib import Path
from joinads.core import pull_models

app = typer.Typer()
console = Console()

@app.command("pull")
def pull(output: str = "models.py"):
    """
    Puxa tabelas do banco e gera tipagens.
    """
    console.print("[cyan]Iniciando DB pull...[/cyan]")
    success = pull_models(output)
    if success:
        console.print(f"[green]Modelos salvos em: {output}[/green]")
    else:
        console.print("[red]Erro ao gerar modelos.[/red]")

@app.command("make:project")
def make_project():
    """
    Cria uma estrutura base de projeto FastAPI.
    """
    folders = [
        "app/controllers",
        "app/routes",
        "app/services",
        "app/repositories",
        "app/jobs",
        "app/core",
        "app/dependencies"
    ]

    files = {
        "app/__init__.py": "",
        "main.py": (
            "from fastapi import FastAPI\n\n"
            "app = FastAPI()\n\n"
            "@app.get('/')\n"
            "def read_root():\n"
            "    return {'msg': 'Hello World'}\n"
        ),
        "settings.py": "# Configurações do projeto\n",
        "requirements.txt": "fastapi\nuvicorn[standard]\n",
        "Dockerfile": (
            "FROM python:3.11\n"
            "WORKDIR /app\n"
            "COPY . .\n"
            "RUN pip install -r requirements.txt\n"
            "CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n"
        ),
        "README.md": "# Projeto FastAPI\n"
    }

    for folder in folders:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓ Pasta criada:[/] {folder}")

    for file_path, content in files.items():
        file = Path(file_path)
        if not file.exists():
            file.write_text(content)
            console.print(f"[blue]✓ Arquivo criado:[/] {file_path}")
        else:
            console.print(f"[yellow]⚠ Arquivo já existe, ignorado:[/] {file_path}")

@app.command("make:repository")
def make_repository():
    """
    Gera repositórios base (CRUD) para as models do projeto.
    """
    models_path = Path("models.py")
    if not models_path.exists():
        console.print("[red]models.py não encontrado. Use `joinads pull` antes.[/red]")
        raise typer.Exit()

    with open(models_path, "r") as f:
        tree = ast.parse(f.read())

    model_names: List[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            model_names.append(node.name)

    if not model_names:
        console.print("[yellow]Nenhuma model encontrada em models.py[/yellow]")
        return

    console.print("[bold cyan]Models disponíveis:[/bold cyan]")
    for i, name in enumerate(model_names, 1):
        console.print(f"{i}. {name}")

    selected = Prompt.ask(
        "[bold green]Digite os números das models (separados por vírgula)[/bold green]",
        default="1"
    )
    indexes = [int(i.strip()) for i in selected.split(",") if i.strip().isdigit()]
    selected_models = [model_names[i - 1] for i in indexes if 0 < i <= len(model_names)]

    Path("app/repositories").mkdir(parents=True, exist_ok=True)

    for model in selected_models:
        file_name = f"app/repositories/{model.lower()}_repository.py"
        if Path(file_name).exists():
            overwrite = Confirm.ask(f"[yellow]Arquivo {file_name} já existe. Sobrescrever?[/yellow]", default=False)
            if not overwrite:
                continue

        with open(file_name, "w") as f:
            f.write(
    f"""from models import {model}
from joinads.repository import Repository
from typing import Any

class {model}Repository(Repository):
    def __init__(self):
        super().__init__({model}.__tablename__)

    def get_by_id(self, id_: int) -> {model} | None:
        return self.where({model}.ID, id_).get()

    def create(self, data: dict) -> int:
        return self.create(data)

    def update(self, id_: int, data: dict) -> bool:
        return self.update(id_, data=data)

    def delete(self, id: int | None = None) -> Any:
        if id is None:
            raise ValueError("id is required")
        return super().delete(id)

    def list_all(self) -> list[{model}]:
        return self.all()
"""
)
    console.print(f"[green]✓ Repository criado:[/] {file_name}")


def main():
    app()

if __name__ == "__main__":
    main()
