FROM python:3-alpine

RUN pip install --upgrade --no-cache-dir pip
RUN pip install --no-cache-dir schedule docker flask six

COPY run.py /

CMD ["python", "-u", "/run.py"]
