FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv

RUN uv sync --no-dev

COPY app/ ./app/
ENV PYTHONPATH=/app

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "app/src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

