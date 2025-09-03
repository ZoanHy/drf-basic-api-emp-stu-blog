Ok, mình đã chỉnh lại format cho đẹp, dễ đọc và trực quan hơn. Bạn có thể copy nguyên văn sang Notion hoặc VSCode để làm tài liệu học tập:

---

# 📘 Lesson 1: API, RESTFul API, Django & Django REST Framework

---

## 1. 🌐 API là gì?

- **API (Application Programming Interface)**: tập hợp các quy tắc cho phép phần mềm giao tiếp với nhau.
- Vai trò: **cầu nối** giữa **client** (web, mobile app) ↔ **server** (nơi xử lý và lưu dữ liệu).

👉 Ví dụ: App thời tiết gọi API server để lấy dữ liệu nhiệt độ.

---

## 2. 🔄 RESTFul API

- **REST (Representational State Transfer)**: phong cách thiết kế API phổ biến.
- **Đặc điểm chính**:

  - HTTP methods:

    - `GET` → lấy dữ liệu
    - `POST` → thêm mới
    - `PUT/PATCH` → cập nhật
    - `DELETE` → xóa

  - Dữ liệu trả về thường ở **JSON**
  - **Stateless**: mỗi request độc lập, server không nhớ trạng thái client
  - URL hướng tài nguyên (**resource-oriented**)

👉 Ví dụ:

- `/students/` → danh sách sinh viên
- `/students/1/` → thông tin sinh viên có `id=1`

---

## 3. ⚙️ Cài đặt Django & DRF

### Bước 1: Tạo môi trường ảo

```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 2: Cài Django

```bash
pip install django
```

### Bước 3: Khởi tạo project

```bash
django-admin startproject myproject
cd myproject
python manage.py runserver
```

### Bước 4: Cài Django REST Framework

```bash
pip install djangorestframework
```

Thêm vào `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
]
```

---

## 4. 🏗️ Tạo app `students` & endpoint

### Bước 1: Tạo app

```bash
python manage.py startapp students
```

Khai báo trong `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'students',
]
```

### Bước 2: Model

`students/models.py`

```python
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    grade = models.CharField(max_length=10)

    def __str__(self):
        return self.name
```

### Bước 3: Serializer

`students/serializers.py`

```python
from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
```

### Bước 4: View

`students/views.py`

```python
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Student
from .serializers import StudentSerializer

@api_view(['GET'])
def student_list(request):
    students = Student.objects.all()
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)
```

### Bước 5: URL

`students/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student-list'),
]
```

`myproject/urls.py`

```python
from django.urls import path, include

urlpatterns = [
    path('students/', include('students.urls')),
]
```

---

## 5. ▶️ Chạy & kiểm tra

- Tạo bảng:

```bash
python manage.py makemigrations
python manage.py migrate
```

- (Tuỳ chọn) tạo admin:

```bash
python manage.py createsuperuser
```

- Chạy server:

```bash
python manage.py runserver
```

- Truy cập API:

```
http://127.0.0.1:8000/students/
```

---

## 6. 📤 Kết quả

Response JSON từ API `/students/` (method: `GET`):

```json
[
  {
    "id": 1,
    "name": "Nguyen Van A",
    "age": 20,
    "grade": "A"
  },
  {
    "id": 2,
    "name": "Tran Thi B",
    "age": 21,
    "grade": "B"
  }
]
```

---

## ✅ Tổng kết

- Hiểu API & RESTFul API.
- Cài đặt Django & Django REST Framework.
- Tạo app `students` với quy trình:
  **Model → Serializer → View → URL**
- Kết quả: Endpoint `/students/` trả về danh sách sinh viên.

---

👉 Đây là kiến thức cơ bản mở đầu, để sau này mở rộng thêm CRUD (`GET`, `POST`, `PUT`, `DELETE`).

---

Bạn có muốn mình vẽ thêm **sơ đồ minh họa luồng API** (Client → Request → DRF → Response JSON) để gắn vào file này không?
