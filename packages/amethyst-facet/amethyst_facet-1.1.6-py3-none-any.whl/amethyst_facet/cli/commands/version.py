import click

@click.command
def version():
    """Print version and exit
    """

    with open("pyproject.toml") as file:
        for line in file.readlines():
            if line.startswith("version"):
                version_str = line.split()[-1][1:-1]
                break

    print(f"Facet v. {version_str} (July 24, 2025)")