FROM python:alpine
COPY . /app
RUN apk update
RUN apk add make automake gcc g++ subversion python3-dev
RUN pip install -r /app/requirements.txt
CMD python /app/manage.py runserver 8000