FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV IS_DOCKER=true
ENV TRADING_MODE=paper
ENV MAX_POSITION_SIZE=3
ENV MAX_TRADES_PER_DAY=2

# Create non-root user for security
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "print('Bot is healthy')" || exit 1

# Run the application
CMD ["python", "run_fly_worker.py"]
