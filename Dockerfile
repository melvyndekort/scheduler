FROM python:3.9-rc-alpine

RUN pip install --upgrade --no-cache-dir pip
RUN pip install --no-cache-dir schedule docker

COPY run.py /

CMD ["python", "-u", "/run.py"]
