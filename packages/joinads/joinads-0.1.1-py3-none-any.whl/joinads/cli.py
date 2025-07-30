import typer
from rich.console import Console
from joinads.core import pull_models

app = typer.Typer()          
app_console = typer.Typer()   

console = Console()

@app_console.command()
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

app.add_typer(app_console, name="")

def main():
    app()

if __name__ == "__main__":
    main()
