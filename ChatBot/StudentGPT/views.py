import os
from django.shortcuts import render
from django.http import JsonResponse
from reportlab.pdfgen import canvas

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
    else:
        print("No file")
    return render(request, 'pages/index.html')