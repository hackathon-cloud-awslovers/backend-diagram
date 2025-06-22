FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies (Graphviz)
RUN yum install -y graphviz

# Install system dependencies
RUN yum -y install unzip wget

# Install D2 binary
RUN wget https://github.com/terrastruct/d2/releases/latest/download/d2-linux-amd64.tar.gz -O /tmp/d2.tar.gz \
    && mkdir -p /opt/bin \
    && tar -xzf /tmp/d2.tar.gz -C /opt/bin \
    && chmod +x /opt/bin/d2

# Add to PATH
ENV PATH="/opt/bin:${PATH}"

# Copy requirements (if you have utils.py deps)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app code
COPY diagram_generate_d2.py .
COPY utils.py .

# Set entrypoint
CMD ["diagram_generate_d2.lambda_handler"]
