FROM public.ecr.aws/lambda/python:3.9

# Instalar dependencias del sistema necesarias
RUN yum install -y graphviz unzip wget tar gzip && yum clean all

# Definir versión de D2
ENV D2_VERSION=v0.7.0

# Descargar y descomprimir D2
RUN wget https://github.com/terrastruct/d2/releases/download/${D2_VERSION}/d2-${D2_VERSION}-linux-amd64.tar.gz -O /tmp/d2.tar.gz \
    && mkdir -p /opt/bin \
    && tar -xzf /tmp/d2.tar.gz -C /opt/bin --strip-components=2 d2-${D2_VERSION}/bin/d2 \
    && chmod +x /opt/bin/d2

# Asegurar que D2 está en PATH
ENV PATH="/opt/bin:${PATH}"

# Copiar el código de la app
COPY diagram_generate_d2.py .
COPY utils.py .

# Comando de entrada de Lambda
CMD ["diagram_generate_d2.lambda_handler"]
