FROM python:3
LABEL maintainer="michael@brunton-spall.co.uk"

WORKDIR /usr/src/app

COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

RUN ["python", "-m", "unittest", "discover"]

#PRod build
FROM python:3

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
ENV FLASK_APP=app.py CLIENT_ID="client" CLIENT_SECRET="secret"
CMD [ "flask", "run", "--host=0.0.0.0" ]
