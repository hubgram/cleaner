FROM python:3

WORKDIR /usr/src/app
COPY . .
RUN python -m pip install -U pip wheel setuptools
RUN python -m pip install -r requirements.txt
CMD ["python", "main.py"]
