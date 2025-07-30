import os
import click
import shutil

# Paths
BASE_DIR = os.path.dirname(__file__)
SHAFTCORE_DIR = os.path.join(BASE_DIR, "shaftcore")
SHAFTCORE_PY = os.path.join(SHAFTCORE_DIR, "shaft.py")
SHAFTCORE_JSON = os.path.join(SHAFTCORE_DIR, "shaft.json")

# Read actual content from shaftcore files
with open(SHAFTCORE_PY, encoding='utf-8') as f:
    core_shaft_code = f.read()

with open(SHAFTCORE_JSON, encoding='utf-8') as f:
    core_shaft_json = f.read()

# Define folder and file structure
SHAFT_STRUCTURE = {
    "shaft.json": core_shaft_json,
    "pivots": {},
    "pipelines": {
        "{project_name}": {
            "default.pipeline.json": "{\n  \"trigger\": \"http\",\n  \"route\": \"/\",\n  \"pipeline\": []\n}"
        }
    },
    "river": {
        "logger.py": "# Custom Shaft logger\n"
    },
    "shaft.py": core_shaft_code
}


def create_structure(base, structure, project_name):
    for name, content in structure.items():
        name = name.replace("{project_name}", project_name)
        path = os.path.join(base, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content, project_name)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content.replace("{project_name}", project_name))


@click.group()
def cli():
    pass

@cli.command()
@click.argument('project_name')
def create(project_name):
    """Create a new Shaft project"""
    if os.path.exists(project_name):
        click.echo(f" Project '{project_name}' already exists.")
        return
    os.makedirs(project_name)
    create_structure(project_name, SHAFT_STRUCTURE, project_name)
    click.echo(f" ✅ Shaft project '{project_name}' created successfully.")

if __name__ == '__main__':
    cli()
