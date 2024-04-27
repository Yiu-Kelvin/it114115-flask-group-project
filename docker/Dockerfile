FROM python:3.9.18-slim-bookworm

ENV PIP_DEFAULT_TIMEOUT=100
ENV CC=clang
ENV CXX=clang++
# ENV FLASK_APP=~/workspace/it114115-flask-project-individual/run.py
RUN apt-get update && apt-get install -y gcc clang cmake g++

RUN useradd -m --shell /bin/bash flaskuser
RUN chmod -R 755 /home/flaskuser
WORKDIR /workspace
COPY --chmod=0755 requirements.txt /tmp/pip-tmp/
RUN chown flaskuser:flaskuser /tmp/pip-tmp/requirements.txt
USER flaskuser
RUN pip3 --disable-pip-version-check --no-cache-dir install --use-pep517 -r /tmp/pip-tmp/requirements.txt


# CMD ["./start.sh"]
