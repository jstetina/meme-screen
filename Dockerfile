FROM python:3.11-slim

# Install system dependencies for X11, display, and image processing
RUN apt-get update && apt-get install --no-install-recommends -y \
    x11-xserver-utils \
    feh \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libfreetype6 \
    libjpeg62-turbo \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY src/sync.py .
COPY src/entrypoint.sh /app/entrypoint.sh

# Create non-root user
RUN useradd -m -s /bin/bash meme && \
    mkdir -p /tmp/meme-screen/pictures && \
    chown -R meme:meme /app /tmp/meme-screen /home/meme

# Set permissions
RUN chmod +x /app/entrypoint.sh

USER meme

# Run the application
CMD ["/app/entrypoint.sh"]
