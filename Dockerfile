FROM python:3.7.2-slim

RUN mkdir /app

# For good caching, run reqs.txt
COPY . /app
RUN pip3 install -r app/requirements.txt

WORKDIR /app

# Containers have no public IP address by default
# Remember to ufw allow port 8000
# Forward host port 80 -> container port
EXPOSE 8000

CMD ["python3", "__ini__.py"]













