FROM python:3.8.2-alpine
WORKDIR /
COPY . /
RUN  apk add --no-cache gcc musl-dev linux-headers python3-dev
RUN pip3 install --upgrade pip
RUN pip3 install flask requests  redis elasticsearch continuous_threading flask_cors 
EXPOSE 5000
CMD ["python3","minute.py"]