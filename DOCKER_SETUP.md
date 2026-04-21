# Docker Setup Guide for DevOps Gamification Dashboard

This guide will help you run the DevOps Gamification Dashboard in Docker Desktop with MongoDB.

## Prerequisites

1. **Docker Desktop** installed on your machine
   - Download from: https://www.docker.com/products/docker-desktop
   - Make sure Docker Desktop is running

2. **MongoDB Connection Details**
   - MongoDB URI (host and port)
   - Database name
   - Username and password
   - Authentication source

3. **Your API Tokens**
   - TeamBook Bearer Token
   - DataSight Bearer Token

## Quick Start - Using Docker CLI

1. **Navigate to project directory**
   ```bash
   cd /Users/kritikapandey/Desktop/Gamification
   ```

2. **Build the Docker image**
   ```bash
   docker build -t devops-gamification:latest .
   ```

3. **Run the container with MongoDB configuration**
   ```bash
   docker run -d \
     --name devops-gamification \
     -p 8501:8501 \
     -e MONGODB_URI="mongodb://your-mongodb-host:27017" \
     -e MONGODB_DATABASE="gamification" \
     -e MONGODB_USERNAME="your_mongodb_username" \
     -e MONGODB_PASSWORD="your_mongodb_password" \
     -e MONGODB_AUTH_SOURCE="admin" \
     -e TEAMBOOK_BEARER_TOKEN="your_teambook_token" \
     -e DATASIGHT_BEARER_TOKEN="your_datasight_token" \
     -e SERVICE_LINE_ID=449 \
     -v $(pwd)/logs:/app/logs \
     devops-gamification:latest
   ```

4. **Access the dashboard**
   - Open your browser and go to: http://localhost:8501

5. **View logs**
   ```bash
   docker logs -f devops-gamification
   ```

6. **Stop the container**
   ```bash
   docker stop devops-gamification
   docker rm devops-gamification
   ```

## Using Docker Desktop GUI

### Building the Image

1. Open **Docker Desktop**
2. Click on **Images** in the left sidebar
3. Click **Build** button
4. Select the `Dockerfile` from: `/Users/kritikapandey/Desktop/Gamification`
5. Give it a name: `devops-gamification`
6. Click **Build**

### Running the Container

1. In Docker Desktop, go to **Images**
2. Find `devops-gamification` image
3. Click the **Run** button (▶️)
4. Click **Optional Settings** to expand configuration:
   
   **Container Name:**
   ```
   devops-gamification
   ```
   
   **Ports:**
   - Host Port: `8501`
   - Container Port: `8501`
   
   **Volumes:**
   - Host Path: `/Users/kritikapandey/Desktop/Gamification/logs`
   - Container Path: `/app/logs`
   
   **Environment Variables (REQUIRED):**
   
   **MongoDB Configuration:**
   - `MONGODB_URI` = `mongodb://your-mongodb-host:27017`
   - `MONGODB_DATABASE` = `gamification`
   - `MONGODB_USERNAME` = `your_mongodb_username`
   - `MONGODB_PASSWORD` = `your_mongodb_password`
   - `MONGODB_AUTH_SOURCE` = `admin`
   - `USE_MONGODB` = `true`
   
   **API Tokens:**
   - `TEAMBOOK_BEARER_TOKEN` = `your_teambook_token`
   - `DATASIGHT_BEARER_TOKEN` = `your_datasight_token`
   
   **Application Settings:**
   - `SERVICE_LINE_ID` = `449`
   - `MAX_WEEKS_TO_KEEP` = `5`
   - `AUTO_REFRESH_ENABLED` = `false`
   - `REFRESH_INTERVAL_HOURS` = `168`

5. Click **Run**

6. Access the dashboard at: http://localhost:8501

### Managing the Container

1. **View Running Containers:**
   - Click **Containers** in Docker Desktop sidebar
   - You'll see `devops-gamification-dashboard` running

2. **View Logs:**
   - Click on the container name
   - Click **Logs** tab

3. **Stop Container:**
   - Click the **Stop** button (⏸️)

4. **Start Container:**
   - Click the **Start** button (▶️)

