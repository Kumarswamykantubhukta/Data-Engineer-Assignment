# Job Market Intelligence Pipeline

A Python-based data engineering project that collects engineering job postings from Greenhouse, Lever, and Hacker News Who is Hiring, processes and deduplicates them, extracts structured information, validates extracted fields, and stores the results in PostgreSQL.

## 1. Project Overview

The objective of this project is to build an incremental job market intelligence pipeline that identifies opportunities in the following engineering categories:

- Data Engineering
- Machine Learning Engineering
- Analytics Engineering
- Platform Engineering

The pipeline focuses on opportunities located in the United States, including explicitly US-remote positions.

### Data Sources

| Source | Description |
|---|---|
| Greenhouse | Job postings collected through the Greenhouse Job Board API |
| Lever | Job postings collected through the Lever Postings API |
| Hacker News | Hiring comments collected from the monthly Who is Hiring thread |

## 2. Architecture

```text
                 DATA SOURCES
                      |
          +-----------+-----------+
          |           |           |
      Greenhouse    Lever     Hacker News
          |           |           |
          +-----------+-----------+
                      |
               DATA INGESTION
                      |
                RAW DATA CACHE
                      |
             HACKER NEWS PARSING
                      |
                JOB FILTERING
                      |
                DEDUPLICATION
                      |
             INCREMENTAL PROCESSING
                      |
              STRUCTURED EXTRACTION
                      |
              EVIDENCE VALIDATION
                      |
                POSTGRESQL
                      |
                 CSV EXPORT
```

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Pipeline development |
| PostgreSQL 18 | Persistent data storage |
| Gemini API | Structured information extraction |
| Pydantic | Data validation and structured schemas |
| Requests | API requests and web scraping |
| BeautifulSoup | HTML parsing |
| Psycopg 3 | PostgreSQL connectivity |
| Python-dotenv | Environment variable management |
| Tenacity / urllib3 Retry | Retry and error handling |
| Pytest | Automated testing |

## 4. Project Structure

```text
job_market_intelligence/
│
├── pipeline/
│   ├── __init__.py
│   ├── config.py
│   ├── greenhouse.py
│   ├── lever.py
│   ├── hackernews.py
│   ├── hackernews_parser.py
│   ├── ingestion.py
│   ├── raw_cache