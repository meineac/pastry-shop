# ---------------------------------------------------------------------------
# Pastry Shop — Dockerfile
# ---------------------------------------------------------------------------
# Build a slim production image using python:3.12-slim.
# The container serves the Django app via gunicorn.
# ---------------------------------------------------------------------------

FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr (important for log visibility)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies required by psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cached separately from source code)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY . .

# Collect static files at build time
RUN python manage.py collectstatic --noinput

# Expose the port gunicorn will listen on
EXPOSE 8000

# Run database migrations then start gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn pastry_shop.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120"]
