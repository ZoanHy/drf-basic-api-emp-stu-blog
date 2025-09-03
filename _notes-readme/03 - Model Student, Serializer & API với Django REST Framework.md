Tuyệt vời—mình gom toàn bộ nội dung “Lesson: Model → Serializer → API” thành **tài liệu Markdown đẹp, học là áp dụng được ngay**. Bạn có thể copy thẳng sang Notion/VS Code.

---

# 📘 Lesson: Model `Student`, Serializer & API với Django REST Framework

> Mục tiêu: Hiểu quy trình **Model → Serializer → View/Response** để trả về JSON cho endpoint `students/`.

---

## 0) Chuẩn bị nhanh

```bash
python3 -m venv venv
source venv/bin/activate

pip install django djangorestframework
django-admin startproject myproject
cd myproject
python manage.py startapp students
```

**Thêm app vào `settings.py`:**

```python
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'students',
]
```

---

## 1) Tạo Model `Student`

**`students/models.py`**

```python
from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=10, unique=True)  # nên unique
    name = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.student_id} - {self.name}"
```

> 💡 **Giải thích:**
>
> - `student_id`: mã SV, nên `unique=True` để tránh trùng.
> - `__str__`: giúp hiển thị đẹp ở Django Admin và shell.

**Chạy migration:**

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 2) Tạo superuser & đăng ký Admin

```bash
python manage.py createsuperuser
```

**`students/admin.py`**

```python
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_id', 'name', 'branch')
    search_fields = ('student_id', 'name', 'branch')
```

> Vào `/admin` để thêm data mẫu nhanh.

---

## 3) Cách 1 (cơ bản): Trả JSON bằng `JsonResponse`

**Ý tưởng:** Lấy `QuerySet → list(dict)` rồi trả về JSON.

**`students/views_json.py` (tuỳ chọn tách file để học)**

```python
from django.http import JsonResponse
from .models import Student

def students_json_view(request):
    # Lấy tất cả SV
    students = Student.objects.all()
    # Convert QuerySet -> list các dict
    students_list = list(students.values('id', 'student_id', 'name', 'branch'))
    # Trả JsonResponse; nhớ safe=False vì dữ liệu là list, không phải dict
    return JsonResponse(students_list, safe=False, status=200)
```

> ⚠️ **Lưu ý quan trọng**
>
> - `JsonResponse` mặc định chỉ cho `dict`. Nếu trả `list`, cần `safe=False`.
> - Cách này **ổn** cho demo, nhưng thiếu: content negotiation, renderer, validation,…
>   → **Khuyến nghị** dùng Django REST Framework.

---

## 4) Cách 2 (chuyên nghiệp): Dùng **Django REST Framework**

### 4.1) Tạo `Serializer`

**`students/serializers.py`**

```python
from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        # hoặc: fields = ('id', 'student_id', 'name', 'branch')
        # read_only_fields = ('id',)
```

> 💡 **Serializer làm gì?**
>
> - **Chuyển đổi 2 chiều**: Model/QuerySet ↔ JSON.
> - **Validation**: kiểm tra dữ liệu input khi tạo/sửa (với POST/PUT/PATCH).
> - **Tùy biến**: ẩn hiện field, read-only, validate riêng.

### 4.2) Viết View với DRF (Function-Based View)

**`students/views.py`**

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Student
from .serializers import StudentSerializer

@api_view(['GET', 'POST'])
def students_view(request):
    if request.method == 'GET':
        students = Student.objects.all().order_by('id')
        serializer = StudentSerializer(students, many=True)  # many=True vì danh sách
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # tạo Student mới
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

> 🧠 **Giải thích nhanh:**
>
> - `@api_view([...])`: khai báo HTTP methods được phép.
> - `Response`: DRF Response, tự lo renderer (JSON, Browsable API, …).
> - `status`: dùng mã HTTP chuẩn (`200`, `201`, `400`, …).
> - `many=True`: bắt buộc khi serialize **danh sách**.

### 4.3) URLs

**`students/urls.py`**

```python
from django.urls import path
from .views import students_view

urlpatterns = [
    path('', students_view, name='students-list-create'),
]
```

**`myproject/urls.py`**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('students/', include('students.urls')),
]
```

---

## 5) Kiểm tra API

**Chạy server**

```bash
python manage.py runserver
```

### 5.1) GET danh sách

- Truy cập: `http://127.0.0.1:8000/students/`
- **Kết quả mẫu:**

