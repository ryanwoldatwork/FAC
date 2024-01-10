CREATE OR REPLACE FUNCTION request_file_access(
    p_report_id INTEGER,
    p_file_type VARCHAR(100),
    p_api_key_id INTEGER
) RETURNS JSON LANGUAGE plpgsql AS
$$
DECLARE
    v_access_uuid VARCHAR(32);
BEGIN
    IF p_api_key_id IS NOT NULL THEN
        -- Generate UUID (using PostgreSQL's gen_random_uuid function)
        SELECT REPLACE(gen_random_uuid()::text, '-', '') INTO v_access_uuid;

        -- Inserting data into the one_time_access table
        INSERT INTO one_time_access (uuid, api_key_id, report_id, file_type)
        VALUES (v_access_uuid, p_api_key_id, p_report_id, p_file_type);

        -- Return the UUID to the user
        RETURN json_build_object('access_uuid', v_access_uuid);
    ELSE
        -- Return an error for unauthorized access
        RETURN json_build_object('error', 'Unauthorized access')::JSON;
    END IF;
END;
$$;
