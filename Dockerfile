FROM python:3.7-stretch as builder
WORKDIR /install
COPY /requirements.txt /tmp/
RUN pip install --user -r /tmp/requirements.txt

FROM python:3.7-alpine as base
COPY --from=builder /root/.local /root/.local
COPY app /app
WORKDIR /app

ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT ["python", "./app.py"]
CMD ["scrobble", "data/playlist/sample.txt"]