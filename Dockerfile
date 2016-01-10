FROM python:2.7

RUN mkdir /code
WORKDIR /code
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . .
# EXPOSE
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
