# Utiliza la imagen base de Ubuntu 24.04
FROM ubuntu:24.04

# Establece el directorio de trabajo
WORKDIR /tmp

# Agrega la ruta de protoc al PATH
ENV PATH="$PATH:/opt/protoc-3.20.0/bin"

# Instala dependencias mínimas y herramientas adicionales
RUN apt-get update && apt-get install -y \
    gnupg \
    curl \
    tar \
    vim \
    wget \
    unzip \
    git \
    apt-transport-https \
    software-properties-common

# Añade la llave de Bazel y su repositorio
RUN curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > /usr/share/keyrings/bazel-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list

# Instala Bazel
RUN apt-get update && apt-get install -y bazel

# Clona el repositorio de protobuf y compila con Bazel
RUN git clone https://github.com/protocolbuffers/protobuf.git && \
    cd protobuf && \
    git submodule update --init --recursive && \
    bazel build :protoc :protobuf && \
    cp bazel-bin/protoc /usr/local/bin

# Instala Protobuf3
RUN wget --no-check-certificate https://github.com/protocolbuffers/protobuf/releases/download/v28.2/protoc-28.2-linux-x86_64.zip && \
    unzip protoc-28.2-linux-x86_64.zip && \
    mkdir -p /opt/protoc-28.2 && \
    mv bin include /opt/protoc-28.2 && \
    rm -rf protoc-28.2-linux-x86_64.zip readme.txt

WORKDIR /
