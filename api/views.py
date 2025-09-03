from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from students.models import Student
from .serializers import StudentSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(['GET'])
def studentsView(request: HttpRequest):
    # students = Student.objects.all()
    # students_list = list(students.values())
    
    if (request.method == 'GET'):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    