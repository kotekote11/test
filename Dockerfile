FROM python:3.12
WORKDIR /app
COPY . /app
RUN pip install requests
RUN pip install beautifulsoup4
CMD ["python", "main.py"]
