import os
import json
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def index(request):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]

        file_path = os.path.join(BASE_DIR, "media", "uploads", uploaded_file.name)
        with open(file_path, "wb+") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        return JsonResponse({"status": "success"})

    if request.method == "DELETE":
        try:
            data = json.loads(request.body.decode("utf-8"))
            filename = data.get("fileName")

            if filename:
                file_path = os.path.join(BASE_DIR, "media", "uploads", filename)
                os.remove(file_path)
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "File name not provided"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "failed"}, status=500)

    return render(request, 'pages/index.html')