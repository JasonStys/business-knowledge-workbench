# Portable single-origin service; build assets first and run the API without root privileges.
FROM node:24-bookworm-slim AS web
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY tsconfig.json vite.config.ts index.html ./
COPY web ./web
COPY public ./public
RUN npm run build
FROM python:3.14-slim
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock && useradd --uid 10001 --create-home workbench
COPY server ./server
COPY --from=web /app/dist ./dist
RUN mkdir data && chown workbench:workbench data
USER workbench
ENV KB_DB=/app/data/workbench.sqlite
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=3)"
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000", "--limit-concurrency", "24"]
