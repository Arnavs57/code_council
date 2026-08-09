# HACKATHON SHOWCASE ONLY — intentionally weak container definition for DevOps findings.
FROM python:3.11

WORKDIR /app
COPY backend /app

# Demo anti-pattern: bake production env into the image layer.
COPY .env.production /app/.env.production

ENV CCAI_ENVIRONMENT=production
ENV CCAI_DATABASE_URL=sqlite:///./code_council.db
ENV CCAI_JWT_SECRET=super_secret_key_do_not_ship_12345

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
