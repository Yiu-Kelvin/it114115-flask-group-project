FROM python:3.9.18-slim-bookworm

ENV PIP_DEFAULT_TIMEOUT=100
ENV CC=clang
ENV CXX=clang++
# ENV FLASK_APP=~/workspace/it114115-flask-project-individual/run.py
RUN apt-get update && apt-get install -y gcc clang cmake g++
COPY requirements.txt /tmp/pip-tmp/
COPY --from=flaskapp . /workspace
WORKDIR /workspace
RUN pip3 --disable-pip-version-check --no-cache-dir install --use-pep517 -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp

CMD ["./start.sh"]
