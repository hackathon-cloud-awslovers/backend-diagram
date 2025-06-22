FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies
RUN yum install -y graphviz unzip wget tar

# Install D2 binary (update version here!)
ENV D2_VERSION=v0.8.4

RUN wget https://github.com/terrastruct/d2/releases/download/v0.7.0/d2-v0.7.0-linux-amd64.tar.gz -O /tmp/d2.tar.gz \
    && mkdir -p /opt/bin \
    && tar -xzf /tmp/d2.tar.gz -C /opt/bin \
    && chmod +x /opt/bin/d2

# Add D2 to PATH
ENV PATH="/opt/bin:${PATH}"

# Copy app code
COPY diagram_generate_d2.py .
COPY utils.py .

# Set entrypoint
CMD ["diagram_generate_d2.lambda_handler"]
