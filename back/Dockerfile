FROM python:3.11.0

WORKDIR /app 
EXPOSE 8000 
COPY requirements.txt ./
RUN pip install wheel setuptools pip --upgrade
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

