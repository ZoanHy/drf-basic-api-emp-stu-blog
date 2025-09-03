Dưới đây là **tài liệu Markdown (đẹp, Notion-ready)** cho bài học về **ViewSet** và **ModelViewSet** trong Django REST Framework, dựa trên ví dụ bạn đưa ra.

---

# 📘 Lesson: ViewSet & ModelViewSet trong Django REST Framework

> Mục tiêu: Hiểu sự khác nhau giữa **`viewsets.ViewSet`** và **`viewsets.ModelViewSet`**, cách **router** tự sinh URL, cách ánh xạ **HTTP → action**, và các tuỳ biến thực chiến (permissions, filters, actions…).

---

## 1) Tổng quan nhanh

- **ViewSet**: Bạn **tự định nghĩa** các action như `list`, `create`, `retrieve`, `update`, `destroy`… và **tự xử lý** lấy object, serialize, status code.
- **ModelViewSet**: Gói sẵn tất cả CRUD (list/create/retrieve/update/partial_update/destroy) dựa trên **queryset + serializer** giống Generics → **ít code nhất**.

**So sánh tóm tắt**

| Tiêu chí      | `viewsets.ViewSet`                  | `viewsets.ModelViewSet`                                    |
| ------------- | ----------------------------------- | ---------------------------------------------------------- |
| CRUD mặc định | Không (tự viết)                     | Có (đủ list/create/retrieve/update/partial_update/destroy) |
| Cấu hình      | Linh hoạt tối đa                    | Gọn, chuẩn REST, ít code                                   |
| Khi dùng      | Logic đặc thù, flow khác CRUD chuẩn | CRUD chuẩn, mở rộng thêm action nhỏ                        |

---

## 2) Cấu hình Router (rất quan trọng)

> ViewSet và ModelViewSet thường đi **kèm router** để tự sinh routes.

```python
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewset  # là ViewSet hoặc ModelViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewset, basename='employee')  # basename cần khi không có queryset

urlpatterns = [
    path('', include(router.urls)),
]
```

**DefaultRouter** sinh thêm endpoint root; **SimpleRouter** thì đơn giản, không có root.
Các route điển hình sẽ có:

- `/employees/` → `GET: list`, `POST: create`
- `/employees/{pk}/` → `GET: retrieve`, `PUT: update`, `PATCH: partial_update`, `DELETE: destroy`

---

## 3) Ví dụ: `viewsets.ViewSet` (theo code của bạn)

```python
# views.py
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from .models import Employee
from .serializers import EmployeeSerializer

class EmployeeViewset(viewsets.ViewSet):
    def list(self, request: HttpRequest):
        queryset = Employee.objects.all()
        serializer = EmployeeSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request: HttpRequest):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request: HttpRequest, pk: int = None):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request: HttpRequest, pk: int = None):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: HttpRequest, pk: int = None):
        employee = get_object_or_404(Employee, pk=pk)
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

> 🔎 Ghi chú:
>
> - Bạn **tự xử lý** get object (`get_object_or_404`), status code, serializer.
> - Nếu cần **`PATCH`**, hãy thêm method `partial_update(self, request, pk=None)` và dùng `serializer = EmployeeSerializer(employee, data=request.data, partial=True)`.

---

## 4) Ví dụ: `viewsets.ModelViewSet` (theo code của bạn)

```python
from rest_framework import viewsets
from .models import Employee
from .serializers import EmployeeSerializer

