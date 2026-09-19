FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY backend ./backend
RUN python -m pip install --no-cache-dir .
EXPOSE 18765
CMD ["uvicorn", "proofops_api.app:app", "--host", "0.0.0.0", "--port", "18765"]
