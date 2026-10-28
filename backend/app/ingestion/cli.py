import typer
from .elexon_client import ElexonClient
from .transform import transform_windfor, transform_fuelhh_wind
from .loader import load_data
from ..repository.db import get_conn

app = typer.Typer()


@app.command()
def ingest(from_: str = typer.Option("2025-12-29"), to: str = typer.Option("2026-02-02")):
    client = ElexonClient()
    try:
        winf = client.fetch_windfor()
        fuel = client.fetch_fuelhh_wind()
        winf_t = transform_windfor(winf)
        fuel_t = transform_fuelhh_wind(fuel)
        conn = get_conn()
        load_data(conn, fuel_t, winf_t)
        conn.close()
        print(f"Loaded actuals={len(fuel_t)} forecasts={len(winf_t)}")
    finally:
        client.close()


if __name__ == "__main__":
    app()
