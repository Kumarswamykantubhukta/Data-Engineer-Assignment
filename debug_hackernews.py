
from pipeline.ingestion import ingest_all_sources
from pipeline.hackernews_parser import split_hackernews_comment
from pipeline.filtering import is_target_role, is_us_eligible

jobs, summary = ingest_all_sources()

hn_jobs = [
    job for job in jobs
    if job.get("source") == "hackernews"
]

print("Raw Hacker News comments:", len(hn_jobs))

parsed_jobs = []

for comment in hn_jobs:
    parsed_jobs.extend(split_hackernews_comment(comment))

print("Parsed Hacker News jobs:", len(parsed_jobs))

print("\n========== SAMPLE PARSED RECORDS ==========")

for job in parsed_jobs[:5]:
    print("\nCompany:", job.get("company"))
    print("Title:", job.get("job_title"))
    print("Location:", job.get("location"))
    print("Description:", (job.get("description") or "")[:400])
    print("Target role:", is_target_role(job.get("job_title")))
    print("US eligible:", is_us_eligible(job))
    
print("\n========== RAW HN RECORD STRUCTURE ==========")

for job in hn_jobs[:3]:
    print("\nKeys:", list(job.keys()))

    for key, value in job.items():
        if key != "description":
            print(f"{key}: {value}")

    print("Description:", (job.get("description") or "")[:250])
