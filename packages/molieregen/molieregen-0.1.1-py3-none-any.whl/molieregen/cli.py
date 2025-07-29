import typer
from molieregen.generator import generate_invoice_from_json, generate_template_json
from molieregen.config import load_config, change_config, update_config_field

app = typer.Typer(
    help="📦 Molière – Generate elegant invoices and quotes from JSON and HTML templates.",
    no_args_is_help=True
)

@app.command()
def configure():
    """Configure moliere's default paths"""
    change_config()

@app.command()
def generate(json_path: str, type: str):
    """Generate a PDF invoice from a JSON file"""
    generate_invoice_from_json(json_path, type)
    # TODO maybe open the pdf file after generation

@app.command()
def json():
    """Generate a default JSON file for invoice or quote"""
    generate_template_json()

@app.command("set-config")
def set_config(field: str, value: str):
    """
    🔧 Update a single config field in ~/.moliere/config.json
    """
    # config = load_config()
    # if field not in config:
    #     typer.echo(f"❌ Unknown field: {field}")
    #     typer.echo(f"📝 Available fields: {', '.join(config.keys())}")
    #     raise typer.Exit(1)

    update_config_field(field, value)