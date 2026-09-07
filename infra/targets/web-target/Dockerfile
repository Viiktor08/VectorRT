# Web target de laboratorio — 10.10.10.11
FROM python:3.12-slim

WORKDIR /srv
RUN echo "<h1>VectorRT lab — web target</h1>" > index.html

EXPOSE 8080
CMD ["python", "-m", "http.server", "8080"]
