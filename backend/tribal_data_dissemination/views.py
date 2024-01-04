from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
#from .models import OneTimeAccess  # for OneTimeAccess model

@csrf_exempt# this is marked as csrf_exempt to enable by-hand testing via tools like Postman. Should be removed when the frontend form is implemented!

def request_file_access(request):
    # Assuming the request contains report_id and file_type in the POST data
    report_id = request.POST.get('report_id')
    file_type = request.POST.get('file_type')

    # Checking if the user has privileged access 
    # WIP
    has_privileged_access = check_privileged_access(request.headers)  # Function to check privileged access

    if has_privileged_access:
        # Generate UUID (using UUID4)
        access_uuid = get_random_string(length=32)

        # Getting user's API key ID
        user_api_key_id = request.user.api_key.id

        # Creating a new entry in the OneTimeAccess table
        one_time_access = OneTimeAccess.objects.create(
            uuid=access_uuid,
            api_key_id=user_api_key_id,
            report_id=report_id,
            file_type=file_type
        )

        # Return the UUID to the user
        return JsonResponse({'access_uuid': access_uuid})
    else:
        return JsonResponse({'error': 'Unauthorized access'}, status=403)
