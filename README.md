# ✈️ Flight Punctuality Analytics

A proof-of-concept modern data stack that analyses the punctuality of flights at Swedish airports. Data is extracted from the Swedavia FlightInfo API and Wikipedia, loaded into Snowflake, transformed with dbt, orchestrated with Dagster and visualised in a Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-ipynb-F37626?logo=jupyter&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white)
![dlt](https://img.shields.io/badge/dlt-data%20load%20tool-C6D300)
![dbt](https://img.shields.io/badge/dbt-FF694B?logo=dbt&logoColor=white)
![Dagster](https://img.shields.io/badge/Dagster-4F43DD?logo=dagster&logoColor=white)
![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?logo=duckdb&logoColor=black)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![uv](https://img.shields.io/badge/uv-DE5FE9?logo=uv&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?logo=docker&logoColor=white)
![Azure](https://img.shields.io/badge/Azure-Container%20Registry-0078D4)
![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)
![API](https://img.shields.io/badge/API-REST-009688)
![SQL](https://img.shields.io/badge/SQL-4479A1?logo=postgresql&logoColor=white)
![Jinja](https://img.shields.io/badge/Jinja-B41717?logo=jinja&logoColor=white)
![YAML](https://img.shields.io/badge/YAML-CB171E?logo=yaml&logoColor=white)
![TOML](https://img.shields.io/badge/TOML-9C4121?logo=toml&logoColor=white)

---

## Table of Contents

1. [Background and Purpose](#1-background-and-purpose)
2. [Architecture](#2-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Getting Started](#5-getting-started)
6. [Usage](#6-usage)
7. [Data Model](#7-data-model)
8. [Testing and Data Quality](#8-testing-and-data-quality)
9. [Deployment (Azure)](#9-deployment-azure)
10. [Known Limitations and Future Work](#10-known-limitations-and-future-work)
11. [Authors and Data Sources](#11-authors-and-data-sources)

---

## 1. Background and Purpose

This project was built as a two-week sprint by a team of data engineers working for a hypothetical Swedish airport authority. The goal is to deliver a proof of concept (PoC) that helps business stakeholders answer questions such as:

- How many arrivals and departures are delayed at Swedish airports?
- Which **airlines** have the most delays?
- Which **airports** are the least punctual?
- How do delays vary by **date**?

The pipeline extracts flight data covering the **past three days** (including the extraction date) for **all available airports in Swedavia data**, and makes it available in an interactive dashboard.

---

## 2. Architecture

![Project Architecture](docs/architecture.png)

| Step | Description |
|------|-------------|
| **Extract & Load** | `dlt` pulls arrivals and departures from the Swedavia FlightInfo API, plus airline and airport information from Wikipedia, and loads it into Snowflake. |
| **Warehouse** | Snowflake stores raw and transformed data, with separate roles, users, warehouse, database and schemas following access-control best practices. |
| **Transform** | `dbt Core` builds staging (`src`), dimension/fact (`dim`/`fct`) and `mart` models. |
| **Orchestrate** | `Dagster` schedules and runs the dlt and dbt steps as assets. |
| **Visualise** | `Streamlit` queries the mart layer in Snowflake and presents the dashboard. |
| **Containerise & Deploy** | Dagster and Streamlit run in separate Docker containers, deployed to Azure. |

---

## 3. Tech Stack

| Tool | Purpose | Why |
|------|---------|-----|
| **dlt** | Data extraction and loading | Lightweight Python-native ingestion with schema handling. Tables are replaced on every run |
| **Snowflake** | Cloud data warehouse | Required by the project; separates storage and compute, supports role-based access control |
| **dbt Core** | Data transformation | SQL-based, version-controlled models with built-in testing and documentation |
| **Dagster** | Orchestration | Asset-based orchestration with schedules, sensors and a UI; integrates with dlt and dbt |
| **Streamlit** | BI dashboard | Fast development of interactive dashboards in Python |
| **Docker** | Containerisation | Reproducible environments for Dagster and Streamlit |
| **Azure** | Cloud deployment | Container App (Dagster) and Web App (Streamlit) |
| **dbdiagram** | Data modelling | Visual design of the dimensional model |
| **uv** | Python package management | Fast dependency management |

---

## 4. Project Structure

```
.
├── data_load_extract/     # dlt pipelines: Swedavia API + Wikipedia
├── data_transformation/
│   └── dbt_flights/       # dbt project (src, dim, fct, mart, macros, seeds)
├── eda/                   # Exploratory work (.ipynb) and EDA
├── orchestration/         # Dagster project (assets, jobs, schedules, sensors)
├── streamlit_app/         # Streamlit dashboard
├── worksheets_snowflake/  # SQL scripts for the Snowflake setup
├── docs/                  # Data model diagram (dm_model.png) and other docs
├── dockerfile.dwh         # Docker image for Dagster (dlt + dbt)
├── dockerfile.dashboard   # Docker image for Streamlit
├── docker-compose.yml     # Runs Dagster and Streamlit locally
├── profiles.yml           # dbt profile used inside the Docker container
├── .env.example           # Template for environment variables
├── pyproject.toml         # Python dependencies (uv)
└── README.md
```

---

## 5. Getting Started

### 5.1 Requirements

**Software:** [Docker](https://www.docker.com/) with Docker Compose and Git. To run without Docker you also need [uv](https://docs.astral.sh/uv/) and Python 3.13 (see `pyproject.toml`).

**Accounts:**

- **Snowflake** trial account (all team members develop within the *same* trial account)
- **Swedavia API key**: sign up at the [Swedavia developer portal](https://apideveloper.swedavia.se/) and subscribe to the FlightInfo API
- **Azure student account** (only needed for the [cloud deployment](#9-deployment-azure))

### 5.2 Set up Snowflake

Before the first run, set up Snowflake with the SQL scripts in `worksheets_snowflake/`, in this order: `setup_wh.sql`, `setup_db.sql`, `setup_users.sql`, `setup_roles.sql`. The setup follows access-control best practices:

- Separate **roles** with least-privilege grants: `flight_dlt_role` writes raw data to `staging`, `flight_dbt_role` reads `staging` and builds the dbt schemas
- One user, `developer`, that is granted both roles
- A dedicated **warehouse** (`swedavia_wh`), **database** (`swedavia_db`) and **schemas**
- Objects are created with `SYSADMIN`, users and roles with `USERADMIN` and `SECURITYADMIN`, not `ACCOUNTADMIN`

### 5.3 Clone the repository and configure

```bash
git clone https://github.com/cactus-commits/flight-punctuality-analytics.git
cd flight-punctuality-analytics
cp .env.example .env
```

All configuration is done through environment variables. See [`.env.example`](.env.example) for the full list of variables and example values. **Never commit `.env`.**

### 5.4 Start the stack

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Dagster UI | http://localhost:3000 |
| Streamlit dashboard | http://localhost:8501 |

### 5.5 Running without Docker (optional)

```bash
uv sync
# Dagster
uv run dagster dev -m orchestration.definitions
# Streamlit (reads the Snowflake credentials from .env)
uv run streamlit run streamlit_app/app.py
```

Without Docker, dbt uses your own `~/.dbt/profiles.yml`.

---

## 6. Usage

### Running the pipeline

1. Open the Dagster UI at http://localhost:3000.
2. Go to **Assets** and click **Materialize all** (or select specific assets).
3. Dagster runs the dlt extract/load steps first, then the dbt models.
4. Follow progress and logs under **Runs**.

### Using the dashboard

1. Open http://localhost:8501.
2. Use the filters (e.g. date, airport, airline) to explore delayed arrivals and departures.
3. Compare airlines and airports to identify where delays are concentrated.

See [`streamlit_app/README.md`](streamlit_app/README.md) for what each chart shows and how the metrics are calculated.

---

## 7. Data Model

The transformed data is modelled as a **dimensional model** (star schema), designed in [dbdiagram](https://dbdiagram.io/).

![Data model](docs/dm_model.png)

### Layers

| Layer | Prefix | Description |
|-------|--------|-------------|
| **Source / staging** | `src_` | Selects and renames the columns from the raw dlt tables |
| **Dimensions** | `dim_` | Descriptive entities: airlines, airports, dates |
| **Facts** | `fct_` | One row per flight (arrivals and departures), deduplicated and linked to the dimensions |
| **Marts** | `mart_` | One row per flight with airline, airport and date names, delay in minutes and whether the flight was delayed. Used by the dashboard |

---

## 8. Testing and Data Quality

Data quality is checked with dbt tests defined in the `schema.yml` files:

- `not_null`: key columns must not be empty
- `unique`: primary keys must be unique

Run the tests:

```bash
cd data_transformation/dbt_flights
dbt test
```

To build the models and run the tests in one go:

```bash
dbt build
```

---

## 9. Deployment (Azure)

Dagster and Streamlit are containerised separately and deployed to an Azure student account.

| Component | Image | Port | Azure resource |
|-----------|-------|------|----------------|
| Dagster (dlt + dbt) | `dwh_pipeline` | 3000 | **Container App** |
| Streamlit | `dashboard` | 8501 | **Web App** |

The flow is: **test locally → push images to Azure Container Registry (ACR) → create the Container App and the Web App → set environment variables in Azure.**

> `.env` is **not** copied into the images (it is in `.dockerignore`), so Azure cannot read it. Every variable the containers need must be added manually as an environment variable in Azure. A *secret* alone is not enough: you must also create an environment variable that references it.

### 9.1 Before you deploy

Use the same resource group and region (e.g. Sweden Central) for all resources. The local setup in [5.3](#53-clone-the-repository-and-configure) and [5.4](#54-start-the-stack) must work first: if `docker compose up --build` runs and both UIs load locally, the images are ready to push.

### 9.2 Push images to Azure Container Registry

Create a container registry and enable **Admin user** under *Settings → Access keys*. The login server, username and password are shown on the same page.

```bash
# Build both images 
docker compose build <imagename>

# Log in with the username and password from Access keys
docker login <registry-name>.azurecr.io

# Push images to Azure 
docker push <registry-name>.azurecr.io/dwh_pipeline:latest
docker push <registry-name>.azurecr.io/dashboard:latest

```

Check in the portal under **Container registry → Repositories** that both `dwh_pipeline` and `dashboard` exist with the tag `latest`.

### 9.3 Container App (Dagster)

In the Azure portal: **Container Apps → Create**.

| Tab | Setting |
|-----|---------|
| Basics | Same resource group, a name (e.g. `dagster-container-app`), region Sweden Central |
| Container | **If needed**: Untick *Use quickstart image*. Source: **Azure Container Registry**, image `dwh_pipeline`, tag `latest` |
| Container | Start with **2 CPU / 4 Gi** memory. Too little memory makes the container crash |
| Ingress | Enable ingress, accept traffic **from anywhere**, **target port `3000`** |

**Environment variables** (*Application → Containers → Edit and deploy → Environment variables*): add every variable from [`.env.example`](.env.example), with exactly the same names (double underscores and upper case matter). dbt and dlt need at least:

| Name | Value |
|------|-------|
| `DESTINATION__SNOWFLAKE__CREDENTIALS__USERNAME` | Snowflake user |
| `DESTINATION__SNOWFLAKE__CREDENTIALS__PASSWORD` | Password (preferably *Reference a secret*) |
| `DESTINATION__SNOWFLAKE__CREDENTIALS__HOST` | Snowflake account identifier |
| `DESTINATION__SNOWFLAKE__CREDENTIALS__DATABASE` | `swedavia_db` |
| `DESTINATION__SNOWFLAKE__CREDENTIALS__WAREHOUSE` | `swedavia_wh` |
| `DESTINATION__SNOWFLAKE__CREDENTIALS__ROLE` | Role used by the pipeline |
| *(the rest of `.env.example`)* | e.g. the Swedavia API key |


### 9.4 Web App (Streamlit)

In the Azure portal: **App Services → Create → Web App**.

| Tab | Setting |
|-----|---------|
| Basics | Same resource group, a name, **Publish: Container**, **OS: Linux**, region Sweden Central |
| Database | None |
| Container | Untick *Sidecar*. Source: **Azure Container Registry**, image `dashboard`, tag `latest` |
| Networking | Public access: On |

**Environment variables** (*Settings → Environment variables → App settings*):

| Name | Value | Why |
|------|-------|-----|
| `WEBSITES_PORT` | `8501` | Azure probes port 80 by default |
| `STREAMLIT_SERVER_ADDRESS` | `0.0.0.0` | Streamlit must listen externally |
| `STREAMLIT_SERVER_PORT` | `8501` | |
| `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER_TRANSFORMER_PASSWORD` and the other `_SNOWFLAKE_*` variables the app reads (database, schema, role, warehouse) | from `.env` | Streamlit connects to Snowflake with these |

Click **Apply**, then **Restart** the Web App.

### 9.5 Verify

- **Container App:** open the *Application Url*. The Dagster UI should load. Materialize the assets to confirm that dlt and dbt run from Azure.
- **Web App:** open the *Default domain*. The dashboard should look the same as locally. The mart tables must exist in Snowflake, so run the pipeline at least once first.
- Logs: **Monitoring → Log stream** for both resources.

### 9.6 Updating after code changes or to start it up again

```bash
docker compose build
# re-tag and push as in 9.2
```

Then create a new revision of the Container App, or **Restart** the Web App.

### 9.7 Troubleshooting

| Error | Cause and fix |
|-------|---------------|
| `Env var required but not provided: 'DESTINATION__SNOWFLAKE__...'` (Dagster fails to load) | The variable is missing or misspelled in the Container App. Add it with the exact name and create a new revision |
| A secret exists but the variable is missing | Create the environment variable and choose *Reference a secret* |
| `ContainerTimeout ... probing port 80` (Web App) | `WEBSITES_PORT=8501` is missing or was not applied. Set it, **Apply** and **Restart**. Optionally set `WEBSITES_CONTAINER_START_TIME_LIMIT=600` |
| `Object 'MART_...' does not exist or not authorized` (dashboard) | Wrong `SNOWFLAKE_DATABASE`/`SNOWFLAKE_SCHEMA`/role in Azure, the pipeline has not been run yet, or the role lacks `SELECT` on the mart schema. Compare with your local `.env` and check the grants in `worksheets_snowflake/` |
| Container crashes or restarts | Increase CPU/memory |
| Image cannot be pulled | *Admin user* not enabled on the registry, or wrong image name/tag |

### 9.8 Security

- Never commit `.env` and never bake secrets into images (`ENV`/`ARG` in a Dockerfile).
- Use secrets for passwords in Azure, and rotate any password that has been exposed.

---

## 10. Known Limitations and Future Work

- Only the past three days of data are extracted. No long-term history is kept yet
- About 3–8% of flights have an airline or airport that is not in the Wikipedia reference lists, so they show as `Unknown` in the marts. Swedavia often gives only an ICAO code for airlines (e.g. JON, FRO), while the Wikipedia list is matched on IATA. Some foreign airports and placeholder codes (e.g. AGH, SFT, ZZZ) are also missing. Swedavia airports that are missing from the Wikipedia list (Ronneby and Kiruna) are added in `data_transformation/dbt_flights/seeds/missing_airports.csv`
- The date of a flight is taken from the scheduled time in UTC. Flights just after midnight Swedish time (00:00–02:00 in summer time, 00:00–01:00 in winter time) are therefore shown on the previous day
- Delay metrics depend on the quality and completeness of the Swedavia API data
- Wikipedia data may be incomplete or change over time
- More dbt tests (e.g. `relationships`, `accepted_values`) could be added
- Alerting on failed Dagster runs
- Additional analyses, e.g. delay causes, time of day, weather

---

## 11. Authors and Data Sources

**Authors:**

| Name | GitHub |
|------|-------|
| Miranda Lyng | [@mirandalyng](https://github.com/mirandalyng) |
| Lisa Yllander | [@LisaYllander92](https://github.com/LisaYllander92) |
| Alexandra Kaktus | [@cactus-commits](https://github.com/cactus-commits) |
| Rickard Garnau | [@rickard-garnau](https://github.com/rickard-garnau) |
| Filippa Jansson | [@Filippa-Jansson](https://github.com/Filippa-Jansson) |

**Data sources:**

- [Swedavia FlightInfo API](https://apideveloper.swedavia.se/): arrivals and departures
- Wikipedia: airline operators
- Wikipedia: airports
- [Dagster docs: creating projects](https://dagster.io/docs/guides/build/projects/creating-projects)

*Project developed as part of a data engineering course.*