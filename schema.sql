CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10),
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    referral_source VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE lexicon (
    id SERIAL PRIMARY KEY,
    lex_key VARCHAR(255) NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    text TEXT NOT NULL,
    UNIQUE (lex_key, lang_code)
);