# Docker Quick Start - DevOps Gamification Dashboard

## 🚀 One-Command Setup

### Build the Image
```bash
cd /Users/kritikapandey/Desktop/Gamification
docker build -t devops-gamification:latest .
```

### Run the Container
```bash
docker run -d \
  --name devops-gamification \
  -p 8501:8501 \
  -e MONGODB_URI="mongodb://YOUR_MONGODB_HOST:27017" \
  -e MONGODB_DATABASE="gamification" \
  -e MONGODB_USERNAME="YOUR_USERNAME" \
  -e MONGODB_PASSWORD="YOUR_PASSWORD" \
  -e MONGODB_AUTH_SOURCE="admin" \
  -e TEAMBOOK_BEARER_TOKEN="YOUR_TEAMBOOK_TOKEN" \
  -e DATASIGHT_BEARER_TOKEN="YOUR_DATASIGHT_TOKEN" \
  -v $(pwd)/logs:/app/logs \
  devops-gamification:latest
```

### Access Dashboard
Open browser: **http://localhost:8501**

---

## 📝 Required Environment Variables

Replace these values before running:

| Variable | Replace With |
|----------|--------------|
| `YOUR_MONGODB_HOST` | Your MongoDB server hostname/IP |
| `YOUR_USERNAME` | Your MongoDB username |
| `YOUR_PASSWORD` | Your MongoDB password |
| `YOUR_TEAMBOOK_TOKEN` | Your TeamBook API token |
| `YOUR_DATASIGHT_TOKEN` | Your DataSight API token |

---

## 🛠️ Common Commands

### View Logs
```bash
docker logs -f devops-gamification
```

### Stop Container
```bash
docker stop devops-gamification
```

### Start Container
```bash
docker start devops-gamification
```

### Restart Container
```bash
docker restart devops-gamification
```

### Remove Container
```bash
docker stop devops-gamification
docker rm devops-gamification
```

### Check Container Status
```bash
docker ps
```

### View Container Details
```bash
docker inspect devops-gamification
```

---

## 🔄 Update Application

```bash
# Stop and remove old container
docker stop devops-gamification
docker rm devops-gamification

# Rebuild image
docker build --no-cache -t devops-gamification:latest .

# Run new container (use the run command from above)
```

---

## 🐛 Troubleshooting

### Check if container is running
```bash
docker ps | grep devops-gamification
```

### View error logs
```bash
docker logs devops-gamification
```

### Test MongoDB connection
```bash
mongosh "mongodb://YOUR_MONGODB_HOST:27017" -u YOUR_USERNAME -p YOUR_PASSWORD
```

### Check environment variables
```bash
docker inspect devops-gamification | grep -A 20 Env
```

---

## 📱 Docker Desktop Steps

1. **Build Image:**
   - Open Docker Desktop
   - Images → Build
   - Select Dockerfile location
   - Name: `devops-gamification`
   - Click Build

2. **Run Container:**
   - Images → Find `devops-gamification`
   - Click Run (▶️)
   - Optional Settings:
     - Container name: `devops-gamification`
     - Port: `8501:8501`
     - Add all environment variables
   - Click Run

3. **Access:**
   - Open http://localhost:8501

---

## ⚠️ Important Notes

- ✅ MongoDB must be running and accessible
- ✅ Use strong passwords for MongoDB
- ✅ Never commit credentials to git
- ✅ All data is stored in MongoDB (not local files)
- ✅ Logs are saved in `./logs/` directory

---

For detailed documentation, see **DOCKER_SETUP.md**
