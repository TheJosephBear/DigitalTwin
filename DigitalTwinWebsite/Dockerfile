FROM python:3.13-slim

WORKDIR /app

# Install netcat for the wait-for-it script
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add a wait script to your Flask app
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

WORKDIR /app/code

CMD ["gunicorn", \
     "-w", "4", \
     "-b", "127.0.0.1:5000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "--capture-output", \
     "App:app"]
# CMD ["sh", "-c", "wait-for-it.sh mongodb:27017 -- gunicorn -w 4 -b 127.0.0.1:5000 app:app"]
# CMD ["flask", "run", "--host=127.0.0.1", "--port=5000", "--debug"]