
from pipeline.ingestion import ingest_all_sources


def test_ingest_all_sources(monkeypatch):

    def mock_greenhouse():
        return [
            {"source": "greenhouse", "job_id": "1"}
        ]

    def mock_lever():
        return [
            {"source": "lever", "job_id": "2"}
        ]

    def mock_hackernews():
        return [
            {"source": "hackernews", "job_id": "3"}
        ]

    monkeypatch.setattr(
        "pipeline.ingestion.fetch_all_greenhouse_jobs",
        mock_greenhouse
    )

    monkeypatch.setattr(
        "pipeline.ingestion.fetch_all_lever_jobs",
        mock_lever
    )

    monkeypatch.setattr(
        "pipeline.ingestion.fetch_hackernews_jobs",
        mock_hackernews
    )

    jobs, summary = ingest_all_sources()

    assert len(jobs) == 3

    assert summary["greenhouse"] == 1
    assert summary["lever"] == 1
    assert summary["hackernews"] == 1


def test_one_source_failure_does_not_stop_pipeline(
    monkeypatch
):

    def mock_greenhouse():
        raise Exception("API unavailable")

    def mock_lever():
        return [{"source": "lever", "job_id": "2"}]

    def mock_hackernews():
        return [{"source": "hackernews", "job_id": "3"}]

    monkeypatch.setattr(
        "pipeline.ingestion.fetch_all_greenhouse_jobs",
        mock_greenhouse
    )

    monkeypatch.setattr(
        "pipeline.ingestion.fetch_all_lever_jobs",
        mock_lever
    )

    monkeypatch.setattr(
        "pipeline.ingestion.fetch_hackernews_jobs",
        mock_hackernews
    )

    jobs, summary = ingest_all_sources()

    assert len(jobs) == 2

    assert summary["greenhouse"] == 0
    assert summary["lever"] == 1
    assert summary["hackernews"] == 1
