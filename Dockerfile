FROM python:3.8

# Create a virtualenv for the application dependencies.
# # If you want to use Python 2, use the -p python2.7 flag.
ADD requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt
ADD . /app
CMD cd app && gunicorn -b :8080 UsersMicroService.wsgi:application
