# Data Engineering Project: eClipseBord

## Fullstack Solar Eclipse Dashboard on Azure

# Overview

This project implements a complete fullstack application, built and deployed on Microsoft Azure, designed to serve two centuries and more of solar eclipse data through an interactive dashboard. Built as a cloud lab using a FastAPI backend, a Streamlit frontend, Docker containers and Azure App Service, the project turns ~11,900 raw eclipse records into a clean, browsable dashboard with key metrics, charts and a map.

The primary dataset is real data from NASA's eclipse catalog (`solar.csv`), covering solar eclipses from the year -1999 (2000 BCE) to 3000 CE across 15 columns. The data is raw: coordinates are stored as text (`6.0N`), years can be negative for BCE dates, and central path width and duration are missing for partial eclipses. All cleaning happens in one place in the backend rather than being spread across the app.

Every cleaning rule is defined once in the backend's `data_processing.py` rather than duplicated across the app, the data-directory lookup is resolved in exactly one place so the same code runs both locally and in a container, and the backend and frontend are separated into two independent, containerised services.

The project consists of four main parts:

1. **Backend API** (FastAPI) that loads, cleans and serves the eclipse data as JSON endpoints
2. **Exploratory Data Analysis** of the raw dataset before building the app
3. **Frontend Dashboard** (Streamlit) that consumes the API and renders metrics, charts and a map
4. **Containerisation and Cloud Deployment** to Azure App Service via Azure Container Registry

# Objectives

- Design and implement a complete flow from raw data to a cleaned API and an interactive dashboard.
- Separate the application into two independent, containerised services (backend and frontend) that communicate over HTTP.
- Apply software engineering principles: separation of concerns, a DRY code structure and reproducible builds.
- Containerise both services with Docker and orchestrate them locally with Docker Compose.
- Deploy the full stack to the cloud on Azure App Service, using Azure Container Registry to host the images.

# Architecture

The application runs as two containers built from a single `uv` workspace with two packages, `backend` and `frontend`, that share one lockfile but keep their own dependencies. Each service has one responsibility: the backend loads and cleans the data and exposes it as JSON, and the frontend fetches that JSON and renders the dashboard. Shared cleaning logic lives in `backend/src/backend/data_processing.py`, so each rule exists in exactly one place and the API layer stays thin.

The frontend reads the backend's address from the `BACKEND_URL` environment variable, so the exact same image runs both locally (via Docker Compose, where the address is `http://backend:8000`) and in Azure (where it points to the deployed backend app). On Azure App Service, each container declares its port through `WEBSITES_PORT` (8000 for the backend, 8501 for the frontend).

In short, the Streamlit frontend (port 8501) sends HTTP requests to the FastAPI backend (port 8000), using the address in `BACKEND_URL`. The backend reads and cleans `solar.csv` from NASA's eclipse catalog and returns the result as JSON, which the frontend renders as the dashboard.

# Features

## Backend API

A FastAPI service that loads the raw `solar.csv` once (cached), cleans it, and exposes it through JSON endpoints:

The API exposes five endpoints. `GET /` is a health check that confirms the API is alive. `GET /eclipses` returns the cleaned data, with an optional `?limit=N` to cap the number of rows. `GET /eclipses/stats` returns key metrics such as the total count, the time span and the average magnitude. `GET /eclipses/types` returns the count per eclipse type, and `GET /eclipses/by-century` returns the count per century.

The cleaning parses text coordinates into numeric latitude/longitude, extracts the year (handling negative BCE years that standard date parsers reject), and maps the eclipse-type code to a readable name (Partial, Annular, Total, Hybrid).

## Frontend Dashboard

A Streamlit dashboard, **eClipseBord**, that consumes the backend API. It shows key metrics (total eclipses, time span, most common type, average magnitude), a bar chart of eclipses by type, a line chart of eclipses by century, a world map of where eclipses occur, and a raw-data table.

## Containerisation

Both services are containerised with Docker. Each has its own dockerfile under `dockerfiles/`, and `docker-compose.yaml` builds and runs both together locally, wiring the frontend to the backend over an internal Docker network.

## Cloud Deployment

The images are pushed to an Azure Container Registry and run as two Azure App Service web apps (Linux containers). The frontend web app is connected to the backend through the `BACKEND_URL` app setting, and each app declares its container port through `WEBSITES_PORT`.

## Exploratory Data Analysis

The `eda/eda.ipynb` notebook documents a short exploratory analysis of the raw dataset: column types, missing values, the distribution of eclipse types, the time span, and the magnitude distribution, enough to understand the data before building the app, with the focus kept on the cloud infrastructure.

## Code Quality

- All data-cleaning logic is collected in `backend/src/backend/data_processing.py`. The API layer stays thin and imports what it needs rather than duplicating it.
- Constants such as the eclipse-type mapping live in one place (`constants.py`), and the data-directory path is resolved once so the same code runs locally and in the container.
- All comments and docstrings are written in English. Data values, eclipse types and coordinates remain in their source form.

# Installation & Usage

## Essential Requirements

- [uv](https://docs.astral.sh/uv/) and Docker Desktop
- An Azure account (Azure for Students works) with the Azure CLI (`az`) for deployment
- The dataset `solar.csv` (included under `data/`)

# 1. Run locally

## With Docker Compose:

```bash
docker compose up --build
```

- Frontend: http://localhost:8501
- Backend:  http://localhost:8000/docs

## Or run the packages directly (for development):

```bash
# Terminal 1 - backend
cd backend
uv sync
uv run uvicorn backend.api:app --reload

# Terminal 2 - frontend
cd frontend
uv sync
BACKEND_URL=http://127.0.0.1:8000 uv run streamlit run src/frontend/dashboard.py
```

# 2. Deploy to Azure

## Build and push the images:

Create a resource group and an Azure Container Registry, set your registry's login server on the two `image:` lines in `docker-compose.yaml`, then build and push:

```bash
az acr login --name <login_server>
docker compose build
docker compose push
```

## Create and configure the web apps:

Create two Linux container web apps (one per image) in Azure App Service, pointing each at your registry. Then set the app settings: `WEBSITES_PORT` = `8000` on the backend, and `WEBSITES_PORT` = `8501` plus `BACKEND_URL` = the backend app's public URL on the frontend.

# 3. Verification

After execution, verify the following:

- **Local**: `docker compose up --build` starts both containers, the dashboard renders at `localhost:8501`, and the API responds at `localhost:8000/docs`.
- **Registry**: `az acr repository list --name <login_server> -o table` shows the `backend` and `frontend` images.
- **Backend (Azure)**: `https://<backend-host>/docs` shows the FastAPI docs with all endpoints.
- **Frontend (Azure)**: `https://<frontend-host>` shows the eClipseBord dashboard with metrics, charts, map and table, loading data from the deployed backend.