Dưới đây là **tài liệu Markdown (Notion-ready)** cho lesson về **generics** trong Django REST Framework, dựa trên code bạn đưa:

---

# 📘 Lesson: DRF Generics — `ListCreateAPIView` & `RetrieveUpdateDestroyAPIView`

> Mục tiêu: Dùng **generic class-based views** để build CRUD nhanh, chuẩn REST, ít code hơn so với `APIView` hoặc `mixins + GenericAPIView`.

---

## 1) Khái niệm nhanh

- **GenericAPIView + Mixins** đã được DRF đóng gói sẵn thành **Generics**:

  - `ListCreateAPIView` = `GenericAPIView` + (`ListModelMixin`, `CreateModelMixin`)
  - `RetrieveUpdateDestroyAPIView` = `GenericAPIView` + (`RetrieveModelMixin`, `UpdateModelMixin`, `DestroyModelMixin`)

- Ưu điểm:

  - **Ít code**, mặc định **status codes** chuẩn (201 khi tạo, 200 khi lấy/cập nhật, 204 khi xóa).
  - Tự tích hợp **pagination**, **filter**, **permissions**, **throttling** theo config DRF.

---

## 2) Code chuẩn (theo bạn đưa)

```python
# views.py
from rest_framework import generics
from .models import Employee
from .serializers import EmployeeSerializer

class Employees(generics.ListCreateAPIView):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer

class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'pk'  # (mặc định đã là 'pk'; chỉ cần đổi khi bạn dùng field khác)
```

**URLs**

```python
# employees/urls.py
from django.urls import path
from .views import Employees, EmployeeDetail

urlpatterns = [
    path('', Employees.as_view(), name='employees-list-create'),      # /employees/
    path('<int:pk>/', EmployeeDetail.as_view(), name='employee-detail')  # /employees/1/
]
```

---

## 3) Mapping HTTP → Hành vi → Status

| Endpoint           | Method | Hành vi (auto)           | Status |
| ------------------ | ------ | ------------------------ | ------ |
| `/employees/`      | GET    | List (phân trang được)   | 200    |
| `/employees/`      | POST   | Create (validate + save) | 201    |
| `/employees/<pk>/` | GET    | Retrieve                 | 200    |
| `/employees/<pk>/` | PUT    | Update toàn phần         | 200    |
| `/employees/<pk>/` | PATCH  | Partial update           | 200    |
| `/employees/<pk>/` | DELETE | Destroy                  | 204    |

> `PATCH` **được hỗ trợ sẵn**, không cần tự viết method.

---

## 4) Tuỳ biến thực chiến (ngắn gọn)

### 4.1) Lọc theo query params

```python
class Employees(generics.ListCreateAPIView):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        qs = Employee.objects.all().order_by('id')
        q = self.request.query_params.get('q')        # tìm theo tên/chức danh
        if q:
            qs = qs.filter(designation__icontains=q) | qs.filter(first_name__icontains=q)
        return qs
```

### 4.2) Pagination & Filter (global)

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}
```

```python
# views.py
class Employees(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    search_fields = ['first_name', 'last_name', 'designation', 'email']
    ordering_fields = ['id', 'first_name', 'designation']
    ordering = ['id']
```

### 4.3) Permissions (ví dụ yêu cầu đăng nhập)

```python
from rest_framework.permissions import IsAuthenticated

class Employees(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    ...
```

### 4.4) Hook lifecycle hay dùng

```python
class Employees(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def perform_create(self, serializer):
        # thêm dữ liệu phụ, hoặc gán owner = request.user
        serializer.save()
```

```python
class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
```

### 4.5) Đổi khóa tra cứu

```python
class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'slug'         # nếu dùng slug
```

```python
# urls.py
path('<slug:slug>/', EmployeeDetail.as_view(), name='employee-detail')
```

---

## 5) Test nhanh (cURL)

```bash
# List
curl -X GET http://127.0.0.1:8000/employees/

# Create
curl -X POST http://127.0.0.1:8000/employees/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Huy","last_name":"Minh","designation":"Backend Dev","email":"huy@example.com"}'

# Retrieve
curl -X GET http://127.0.0.1:8000/employees/1/

# Update (PUT)
curl -X PUT http://127.0.0.1:8000/employees/1/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Huy","last_name":"Minh","designation":"Senior Backend","email":"huy@example.com"}'

# Partial update (PATCH)
curl -X PATCH http://127.0.0.1:8000/employees/1/ \
  -H "Content-Type: application/json" \
  -d '{"designation":"Lead Backend"}'

# Delete
curl -X DELETE http://127.0.0.1:8000/employees/1/
```

---

## 6) So sánh ngắn

| Cách viết                 | Ưu             | Nhược                   | Khi dùng                  |
| ------------------------- | -------------- | ----------------------- | ------------------------- |
| `APIView`                 | Linh hoạt nhất | Nhiều code              | Custom logic phức tạp     |
| `mixins + GenericAPIView` | Gọn            | Vẫn phải map method     | CRUD chuẩn + cần tuỳ biến |
| **Generics** (bài này)    | **Gọn nhất**   | Ít “hook” hơn `APIView` | CRUD nhanh, chuẩn REST    |

---

## 7) Lỗi thường gặp

- Quên `.as_view()` trong `urls.py`.
- Không set `queryset` hoặc `serializer_class`.
- PUT gửi thiếu field → fail validation (dùng PATCH nếu cập nhật một phần).
- Nhầm `lookup_field` với kiểu param trong `urls.py`.
- Chưa bật pagination/filter/permissions trong `REST_FRAMEWORK`.

---

## 8) Checklist

- [x] `Employees: ListCreateAPIView`
- [x] `EmployeeDetail: RetrieveUpdateDestroyAPIView`
- [x] URL mapping chuẩn
- [x] Test GET/POST/PUT/PATCH/DELETE
- [x] (Optional) Pagination, Search, Ordering, Permissions
- [x] (Optional) `perform_create/update/destroy` hooks

---

Bạn muốn bài **tiếp theo** chuyển sang **ViewSet + Router** (còn gọn hơn nữa, auto route CRUD + action tùy chỉnh) không?
