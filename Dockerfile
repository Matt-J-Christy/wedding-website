FROM python:3.9-slim
COPY requirements.in ./

SHELL ["/bin/bash", "-c"]

# install dependencies
RUN pip install -r ./requirements.in

LABEL Maintainer='Matt Christy'

COPY app/ ./app
COPY static ./static
COPY main.py ./

# run the application
CMD python main.py
