DROP TABLE IF EXISTS support_administrative_key_uuids;

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
        'darth.vader@deathstar.com',
        'b6e08808-ecb2-b928-46d4205497ff',
        '2024-01-08'
    )
    ;
