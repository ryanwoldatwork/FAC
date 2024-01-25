-- WARNING
-- Under PostgreSQL 12, the functions below work.
-- Under PostgreSQL 14, these will break.
--
-- Note the differences:
--
-- raise info 'Works under PostgreSQL 12';
-- raise info 'request.header.x-magic %', (SELECT current_setting('request.header.x-magic', true));
-- raise info 'request.jwt.claim.expires %', (SELECT current_setting('request.jwt.claim.expires', true));
-- raise info 'Works under PostgreSQL 14';
-- raise info 'request.headers::json->>x-magic %', (SELECT current_setting('request.headers', true)::json->>'x-magic');
-- raise info 'request.jwt.claims::json->expires %', (SELECT current_setting('request.jwt.claims', true)::json->>'expires');
--
-- To quote the work of Dav Pilkey, "remember this now."

-- We don't grant tribal access (yet)
create or replace function api_v1_0_3_functions.has_tribal_data_access() returns boolean
as $has_tribal_data_access$
DECLARE 
    uuid_header text;
    key_exists boolean;
BEGIN
    SELECT admin_api_v1_0_0_functions.get_api_key_uuid() INTO uuid_header;

    SELECT 
        CASE WHEN EXISTS (
            SELECT uuid 
            FROM public.support_administrative_key_uuids aku
            WHERE aku.uuid = uuid_header)
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO key_exists;
    RETURN key_exists;
END;
$has_tribal_data_access$ LANGUAGE plpgsql;



--The function below add_tribal_api_key_access adds read access to a tribal API for a specified email.
--It checks if the API user has read permissions.
--If the email already exists in the database, the function returns false.
--Otherwise, it adds the email with 'read-tribal' permission, logs the event, and returns true.

CREATE OR REPLACE FUNCTION api_v1_0_3.add_tribal_api_key_access(params JSON) 
RETURNS BOOLEAN
AS $add_tribal_api_key_access$
DECLARE 
    already_exists INTEGER;
    read_tribal_id INTEGER;
BEGIN
    -- If the API user has read permissions, give it a go
    IF admin_api_v1_0_0_functions.has_admin_data_access('READ') THEN
        -- Check if the email already exists
        SELECT count(up.email) 
        INTO already_exists
        FROM public.users_userpermission AS up
        WHERE email = params->>'email';

        -- If they are already in the table, exit
        IF already_exists <> 0 THEN
            RETURN 0;
        END IF;

        -- Get the 'read-tribal' permission ID
        SELECT up.id 
        INTO read_tribal_id 
        FROM public.users_permission AS up
        WHERE up.slug = 'read-tribal';

        -- Insert the new user permission
        INSERT INTO public.users_userpermission (email, permission_id, user_id)
        VALUES (params->>'email', read_tribal_id, null);

        -- Log the event
        RETURN admin_api_v1_0_0_functions.log_admin_api_event('tribal-access-email-added', 
                                                    json_build_object('email', params->>'email'));
    END IF;

    RETURN 0;
END;
$add_tribal_api_key_access$ LANGUAGE plpgsql;


NOTIFY pgrst, 'reload schema';
