CREATE OR REPLACE FUNCTION request_file_access(
    p_report_id INTEGER,
    p_file_type VARCHAR(100),
    p_api_key_id INTEGER
) RETURNS JSON LANGUAGE plpgsql AS
$$
DECLARE
    v_access_uuid VARCHAR(32);
    v_has_permission BOOLEAN;
    v_key_exists BOOLEAN;
    v_key_added_date DATE;
BEGIN
    -- Check if the user has tribal data access permission
    SELECT api_v1_0_3_functions.has_tribal_data_access() INTO v_has_permission;

    -- Check if the provided API key exists in tribal_api_access_key_ids
    SELECT 
        EXISTS(
            SELECT 1
            FROM tribal_api_access_key_ids
            WHERE keyid = p_api_key_id
        ) INTO v_key_exists;

    -- Get the added date of the key from tribal_api_access_key_ids
    SELECT added
    INTO v_key_added_date
    FROM tribal_api_access_key_ids
    WHERE keyid = p_api_key_id;

    -- Check if the key is less than 6 months old
    IF p_api_key_id IS NOT NULL AND v_has_permission AND v_key_exists AND v_key_added_date >= CURRENT_DATE - INTERVAL '6 months' THEN
        -- Generate UUID (using PostgreSQL's gen_random_uuid function)
        SELECT REPLACE(gen_random_uuid()::text, '-', '') INTO v_access_uuid;

        -- Inserting data into the one_time_access table
        INSERT INTO one_time_access (uuid, api_key_id, report_id, file_type)
        VALUES (v_access_uuid, p_api_key_id, p_report_id, p_file_type);

        -- Return the UUID to the user
        RETURN json_build_object('access_uuid', v_access_uuid);
    ELSE
        -- Return an error for unauthorized access
        RETURN json_build_object('error', 'Unauthorized access or key older than 6 months')::JSON;
    END IF;
END;
$$;
