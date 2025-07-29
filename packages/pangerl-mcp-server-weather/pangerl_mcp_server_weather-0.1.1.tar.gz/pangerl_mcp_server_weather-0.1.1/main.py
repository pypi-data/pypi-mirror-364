from src.pangerl_mcp_server_weather import app


if __name__ == "__main__":
    app.run(transport='stdio')