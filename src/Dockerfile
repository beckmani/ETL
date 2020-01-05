FROM python:3.6

WORKDIR  /usr/src
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=mysecretpassword
ENV POSTGRES_DB=postgres
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8081
CMD ["gunicorn" , "-w", "4", "--timeout", "40", "--log-level", "debug", "-b", "0.0.0.0:8081", "endpoint:app"]
