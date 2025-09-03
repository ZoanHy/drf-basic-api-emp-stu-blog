from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

def students(request: HttpRequest):
    students = [
        {'id': 1, 'name': 'Linh', 'age': 20},
        {'id': 2, 'name': 'John', 'age': 22},
        {'id': 3, 'name': 'Jane', 'age': 21},
    ]
    
    
    return HttpResponse(students)