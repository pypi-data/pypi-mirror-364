import click
import datetime
from pathlib import Path
from modelstack.db import (
    init_db,
    register_model,
    list_models,
    delete_model,
    delete_all_models
)
from modelstack.utils import find_latest_model, load_model, extract_framework


@click.group()
def cli():
    """ModelStack CLI"""
    pass


@click.command()
def init():
    """Initialize the ModelStack database"""
    init_db()
    click.echo("ModelStack database initialized")


@click.command()
@click.argument('name_accuracy')
def register(name_accuracy):
    """Register a model (auto detects file and info)"""
    try:
        tokens = name_accuracy.strip().split()
        name = tokens[0]
        accuracy = float(tokens[1]) if len(tokens) > 1 else None

        file_path = find_latest_model()
        model = load_model(file_path)
        framework = extract_framework(model)

        status = register_model(
            name=name,
            path=str(Path(file_path).resolve()),
            framework=framework,
            accuracy=accuracy,
            timestamp=datetime.datetime.now().isoformat()
        )

        if status == "duplicate":
            confirm = input(f"A model named '{name}' already exists. Replace it? (y/N): ")
            if confirm.lower() == 'y':
                register_model(
                    name=name,
                    path=str(Path(file_path).resolve()),
                    framework=framework,
                    accuracy=accuracy,
                    timestamp=datetime.datetime.now().isoformat(),
                    force_replace=True
                )
                click.echo(f"Replaced and registered '{name}'")
            else:
                click.echo("Registration cancelled.")
        else:
            click.echo(f"Registered '{name}' from {file_path.name}")

    except Exception as e:
        click.echo(f"Error registering model: {e}")


@click.command()
def list():
    """List all registered models"""
    list_models()


@click.command()
@click.argument('name', required=False)
@click.option('--all', '-a', is_flag=True, help="Delete all models")
def delete(name, all):
    """Delete a registered model by name or use --all to delete all"""
    if all:
        confirm = input("Are you sure you want to delete ALL models? (y/N): ")
        if confirm.lower() == 'y':
            delete_all_models()
        else:
            print("Aborted.")
    elif name:
        delete_model(name)
    else:
        print("Please provide a model name or use --all.")


cli.add_command(init)
cli.add_command(register)
cli.add_command(list)
cli.add_command(delete)