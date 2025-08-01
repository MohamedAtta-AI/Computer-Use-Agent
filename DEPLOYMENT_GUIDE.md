# 🚀 Computer Use Agent Backend - Deployment Guide

## 📋 Overview

This guide provides complete instructions for deploying the Computer Use Agent Backend in both development and production environments.

## 🏗️ Project Structure

```
backend/
├── app/                    # Application code
│   ├── api/               # FastAPI route handlers
│   ├── core/              # Integrated agent logic
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── config.py          # Configuration
├── docker-compose.yml     # Development setup
├── docker-compose.prod.yml # Production setup
├── Dockerfile             # Development container
├── Dockerfile.prod        # Production container
├── nginx.conf             # Load balancer config
├── deploy.sh              # Linux/macOS deployment
├── deploy.bat             # Windows deployment
└── env.example            # Environment template
```

## 🔧 Quick Start

### 1. Development Setup

```bash
# Clone and navigate
cd backend

# Set up environment
cp env.example .env
# Edit .env with your values

# Install dependencies
pip install -r requirements.txt

# Run locally
python run.py
```

### 2. Docker Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### 3. Production Deployment

```bash
# Set up production environment
cp env.prod.example .env.prod
# Edit .env.prod with production values

# Deploy (Linux/macOS)
./deploy.sh

# Deploy (Windows)
deploy.bat
```

## 🔑 Required Configuration

### Environment Variables

**Required:**
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `SECRET_KEY` - Long random string for JWT tokens
- `DATABASE_URL` - PostgreSQL connection string

**Optional:**
- `REDIS_URL` - Redis connection (for caching)
- `VNC_HOST/PORT/PASSWORD` - VNC server details
- `DEBUG` - Set to `false` in production

### Database Setup

**Development:**
```bash
DATABASE_URL=sqlite:///./computer_use_agent.db
```

**Production:**
```bash
DATABASE_URL=postgresql://user:password@postgres:5432/computer_use_agent
```

## 🐳 Docker Configuration

### Development (`docker-compose.yml`)

- **Backend**: FastAPI with hot reload
- **PostgreSQL**: Database with health checks
- **Redis**: Caching layer
- **Volumes**: Code mounted for live development

### Production (`docker-compose.prod.yml`)

- **Backend**: Multi-worker FastAPI (3 replicas)
- **PostgreSQL**: Persistent database
- **Redis**: Persistent cache
- **Nginx**: Load balancer with rate limiting
- **Health checks**: All services monitored
- **Resource limits**: CPU and memory constraints

## 📊 Monitoring & Health Checks

### Health Endpoints

- `GET /health` - Application health
- `GET /api/v1/status` - API status
- Docker health checks for all services

### Logs

```bash
# View all logs
docker-compose logs

# Follow backend logs
docker-compose logs -f backend

# Production logs
docker-compose -f docker-compose.prod.yml logs
```

## 🔒 Security Features

### Production Security

- **Non-root containers**: All services run as non-root users
- **Rate limiting**: Nginx rate limiting on API endpoints
- **Security headers**: XSS protection, content type validation
- **Resource limits**: CPU and memory constraints
- **Health checks**: Automatic service monitoring

### SSL/HTTPS

To enable HTTPS:

1. Add SSL certificates to `ssl/` directory
2. Uncomment HTTPS section in `nginx.conf`
3. Update `docker-compose.prod.yml` to mount SSL certificates

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale backend service
docker-compose -f docker-compose.prod.yml up -d --scale backend=5

# Scale with resource limits
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Load Balancing

Nginx automatically load balances between backend instances:
- Round-robin distribution
- Health check integration
- WebSocket support
- Rate limiting per endpoint

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection**
   ```bash
   # Check PostgreSQL status
   docker-compose ps postgres
   
   # Reset database
   docker-compose down -v
   docker-compose up -d
   ```

2. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -ano | findstr :8000
   
   # Change port in .env
   PORT=8001
   ```

3. **Permission Issues**
   ```bash
   # Fix uploads directory
   chmod 755 uploads/
   ```

### Debug Mode

```bash
# Enable debug logging
DEBUG=true

# View detailed logs
docker-compose logs -f backend
```

## 📚 API Documentation

Once deployed, access:
- **Interactive docs**: http://localhost/docs
- **ReDoc**: http://localhost/redoc
- **Health check**: http://localhost/health

## 🔄 Updates & Maintenance

### Updating the Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Database Migrations

```bash
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose exec backend alembic upgrade head
```

## 📞 Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify environment variables
3. Test health endpoints
4. Check resource usage

## 🎯 Best Practices

1. **Environment Variables**: Never commit `.env` files
2. **Secrets**: Use secure secret management in production
3. **Backups**: Regular database backups
4. **Monitoring**: Set up application monitoring
5. **Updates**: Regular security updates
6. **Testing**: Run tests before deployment

---

**Ready to deploy!** 🚀 