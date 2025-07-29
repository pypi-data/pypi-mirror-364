from .server import app


def main() -> None:
    app.run(transport='stdio')
