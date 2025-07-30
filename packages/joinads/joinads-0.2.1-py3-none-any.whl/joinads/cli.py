import typer
from rich.console import Console
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

def main():
    app()

if __name__ == "__main__":
    main()
