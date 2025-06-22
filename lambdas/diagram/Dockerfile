FROM public.ecr.aws/lambda/nodejs18.x

# Instalar herramientas necesarias (tar, wget, unzip, etc.)
RUN yum install -y tar gzip wget unzip && yum clean all

# Variables de versión de D2
ENV D2_VERSION=v0.8.4

# Descargar D2 y preparar en /opt/bin
RUN wget https://github.com/terrastruct/d2/releases/download/${D2_VERSION}/d2-${D2_VERSION}-linux-amd64.tar.gz -O /tmp/d2.tar.gz \
    && mkdir -p /opt/bin \
    && tar -xzf /tmp/d2.tar.gz -C /opt/bin \
    && chmod +x /opt/bin/d2

# Agregar /opt/bin al PATH
ENV PATH="/opt/bin:${PATH}"

# Copiar código de la Lambda
COPY . ${LAMBDA_TASK_ROOT}

# Instalar dependencias (si usas npm)
RUN npm install

# Comando por defecto
CMD [ "index.handler" ]
