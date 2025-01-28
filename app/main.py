from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = FastAPI()

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 'Total number of HTTP requests', ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'http_request_latency_seconds', 'Latency of HTTP requests', ['method', 'endpoint']
)

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Update Prometheus metrics
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, http_status=response.status_code).inc()
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(process_time)

    return response

@app.get("/")
async def read_root():
    return {"message": "Hello, world!"}

@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)