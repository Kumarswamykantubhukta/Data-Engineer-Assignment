
CREATE TABLE IF NOT EXISTS jobs (
    id BIGSERIAL PRIMARY KEY,

    company VARCHAR(255) NOT NULL,
    job_title VARCHAR(500) NOT NULL,

    location TEXT,
    country VARCHAR(100),
    work_arrangement VARCHAR(100),
    employment_type VARCHAR(100),
    experience_required TEXT,
    salary TEXT,

    required_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    preferred_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,

    description TEXT,
    content_hash VARCHAR(64),

    status VARCHAR(30) NOT NULL DEFAULT 'active',

    first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_job_status
        CHECK (status IN ('active', 'closed', 'expired', 'review'))
);


CREATE TABLE IF NOT EXISTS job_sources (
    id BIGSERIAL PRIMARY KEY,

    job_id BIGINT NOT NULL
        REFERENCES jobs(id) ON DELETE CASCADE,

    source VARCHAR(50) NOT NULL,
    source_job_id VARCHAR(255),
    source_url TEXT NOT NULL,

    raw_record JSONB NOT NULL DEFAULT '{}'::jsonb,

    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_source_record
        UNIQUE (source, source_job_id)
);


CREATE TABLE IF NOT EXISTS job_history (
    id BIGSERIAL PRIMARY KEY,

    job_id BIGINT NOT NULL
        REFERENCES jobs(id) ON DELETE CASCADE,

    change_type VARCHAR(50) NOT NULL,

    old_data JSONB,
    new_data JSONB,

    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- Indexes for common queries

CREATE INDEX IF NOT EXISTS idx_jobs_company
    ON jobs(company);

CREATE INDEX IF NOT EXISTS idx_jobs_title
    ON jobs(job_title);

CREATE INDEX IF NOT EXISTS idx_jobs_status
    ON jobs(status);

CREATE INDEX IF NOT EXISTS idx_jobs_last_seen
    ON jobs(last_seen);

CREATE INDEX IF NOT EXISTS idx_job_sources_job_id
    ON job_sources(job_id);

CREATE INDEX IF NOT EXISTS idx_job_sources_source
    ON job_sources(source);

CREATE INDEX IF NOT EXISTS idx_job_history_job_id
    ON job_history(job_id);

CREATE INDEX IF NOT EXISTS idx_jobs_required_skills
    ON jobs USING GIN(required_skills);
