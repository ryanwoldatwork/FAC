CREATE OR REPLACE FUNCTION admin_api_v1_0_0.add_tribal_api_key_access(params JSON) 
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
