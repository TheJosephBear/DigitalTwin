# Digital twin - Server
This repository contains the Flask server that powers the main functionality of the Digital Twin project. The server is responsible for hosting Unity builds and providing API endpoints for data management.
## Running the application
Run the app.py in visual studio code or type the following command in your terminal:
```bash
python app.py
```
## Links to associated projects
[Digital twin - client](https://github.com/TheJosephBear/DigitalTwin-Client) <br>-
[Digital twin - editor](https://github.com/TheJosephBear/DigitalTwin-UnityProjectEditor) <br>
[Digital twin - viewer](https://github.com/TheJosephBear/DigitalTwin-UnityProjectViewer) <br>

## Production Deployment

1. **Create `.env.production` file** in the project root:
   ```bash
   MONGO_USERNAME='username'
   MONGO_PASSWORD='password'
   MONGO_DBNAME='digitalTwin'
   MONGO_URI=mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@mongodb:27017/
   ```

2. **Deploy using production compose file**:
   ```bash
   docker-compose -f docker-compose.yml --env-file .env.production up --build -d
   ```