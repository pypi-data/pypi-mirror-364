import asyncio
import rich_click as click
from functools import wraps

from agb_sdk.__version__ import version
from agb_sdk.core.dtos.biotrop_bioindex import BiotropBioindex
from agb_sdk.core.use_cases.convert_bioindex_to_tabular import (
    convert_bioindex_to_tabular,
)


def async_cmd(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@click.group(
    "agb-sdk",
    help="Agrobiota SDK CLI",
)
@click.version_option(version)
def main():
    pass


@main.group(
    "convert",
    help="Convert data between formats",
)
def cli_group():
    pass


@cli_group.command("bioindex-to-tabular")
@click.argument(
    "input_path",
    type=click.Path(exists=True),
)
@click.argument(
    "output_path",
    type=click.Path(),
)
@click.option(
    "--resolve-taxonomies",
    is_flag=True,
    default=True,
    help="Resolve taxonomies",
)
@async_cmd
async def convert_bioindex_to_tabular_cmd(
    input_path: str,
    output_path: str,
    resolve_taxonomies: bool = True,
) -> None:

    bioindex: BiotropBioindex | None = None

    try:
        with open(input_path, "r") as f:
            bioindex = BiotropBioindex.model_validate_json(f.read())
    except Exception as e:
        raise click.ClickException(f"Error parsing bioindex: {e}")

    if bioindex is None:
        raise click.ClickException("Failed to parse bioindex")

    await convert_bioindex_to_tabular(bioindex, output_path, resolve_taxonomies)


if __name__ == "__main__":
    main()
