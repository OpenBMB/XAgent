import uvicorn

if __name__ == "__main__":
    uvicorn.run(app="app:app", host="0.0.0.0",
                port=16204, reload=False, workers=8)