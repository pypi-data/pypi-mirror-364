from joinads.SQL.connection import MySQL
from rich.console import Console

console = Console()

def mysql_to_python(mysql_type: str) -> str:
    mysql_type = mysql_type.lower()
    if "int" in mysql_type:
        return "int"
    if "decimal" in mysql_type or "float" in mysql_type or "double" in mysql_type:
        return "float"
    if "bool" in mysql_type or "tinyint(1)" in mysql_type:
        return "bool"
    if "date" in mysql_type or "time" in mysql_type or "year" in mysql_type:
        return "datetime"
    return "str"


def pull_models(output: str) -> bool:
    try:
        tables = MySQL.execute_select("SHOW TABLES", fetch_type='all')
        table_names = [list(t.values())[0] for t in tables]

        with open(output, "w") as f:
            f.write("from dataclasses import dataclass\n\n")
            for table in table_names:
                console.print(f"[bold blue]Gerando modelo para tabela:[/] {table}")
                columns = MySQL.execute_select(f"SHOW COLUMNS FROM `{table}`", fetch_type='all')

                class_name = table.title().replace("_", "")
                f.write(f"@dataclass\nclass {class_name}:\n")
                for col in columns:
                    py_type = mysql_to_python(col['Type'])
                    f.write(f"    {col['Field']}: {py_type}  # tipo real: {col['Type']}\n")
                f.write("\n")
        return True
    except Exception as e:
        console.print(f"[red]Erro ao puxar modelos:[/] {e}")
        return False
