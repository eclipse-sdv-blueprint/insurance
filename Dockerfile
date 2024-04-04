FROM python:3.9
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /insurance
COPY edge/applications /insurance/applications

COPY edge/proto_build /usr/local/lib/python3.9/proto_build

COPY bin bin

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r /requirements.txt
