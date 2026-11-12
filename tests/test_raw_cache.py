
from pipeline.raw_cache import (
    calculate_hash,
    save_raw_response
)


def test_hash_is_consistent():

    content = b'{"company": "Stripe"}'

    hash1 = calculate_hash(content)
    hash2 = calculate_hash(content)

    assert hash1 == hash2


def test_changed_content_has_different_hash():

    content1 = b'{"salary": 100000}'
    content2 = b'{"salary": 120000}'

    assert calculate_hash(content1) != calculate_hash(content2)


def test_save_raw_response(tmp_path, monkeypatch):

    import pipeline.raw_cache as cache

    monkeypatch.setattr(
        cache,
        "RAW_DIR",
        tmp_path
    )

    content = b'{"company": "Stripe"}'

    result = save_raw_response(
        source="greenhouse",
        identifier="stripe",
        content=content,
        extension="json"
    )

    assert result["source"] == "greenhouse"

    assert result["identifier"] == "stripe"

    assert result["content_hash"] == calculate_hash(content)

    assert (tmp_path / "manifest.jsonl").exists()
