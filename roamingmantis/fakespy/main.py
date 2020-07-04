import json

import typer

from roamingmantis.fakespy.analyzer import analyze
from roamingmantis.fakespy.client import Client

app = typer.Typer()


@app.command()
def send_command(command: str, c2: str, mobile_number: str = "xx"):
    client = Client(c2=c2, mobile_number=mobile_number)
    res = client.query(command)
    formatted_json = json.dumps(res, indent=2)
    typer.echo(formatted_json)


@app.command()
def analyze_apk(path: str, extract_dex: bool = False, verbose: bool = False):
    res = analyze(path, extract_dex, verbose)
    formatted_json = json.dumps(res, indent=2)
    typer.echo(formatted_json)


if __name__ == "__main__":
    app()
