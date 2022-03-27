FROM python:bullseye
COPY . /app
RUN apt update
RUN apt install -y build-essential gcc g++ autoconf automake libtool bison flex gettext
RUN pip install -r /app/requirements.txt
CMD python /app/manage.py runserver 8000
ENV PYTHONUNBUFFERED=1