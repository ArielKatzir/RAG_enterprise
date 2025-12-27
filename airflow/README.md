# Airflow Setup

## Quick Start

### 1. Initialize Airflow (first time only)
```bash
cd airflow
docker-compose up airflow-init
```

Wait for the message: "airflow-init-1 exited with code 0"

### 2. Start Airflow
```bash
docker-compose up -d
```

This starts:
- Airflow Webserver (UI): http://localhost:8080
- Airflow Scheduler (runs DAGs)
- PostgreSQL (metadata database)

### 3. Access the UI
- URL: http://localhost:8080
- Username: `airflow`
- Password: `airflow`

### 4. Stop Airflow
```bash
docker-compose down
```

### 5. Clean up (removes all data)
```bash
docker-compose down --volumes --remove-orphans
```

---

## Directory Structure

```
airflow/
├── dags/              # Put your DAG files here
├── logs/              # Airflow task logs
├── plugins/           # Custom operators/hooks
├── config/            # Configuration files
├── docker-compose.yaml
└── .env
```

---

## Adding DAGs

1. Create a Python file in `airflow/dags/`
2. The file will be automatically detected (may take ~30 seconds)
3. View it in the UI at http://localhost:8080

---

## Installed Packages

The Airflow image includes:
- openai
- faiss-cpu
- pandas
- pydantic
- pypdf2

To add more packages, edit `_PIP_ADDITIONAL_REQUIREMENTS` in `docker-compose.yaml`

---

## Accessing Your Code

Your project directories are mounted in the container:
- `/opt/airflow/data` → `../data/`
- `/opt/airflow/src` → `../src/`
- `/opt/airflow/dags` → `./dags/`

---

## Troubleshooting

### Permission errors
```bash
sudo chown -R $(id -u):$(id -g) ./dags ./logs ./plugins
```

### Check logs
```bash
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
```

### Restart services
```bash
docker-compose restart
```
