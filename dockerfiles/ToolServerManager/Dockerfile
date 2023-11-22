FROM python:3.10

LABEL Role="toolserver.manager"

EXPOSE 8080

WORKDIR /app

COPY ToolServer/ToolServerManager/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ToolServer/ToolServerManager .

RUN mkdir -p assets

HEALTHCHECK --interval=30s --timeout=5s --start-period=1s --retries=3 CMD ["bash", "-c", "curl -sS 'http://localhost:8080/alive' || exit 1"]

ENTRYPOINT [ "gunicorn", "main:app", "-b","0.0.0.0:8080","--worker-class","uvicorn.workers.UvicornWorker"]