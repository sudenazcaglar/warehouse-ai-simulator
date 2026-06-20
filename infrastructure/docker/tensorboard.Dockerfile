FROM python:3.11-slim

RUN pip install --no-cache-dir tensorboard==2.17.1

WORKDIR /workspace

EXPOSE 6006

CMD ["tensorboard", "--logdir", "/workspace/training", "--host", "0.0.0.0", "--port", "6006"]
