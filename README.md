# AI Mock Interview Analytics System

A **FastAPI** backend that evaluates mock interview performance and generates dynamic data visualizations (PNG charts) in memory using **Pandas** and **Matplotlib**.

## Features

- **Performance Analytics**: Calculates candidate performance, topic averages, and progression.
- **In-Memory Chart Rendering**: Generates PNG visualisations on-the-fly using Matplotlib (`Agg` backend) and `io.BytesIO` without writing to disk.
- **RESTful Endpoints**: Provides endpoints for answer submissions and chart visualization.

## Tech Stack

- **Framework**: FastAPI
- **Data Processing**: Pandas
- **Visualization**: Matplotlib
- **Server**: Uvicorn

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/hrachm18-glitch/ai_mock_interview.git](https://github.com/hrachm18-glitch/ai_mock_interview.git)


python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload