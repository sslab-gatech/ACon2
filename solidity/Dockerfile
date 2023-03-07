# syntax=docker/dockerfile:1.2
FROM ubuntu:latest
WORKDIR /app

# use bash
#RUN ln -sf /bin/bash /bin/sh
RUN chsh -s /bin/bash root

# Install Python3 and utils
RUN apt-get update && apt-get install -y --no-install-recommends \
		python3 \
		python3-pip \
		python3-dev \
		build-essential \
		screen \
		curl \
		git \
		jq \
		&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Install foundry
RUN curl -L https://foundry.paradigm.xyz | bash
RUN /root/.foundry/bin/foundryup

# Install python packages
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy artifacts
COPY lib/ ./lib
COPY plots/ ./plots
COPY foundry.toml ./foundry.toml
COPY remappings.txt ./remappings.txt
COPY script/ ./script
COPY src/ ./src
COPY test/ ./test
COPY output_CR/ ./output_CR
RUN mkdir -p ./output

