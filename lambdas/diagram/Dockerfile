FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies (Graphviz)
RUN yum install -y graphviz

# Install python dependencies (diagrams)
COPY requirements.txt ./
RUN pip install -r requirements.txt -t .

# Set the CMD to your handler
CMD ["diagram/diagram_build.lambda_handler"]
