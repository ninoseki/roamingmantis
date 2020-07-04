import asyncio
import json

import typer

from roamingmantis.moqhao.analyzer import analyze

app = typer.Typer()


@app.command()
def analyze_apk(path: str, extract_dex: bool = True):
    loop = asyncio.get_event_loop()
    gather = asyncio.gather(analyze(path, extract_dex))
    results = loop.run_until_complete(gather)
    loop.close()

    result = results[0]
    typer.echo(json.dumps(result, sort_keys=True, indent=4))


if __name__ == "__main__":
    app()
