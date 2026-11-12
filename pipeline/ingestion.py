
import logging
from collections import Counter

from pipeline.greenhouse import fetch_all_greenhouse_jobs
from pipeline.lever import fetch_all_lever_jobs
from pipeline.hackernews import fetch_hackernews_jobs


logger = logging.getLogger(__name__)


def ingest_all_sources():

    all_jobs = []

    source_results = {}

    # ---------------------------------
    # 1. Greenhouse ingestion
    # ---------------------------------

    try:

        greenhouse_jobs = fetch_all_greenhouse_jobs()

        all_jobs.extend(greenhouse_jobs)

        source_results["greenhouse"] = len(
            greenhouse_jobs
        )

    except Exception:

        logger.exception(
            "Greenhouse ingestion failed"
        )

        source_results["greenhouse"] = 0


    # ---------------------------------
    # 2. Lever ingestion
    # ---------------------------------

    try:

        lever_jobs = fetch_all_lever_jobs()

        all_jobs.extend(lever_jobs)

        source_results["lever"] = len(
            lever_jobs
        )

    except Exception:

        logger.exception(
            "Lever ingestion failed"
        )

        source_results["lever"] = 0


    # ---------------------------------
    # 3. Hacker News ingestion
    # ---------------------------------

    try:

        hackernews_jobs = fetch_hackernews_jobs()

        all_jobs.extend(hackernews_jobs)

        source_results["hackernews"] = len(
            hackernews_jobs
        )

    except Exception:

        logger.exception(
            "Hacker News ingestion failed"
        )

        source_results["hackernews"] = 0


    # ---------------------------------
    # 4. Generate ingestion summary
    # ---------------------------------

    logger.info("INGESTION SUMMARY")

    for source, count in source_results.items():

        logger.info(
            "%s: %d records",
            source,
            count
        )

    logger.info(
        "Total raw records: %d",
        len(all_jobs)
    )

    return all_jobs, source_results


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    jobs, summary = ingest_all_sources()

    print("\n========== INGESTION SUMMARY ==========")

    for source, count in summary.items():

        print(f"{source}: {count}")

    print("\nTotal raw records:", len(jobs))
