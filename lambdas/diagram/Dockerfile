FROM public.ecr.aws/lambda/python:3.9

# Instalar dependencias del sistema
RUN yum install -y graphviz unzip wget tar gzip && yum clean all

# Instalar D2 binary (puedes cambiar la versión fácilmente)
ENV D2_VERSION=v0.7.0

RUN wget https://github.com/terrastruct/d2/releases/download/${D2_VERSION}/d2-${D2_VERSION}-linux-amd64.tar.gz -O /tmp/d2.tar.gz \
    && mkdir -p /opt/bin \
    && tar -xzf /tmp/d2.tar.gz -C /opt/bin \
    && chmod +x /opt/bin/d2-v0.7.0/bin/d2

# Agregar D2 al PATH
ENV PATH="/opt/bin:${PATH}"

# Copiar código de la app (ajusta si tienes requirements.txt)
COPY diagram_generate_d2.py .
COPY utils.py .

# Instalar requirements si es necesario
# RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Comando de entrada de Lambda
CMD ["diagram_generate_d2.lambda_handler"]