class EmployeeViewset(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'pk'  # mặc định đã là 'pk', chỉ cần đổi khi bạn dùng field khác
```

**Đã có sẵn các action:**

- `list` → GET `/employees/`
- `create` → POST `/employees/`
- `retrieve` → GET `/employees/{pk}/`
- `update` → PUT `/employees/{pk}/`
- `partial_update` → PATCH `/employees/{pk}/`
- `destroy` → DELETE `/employees/{pk}/`

---

## 5) Tuỳ biến hữu ích (thực chiến)

### 5.1) Tối ưu truy vấn

```python
class EmployeeViewset(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('department').prefetch_related('skills')
    serializer_class = EmployeeSerializer
```

> Dùng `select_related/prefetch_related` để giảm N+1 queries.

### 5.2) Lọc, tìm kiếm, sắp xếp

```python
from rest_framework.filters import SearchFilter, OrderingFilter

class EmployeeViewset(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'designation', 'email']
    ordering_fields = ['id', 'first_name', 'designation']
    ordering = ['id']
```

- `GET /employees/?search=backend`
- `GET /employees/?ordering=first_name` hoặc `?ordering=-first_name`

### 5.3) Phân trang (global)

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}
```

### 5.4) Quyền truy cập & xác thực

```python
from rest_framework.permissions import IsAuthenticated

class EmployeeViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
```

### 5.5) Tuỳ chỉnh theo request (override hooks)

```python
class EmployeeViewset(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(designation__icontains=q)
        return qs

    def perform_create(self, serializer):
        # gán thêm dữ liệu, ví dụ: owner=self.request.user
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
```

### 5.6) Custom action với `@action`

```python
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class EmployeeViewset(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    # Action trên 1 employee (detail=True)
    @action(detail=True, methods=['post'], url_path='promote')
    def promote(self, request, pk=None):
        employee = self.get_object()
        # ... cập nhật designation, v.v.
        employee.designation = "Senior " + (employee.designation or "")
        employee.save()
        return Response({"message": "Promoted!"}, status=status.HTTP_200_OK)

    # Action trên danh sách (detail=False)
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        total = Employee.objects.count()
        return Response({"total": total}, status=status.HTTP_200_OK)
```

**Routes được sinh thêm:**

- `/employees/{pk}/promote/` (POST)
- `/employees/stats/` (GET)

---

## 6) Mapping HTTP → Action & Status (chuẩn REST)

| Endpoint           | Method | Action           | Status phổ biến  |
| ------------------ | ------ | ---------------- | ---------------- |
| `/employees/`      | GET    | `list`           | `200 OK`         |
| `/employees/`      | POST   | `create`         | `201 Created`    |
| `/employees/{pk}/` | GET    | `retrieve`       | `200 OK`         |
| `/employees/{pk}/` | PUT    | `update`         | `200 OK`         |
| `/employees/{pk}/` | PATCH  | `partial_update` | `200 OK`         |
| `/employees/{pk}/` | DELETE | `destroy`        | `204 No Content` |

---

## 7) Test nhanh (cURL)

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

# Custom action (POST /employees/1/promote/)
curl -X POST http://127.0.0.1:8000/employees/1/promote/
```

---

## 8) Lỗi thường gặp & cách né

- **Quên đăng ký router** hoặc `basename` (khi không có `queryset`) → URL không sinh ra.
- **Nhầm `lookup_field`** với kiểu param trong `urls.py` → 404.
- **Thiếu quyền / auth** nhưng vẫn gọi API → 401/403.
- **Không dùng `partial=True` khi PATCH** → validate fail vì thiếu field.
- **N+1 queries** khi list/retrieve nhiều quan hệ → dùng `select_related/prefetch_related`.

---

## 9) Checklist hoàn thành

- [x] Hiểu khác nhau giữa **ViewSet** & **ModelViewSet**.
- [x] Đăng ký **router** để tự sinh routes.
- [x] CRUD chuẩn với **ModelViewSet** (ít code).
- [x] Tuỳ biến: pagination, filter, permissions, hooks.
- [x] Tạo **custom actions** (`@action`) cho use-cases riêng.

---

Bạn muốn mình làm **bài tiếp theo** về **Router nâng cao (nested routers)** + **permission theo action** (ví dụ: list mở public, create/update/delete yêu cầu auth) + **versioning API** không? Mình sẽ giữ đúng style tài liệu này để bạn học liền mạch.