5. **Delete Container:**
   - Stop the container first
   - Click the **Delete** button (🗑️)

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` | **Yes** |
| `MONGODB_DATABASE` | MongoDB database name | `gamification` | **Yes** |
| `MONGODB_USERNAME` | MongoDB username | `admin` | **Yes** |
| `MONGODB_PASSWORD` | MongoDB password | `changeme` | **Yes** |
| `MONGODB_AUTH_SOURCE` | MongoDB auth source | `admin` | No |
| `USE_MONGODB` | Enable MongoDB | `true` | No |
| `TEAMBOOK_BEARER_TOKEN` | TeamBook API token | - | **Yes** |
| `DATASIGHT_BEARER_TOKEN` | DataSight API token | - | **Yes** |
| `SERVICE_LINE_ID` | Service line identifier | `449` | No |
| `MAX_WEEKS_TO_KEEP` | Data retention period | `5` | No |
| `AUTO_REFRESH_ENABLED` | Enable auto-refresh | `false` | No |
| `REFRESH_INTERVAL_HOURS` | Refresh interval | `168` | No |

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs devops-gamification

# Or in Docker Desktop: Containers → Click container → Logs tab
```

**Common issues:**
- Missing MongoDB credentials
- MongoDB server not accessible
- Invalid MongoDB URI format
- Missing API tokens

### MongoDB connection errors
```bash
# Test MongoDB connection from your host
mongosh "mongodb://your-mongodb-host:27017" -u your_username -p your_password

# Check if MongoDB is accessible from Docker
docker run --rm mongo:7.0 mongosh "mongodb://your-mongodb-host:27017" -u your_username -p your_password
```

**Solutions:**
- Verify MongoDB URI is correct
- Check MongoDB username/password
- Ensure MongoDB server is running and accessible
- Check network connectivity
- Verify authentication source is correct

### Port already in use
```bash
# Use a different port
docker run -p 8502:8501 ...
# Then access at http://localhost:8502
```

### Can't access dashboard
1. Check container is running: `docker ps`
2. Check port mapping: `docker port devops-gamification`
3. Try: http://localhost:8501 or http://127.0.0.1:8501
4. Check firewall settings
5. Verify container health: `docker inspect devops-gamification | grep Health`

### Application errors
```bash
# View detailed logs
docker logs -f devops-gamification

# Check environment variables
docker inspect devops-gamification | grep -A 20 Env
```

## Updating the Application

1. **Stop and remove old container**
   ```bash
   docker stop devops-gamification
   docker rm devops-gamification
   ```

2. **Pull latest code**
   ```bash
   cd /Users/kritikapandey/Desktop/Gamification
   git pull
   ```

3. **Rebuild image**
   ```bash
   docker build --no-cache -t devops-gamification:latest .
   ```

4. **Run new container**
   ```bash
   # Use the same docker run command from Quick Start section
   docker run -d \
     --name devops-gamification \
     -p 8501:8501 \
     -e MONGODB_URI="mongodb://your-mongodb-host:27017" \
     -e MONGODB_DATABASE="gamification" \
     -e MONGODB_USERNAME="your_mongodb_username" \
     -e MONGODB_PASSWORD="your_mongodb_password" \
     -e MONGODB_AUTH_SOURCE="admin" \
     -e TEAMBOOK_BEARER_TOKEN="your_teambook_token" \
     -e DATASIGHT_BEARER_TOKEN="your_datasight_token" \
     -e SERVICE_LINE_ID=449 \
     -v $(pwd)/logs:/app/logs \
     devops-gamification:latest
   ```

## Health Check

The container includes a health check that runs every 30 seconds:
```bash
# Check container health
docker ps
# Look for "healthy" status

# Or in Docker Desktop: Containers → Check status indicator
```

## Data Persistence

Application logs are persisted in:
- `./logs/` - Application logs (mounted as volume)

**Note:** All data is stored in MongoDB, not in local files. Make sure your MongoDB instance has proper backup and persistence configured.

## Security Notes

1. **Never commit MongoDB credentials** to version control
2. **Use strong MongoDB passwords**
3. **Use secrets management** for production deployments
4. **Restrict MongoDB network access** to trusted sources only
5. **Enable MongoDB authentication** and use SSL/TLS
6. **Restrict port 8501** if exposing to network
7. **Keep Docker Desktop updated**
8. **Regularly update base images**
9. **Store API tokens securely** - never hardcode in Dockerfile

## MongoDB Connection Examples

### Local MongoDB
```bash
-e MONGODB_URI="mongodb://localhost:27017"
```

### MongoDB Atlas (Cloud)
```bash
-e MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
```

### MongoDB with Authentication
```bash
-e MONGODB_URI="mongodb://username:password@host:27017/gamification?authSource=admin"
```

### MongoDB Replica Set
```bash
-e MONGODB_URI="mongodb://host1:27017,host2:27017,host3:27017/gamification?replicaSet=rs0"
```

## Support

For issues or questions:
1. Check container logs: `docker logs devops-gamification`
2. Verify MongoDB connection
3. Review this documentation
4. Check Docker Desktop diagnostics
5. Consult the main README.md
