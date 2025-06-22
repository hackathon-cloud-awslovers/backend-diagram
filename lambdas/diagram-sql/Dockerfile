# Dockerfile
FROM public.ecr.aws/lambda/python:3.9

# Instala Graphviz (necesario si decides usar dot en lugar de PlantUML)
RUN yum install -y graphviz

# Copia e instala dependencias Python
COPY requirements.txt ./
RUN pip install -r requirements.txt -t .

# Copia el código de la Lambda
COPY diagram/ ./diagram/

# Define el handler
CMD ["diagram/diagram_build.lambda_handler"]
