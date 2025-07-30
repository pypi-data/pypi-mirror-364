import asyncio
from functools import wraps

import rich_click as click

from agb_sdk.__version__ import version
from agb_sdk.core.dtos import BiotropBioindex
from agb_sdk.core.use_cases import convert_bioindex_to_tabular
from agb_sdk.settings import DEFAULT_TAXONOMY_URL


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
    help=(
        "The path to the input file. This is the JSON file that contains the "
        "Biotrop Bioindex."
    ),
)
@click.argument(
    "output_path",
    type=click.Path(),
    help=(
        "The path to the output file. This is the XLSX file that will contain "
        "the tabular data."
    ),
)
@click.option(
    "--resolve-taxonomies",
    is_flag=True,
    default=True,
    show_default=True,
    help=(
        "If true, the taxonomies will be resolved from the taxonomy service. "
        "Otherwise the TaxID values will be used as is."
    ),
)
@click.option(
    "--taxonomy-url",
    type=str,
    default=DEFAULT_TAXONOMY_URL,
    show_default=True,
    envvar="TAXONOMY_URL",
    help="The URL to the taxonomy service.",
)
@async_cmd
async def convert_bioindex_to_tabular_cmd(
    input_path: str,
    output_path: str,
    resolve_taxonomies: bool = True,
    **kwargs,
) -> None:

    bioindex: BiotropBioindex | None = None

    try:
        with open(input_path, "r") as f:
            bioindex = BiotropBioindex.model_validate_json(f.read())
    except Exception as e:
        raise click.ClickException(f"Error parsing bioindex: {e}")

    if bioindex is None:
        raise click.ClickException("Failed to parse bioindex")

    await convert_bioindex_to_tabular(
        bioindex,
        output_path,
        resolve_taxonomies,
        **kwargs,
    )


if __name__ == "__main__":
    main()
