from django.shortcuts import render
from django.http import HttpRequest, JsonResponse

def studentsView(request: HttpRequest):
    students =  {'id': 1, 'name': 'Linh', 'age': 20}
    
    return JsonResponse(students)