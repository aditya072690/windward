import typer

app = typer.Typer()


@app.command()
def ingest(from_: str = typer.Option("2025-12-29"), to: str = typer.Option("2026-02-02")):
    print(f"Ingesting from {from_} to {to} (stub)")


if __name__ == "__main__":
    app()
