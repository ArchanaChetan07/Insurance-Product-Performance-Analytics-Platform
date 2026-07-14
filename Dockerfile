FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt pyproject.toml README.md ./
COPY insurance_pipeline ./insurance_pipeline
COPY streamlit_ui ./streamlit_ui
COPY Data ./Data
COPY tests ./tests

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install -e .

# Rebuild medallion layers from committed raw Excel, then serve HITL UI
EXPOSE 8501

CMD ["sh", "-c", "python -m insurance_pipeline.run && streamlit run streamlit_ui/claims_review_app.py --server.address=0.0.0.0 --server.port=8501 --browser.gatherUsageStats=false"]