```json
[
  { "id": 1, "student_id": "SV001", "name": "Nguyen Van A", "branch": "CS" },
  { "id": 2, "student_id": "SV002", "name": "Tran Thi B", "branch": "IT" }
]
```

### 5.2) POST tạo mới

**cURL**

```bash
curl -X POST http://127.0.0.1:8000/students/ \
  -H "Content-Type: application/json" \
  -d '{"student_id":"SV003","name":"Le Van C","branch":"AI"}'
```

**Kết quả 201**

```json
{ "id": 3, "student_id": "SV003", "name": "Le Van C", "branch": "AI" }
```

---

## 6) So sánh nhanh: `JsonResponse` vs **DRF Response + Serializer**

| Tiêu chí                            | JsonResponse (thuần Django)        | DRF (khuyến nghị)               |
| ----------------------------------- | ---------------------------------- | ------------------------------- |
| Chuyển đổi dữ liệu                  | Tự convert `QuerySet → list(dict)` | `Serializer` làm tự động, gọn   |
| Validation                          | Tự viết tay                        | Tích hợp trong `Serializer`     |
| Renderer / Browsable API            | Không                              | Có (JSON + giao diện duyệt API) |
| Status codes tiện lợi               | Không (tự nhập số)                 | Có `rest_framework.status`      |
| Mở rộng (Auth, Pagination, Filters) | Thủ công                           | Có sẵn hệ sinh thái DRF         |

---

## 7) Mở rộng nhanh (tuỳ chọn)

### 7.1) Tách chi tiết 1 Student (`/students/<pk>/`)

```python
@api_view(['GET'])
def student_detail_view(request, pk):
    from django.shortcuts import get_object_or_404
    student = get_object_or_404(Student, pk=pk)
    serializer = StudentSerializer(student)
    return Response(serializer.data, status=status.HTTP_200_OK)
```

**`students/urls.py`**

```python
from django.urls import path
from .views import students_view, student_detail_view

urlpatterns = [
    path('', students_view, name='students-list-create'),
    path('<int:pk>/', student_detail_view, name='student-detail'),
]
```

### 7.2) Dùng Class-Based View (Generic)

```python
from rest_framework import generics
from .models import Student
from .serializers import StudentSerializer

class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all().order_by('id')
    serializer_class = StudentSerializer
```

> Ưu điểm: **ít code**, tích hợp pagination/filters dễ dàng.

---

## 8) Lỗi thường gặp & cách xử lý

- **Quên `safe=False` khi trả `list` bằng `JsonResponse`**
  → `JsonResponse([...], safe=False)`.
- **Thiếu `many=True` khi serialize list**
  → `StudentSerializer(queryset, many=True)`.
- **Trùng `student_id`** khi thêm mới
  → Thêm `unique=True` + xử lý `serializer.errors`.
- **Chưa thêm app vào `INSTALLED_APPS`**
  → DRF/Model không hoạt động, kiểm tra `settings.py`.
- **Quên migrate**
  → Chạy `makemigrations` + `migrate`.

---

## 9) Kết luận (Checklist)

- [x] Tạo Model `Student` (+ `unique` cho `student_id`).
- [x] Đăng ký Admin, seed dữ liệu nhanh.
- [x] Hiển thị JSON:

  - Cách 1: `JsonResponse` (+ `values()` + `safe=False`).
  - Cách 2: **DRF + Serializer** (**khuyên dùng**).

- [x] Tạo endpoint:

  - `GET /students/` → danh sách
  - `POST /students/` → tạo mới
  - `GET /students/<pk>/` → chi tiết (tuỳ chọn)

- [x] Hiểu vai trò `Serializer` trong chuyển đổi & validation.

---

## Phụ lục: Cấu trúc thư mục mẫu

```
myproject/
├─ myproject/
│  ├─ settings.py
│  └─ urls.py
├─ students/
│  ├─ admin.py
│  ├─ models.py
│  ├─ serializers.py
│  ├─ views.py
│  └─ urls.py
└─ manage.py
```

---

Muốn mình **bổ sung tính năng Update/Delete (PUT/PATCH/DELETE)** và **pagination + filter theo `branch`** ở bài tiếp theo không? Mình sẽ giữ đúng style tài liệu như trên để bạn học liên tục.
