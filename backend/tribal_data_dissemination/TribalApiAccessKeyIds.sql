DROP TABLE IF EXISTS tribal_api_access_key_ids;

CREATE TABLE tribal_api_access_key_ids
    (
        id BIGSERIAL PRIMARY KEY,
        email TEXT,
        keyid TEXT,
        added DATE
    );

INSERT INTO tribal_api_access_key_ids 
    (email, keyid, added)
    VALUES
    (
        'darth.vader@deathstar.gsa.gov',
        'b6e08808-ecb2-b928-46d4205497ff',
        '2024-01-08'
    )
    ;
