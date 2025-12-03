cat > discord/Dockerfile <<'EOF'
# Simple Dockerfile to run the discord bot
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

# Use an unprivileged user
RUN useradd -m botuser
USER botuser
ENV PATH="/home/botuser/.local/bin:${PATH}"

CMD ["python", "bot.py"]
EOF
