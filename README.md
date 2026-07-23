# Digital twin - Server
This repository contains the Flask server that powers the main functionality of the Digital Twin project. The server is responsible for hosting Unity builds and providing API endpoints for data management.

## Running the application locally
Run the start scripts `run.bat`, `run.ps1` or `run.sh`, depending on your shell.
Or you can run the App.py in Visual Studio Code or type the following command in your terminal:
```bash
cd DigitalTwinWebsite/code
python App.py --local
```

The application expects `.env.local` file like in `env.example`.

## Links to associated projects
[Digital twin - client](https://github.com/TheJosephBear/DigitalTwin-Client) <br>-
[Digital twin - editor](https://github.com/TheJosephBear/DigitalTwin-UnityProjectEditor) <br>
[Digital twin - viewer](https://github.com/TheJosephBear/DigitalTwin-UnityProjectViewer) <br>

## Production Deployment

1. **Create `.env` file** in the project root:
   ```bash
   MONGO_USERNAME='username'
   MONGO_PASSWORD='password'
   MONGO_DBNAME='digitalTwin'
   MONGO_URI=mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@mongodb:27017/
   SECRET_KEY='secret'
   LOG_LEVEL='INFO'
   ```

2. **Deploy using production compose file**:
   ```bash
   docker-compose up --build -d
   ```
   Note: `.env` file is implicit, for specifying use `--env-file .env`

To only refresh the Flask container without touching MongoDB, run:

```bash
docker-compose rm -fs flask
docker-compose up -d --build --no-deps flask
```

To follow live logs for the Flask container, run:

```bash
docker-compose logs -f flask
```
