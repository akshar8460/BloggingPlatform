FROM python:3.9

WORKDIR /code

COPY . .

RUN pip install --upgrade -r /code/requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]