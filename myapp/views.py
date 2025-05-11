from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
import json
import os
from .BERT import handle_uploaded_file


# Create your views here.

def index(request):
    return render(request, 'index.html')


@csrf_exempt
def sign_up(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            email = data.get("email")
            password = data.get("password")

            if not name or not email or not password:
                return JsonResponse({"error": "All fields are required"}, status=400)

            # Add logic to save the user to the database
            user = User(name=name, email=email, password=password)
            user.save()
            return JsonResponse({"message": "Signup successful"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def signin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        try:
            user = User.objects.get(email=email, password=password)
            return JsonResponse({'message': 'User authenticated successfully'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid email or password'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        upload_dir = "uploads"  # Directory to save uploaded files
        file_path = os.path.join(upload_dir, uploaded_file.name)

        try:
            # Ensure the uploads directory exists
            os.makedirs(upload_dir, exist_ok=True)

            # Save the uploaded file
            with open(file_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # Process the file using BERT.py
            result = handle_uploaded_file(file_path)

            # Clean up the uploaded file if needed
            os.remove(file_path)

            # Format the summary and risks as bullet points
            formatted_summary = [f"{line.strip()}" for line in result.get("summary", []) if line.strip()]
            formatted_risks = [f"{line.strip()}" for line in result.get("risks", []) if line.strip()]

            # Return the analysis result in a formatted JSON response
            return JsonResponse({
                "message": "File processed successfully",
                "data": {
                    "summary": formatted_summary or ["No summary available"],
                    "risks": formatted_risks or ["No risks identified"],
                    "pdf_file": f"/outputs/{os.path.basename(result.get('pdf_file'))}"  # Ensure correct path
                }
            }, json_dumps_params={'indent': 4})  # Add indentation for better formatting
        except Exception as e:
            # Log the error and return a 500 response
            print(f"Error: {e}")
            return JsonResponse({"error": "An error occurred while processing the file"}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)