import click


@click.group(
    help="SchemaHound CLI.",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(package_name="schemahound")
@click.option("-v", "--verbose", count=True, help="Increase verbosity level.")
@click.pass_context
def main(ctx: click.Context, verbose: int) -> None:
    """SchemaHound CLI entry point."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
