import uvicorn

def run_server(host="127.0.0.1", port=8001, debug=False):
    """Run the FastAPI server"""
    uvicorn.run("noviq.backend.api:app", host=host, port=port, reload=debug)

if __name__ == "__main__":
    run_server(debug=True) 