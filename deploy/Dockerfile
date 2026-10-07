FROM python:3.14-slim
RUN useradd -m -u 1000 space
WORKDIR /home/space/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=space:space . .
USER space
ENV PYTHONPATH=/home/space/app \
    PYTHONUNBUFFERED=1 \
    SCAYL_LLM_MODE=cache \
    SCAYL_HOSTED=1 \
    SCAYL_SNAPSHOT_DIR=data/processed/v1 \
    SCAYL_LLM_CACHE=/home/space/app/data/cache/llm \
    SCAYL_STATE_DIR=/home/space/app/data/state
EXPOSE 7860
CMD ["python", "-m", "streamlit", "run", "app/space.py", "--server.address=0.0.0.0", "--server.port=7860", "--server.enableStaticServing=false", "--server.enableXsrfProtection=true", "--server.enableCORS=true"]
