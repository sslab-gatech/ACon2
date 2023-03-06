# syntax=docker/dockerfile:1.2
FROM ubuntu:latest
WORKDIR /app

# Install Python3
RUN apt-get update && apt-get install -y --no-install-recommends \
		python3 \
		python3-pip \
		python3-dev \
		build-essential \
		&& apt-get clean && rm -rf /var/lib/apt/lists/*
		
# Install python packages
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy artifacts
COPY acon2/ ./acon2
COPY data/ ./data
COPY plots/ ./plots
COPY utils/ ./utils
COPY scripts/ ./scripts
COPY main.py ./main.py
COPY output_CR/ ./output_CR
RUN mkdir -p ./output

