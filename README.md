# AlertingSystem

A Python-based alerting system designed for real-time monitoring, notification, and visualization. This project combines a FastAPI backend with a Streamlit frontend, supporting customizable alerting and an interactive dashboard. The system is ideal for infrastructure monitoring, application health checks, and custom alert workflows.

## Features

- **Real-Time Monitoring:** Continuously checks configurable metrics or events.
- **Customizable Alerts:** Supports multiple notification channels.
- **Web Dashboard:** Visualizes alerts and system status via Streamlit.
- **REST API:** FastAPI backend for integration and automation.
- **Configurable Database:** Uses SQLite by default; easily switchable.

## Tech Stack

- **Python** (primary language)
- **FastAPI** (backend API)
- **Streamlit** (frontend dashboard)
- **SQLite** (default database)
- **uv** (dependency management)
- **Uvicorn** (ASGI server)

## Quickstart

### 1. Install Dependencies

> **Note:** Requires [uv](https://github.com/astral-sh/uv) (next-gen Python package/dependency manager).  
> If you don't have `uv`, install it first:
>
> ```bash
> pip install uv
> ```

1. **Set Up Python Virtual Environment:**

    ```bash
    uv venv
    ```

2. **Activate the Virtual Environment:**

    - On Windows:
      ```bash
      .venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source .venv/bin/activate
      ```

3. **Sync and Install Python Dependencies:**

    ```bash
    uv sync
    ```

4. **Set Up Environment Variables:**

    - Create a `.env` file in the root directory.
    - Add this line, setting the path for your SQLite database:
      ```
      DB_URL=sqlite:///path/to/your/database.db
      ```

---

### 2. Start FastAPI Backend

Open a terminal and run:

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

### 3. Start Streamlit Frontend

In another terminal, run:

```bash
cd front_end
streamlit run app.py
```

---

## Directory Structure

```
AlertingSystem/
│
├── api/           # FastAPI backend code
├── front_end/     # Streamlit frontend code
├── .env           # Environment variables (DB_URL, etc.)
├── requirements.txt
└── README.md
```

## Configuration

- **Backend:** Configure alert logic, channels, and monitoring in `api/`.
- **Frontend:** Customize dashboard in `front_end/app.py`.
- **Database:** Default is SQLite; `DB_URL` can point to any supported SQLAlchemy database.

## Contributing

Contributions are welcome!
- Fork the repo
- Create a feature branch
- Submit a pull request

**Maintainer:** [JogannagariSaiCharanReddy](https://github.com/JogannagariSaiCharanReddy)
