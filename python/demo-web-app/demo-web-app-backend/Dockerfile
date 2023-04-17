FROM python:3-alpine

WORKDIR /usr/src/asyncio-icap-client

COPY --from=asyncio-icap-client . .

RUN pip install --no-cache-dir .

WORKDIR /usr/src/demo-web-app-backend

COPY . .

RUN pip install --no-cache-dir . && \
    pip install --no-cache-dir uvicorn

CMD [ "uvicorn", "--host", "0.0.0.0", "--port", "80", "demo_web_app_backend.app:app" ]
