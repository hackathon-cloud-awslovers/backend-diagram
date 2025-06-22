FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies (Graphviz)
RUN yum install -y graphviz

# Install python dependencies (diagrams)
COPY requirements.txt ./
RUN pip install -r requirements.txt -t .

# Install D2
RUN yum install -y tar gzip
RUN curl -L -o d2.tar.gz https://github.com/terrastruct/d2/releases/download/v0.6.6/d2-linux-amd64.tar.gz
RUN tar -xzf d2.tar.gz && chmod +x d2 && mv d2 /usr/local/bin/d2

# Set the CMD to your handler
CMD ["diagram/diagram_build.lambda_handler"]
