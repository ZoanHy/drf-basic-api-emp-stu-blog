Dưới đây là **tài liệu Markdown (đẹp, Notion-ready)** cho bài học về **mixins** và **generic views** trong Django REST Framework, dựa trên code bạn đưa ra. Copy nguyên khối để dùng làm README/notes học tập.

---

# 📘 Lesson: DRF Mixins & GenericAPIView cho Employees

> Mục tiêu: Hiểu cơ chế **mixins** + **GenericAPIView** để xây nhanh các endpoint **List/Create** và **Retrieve/Update/Destroy** cho `Employee`.

---

## 1) Tư duy tổng quát

- **`GenericAPIView`**: cung cấp “xương sống” cho view (quản lý `queryset`, `serializer_class`, `get_object()`, phân trang, filter…).
- **`mixins.*`**: cung cấp **hành vi (action)** sẵn có như:

  - `ListModelMixin` → `.list(request, *args, **kwargs)`
  - `CreateModelMixin` → `.create(request, *args, **kwargs)`
  - `RetrieveModelMixin` → `.retrieve(request, *args, **kwargs)`
  - `UpdateModelMixin` → `.update(request, *args, **kwargs)` & `.partial_update(...)`
  - `DestroyModelMixin` → `.destroy(request, *args, **kwargs)`

- Bạn **ánh xạ HTTP method → mixin method** (ví dụ: `GET` → `.list()` hoặc `.retrieve()`, `POST` → `.create()`, `PUT` → `.update()`, `DELETE` → `.destroy()`).

---

## 2) Code mẫu (theo bạn đưa)

```python
# views.py
from django.http import HttpRequest
from rest_framework import mixins, generics, status
from rest_framework.response import Response
from .models import Employee
from .serializers import EmployeeSerializer


class Employees(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get(self, request: HttpRequest):
        return self.list(request)          # GET /employees/ → list

    def post(self, request: HttpRequest):
        return self.create(request)        # POST /employees/ → create


class EmployeeDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get(self, request: HttpRequest, pk: int):
        return self.retrieve(request, pk=pk)    # GET /employees/<pk>/ → detail

    def put(self, request: HttpRequest, pk: int):
        return self.update(request, pk=pk)      # PUT /employees/<pk>/ → update toàn phần

    def delete(self, request: HttpRequest, pk: int):
        return self.destroy(request, pk=pk)     # DELETE /employees/<pk>/ → xoá
```

**URLs**

```python
# employees/urls.py
from django.urls import path
from .views import Employees, EmployeeDetail

urlpatterns = [
    path('', Employees.as_view(), name='employees-list-create'),
    path('<int:pk>/', EmployeeDetail.as_view(), name='employee-detail'),
]
```

> ✅ **Hoạt động vì**: `GenericAPIView` hiểu `lookup_field='pk'` mặc định, nên khi bạn gọi `self.retrieve(request, pk=pk)` (hoặc `update/destroy`) nó tìm object theo `pk` trong `queryset`.

---

## 3) Mapping HTTP → Action & Status

| Endpoint           | Method | Action (mixin)      | Status thường dùng         |
| ------------------ | -----: | ------------------- | -------------------------- |
| `/employees/`      |    GET | `.list()`           | `200 OK`                   |
| `/employees/`      |   POST | `.create()`         | `201 Created` (thành công) |
| `/employees/<pk>/` |    GET | `.retrieve()`       | `200 OK`                   |
| `/employees/<pk>/` |    PUT | `.update()`         | `200 OK`                   |
| `/employees/<pk>/` |  PATCH | `.partial_update()` | `200 OK`                   |
| `/employees/<pk>/` | DELETE | `.destroy()`        | `204 No Content`           |

> 💡 Thêm **PATCH** nhanh:
>
> ```python
> def patch(self, request, pk: int):
>     return self.partial_update(request, pk=pk)
> ```

---

## 4) Tuỳ biến quan trọng (thực chiến)

### 4.1) `lookup_field` & `lookup_url_kwarg`

- Dùng khi khoá tra cứu không phải `pk` (ví dụ `slug`, `code`).

```python
class EmployeeDetail(...):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'slug'            # tìm theo slug
    lookup_url_kwarg = 'employee_slug'
```

```python
# urls.py
path('<slug:employee_slug>/', EmployeeDetail.as_view())
```

### 4.2) Phân trang (Pagination)

- **Global** trong `settings.py`:

```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}
```

- **Hoặc cục bộ**:

```python
from rest_framework.pagination import PageNumberPagination

class DefaultPagination(PageNumberPagination):
    page_size = 10

class Employees(...):
    pagination_class = DefaultPagination
```

> `ListModelMixin` sẽ tự gọi `.paginate_queryset()` và `.get_paginated_response()`.

### 4.3) Tìm kiếm & Sắp xếp (Search/Ordering)

```python
from rest_framework.filters import SearchFilter, OrderingFilter

class Employees(...):
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'designation', 'email']
    ordering_fields = ['id', 'first_name', 'designation', 'email']
    ordering = ['id']
```

- Dùng query:

  - `GET /employees/?search=backend`
  - `GET /employees/?ordering=first_name` (tăng dần), `?ordering=-first_name` (giảm dần)

### 4.4) Quyền truy cập (Permissions) & Auth

```python
from rest_framework.permissions import IsAuthenticated

class Employees(...):
    permission_classes = [IsAuthenticated]
```

> Có thể cấu hình global trong `REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"]`.

### 4.5) Tuỳ biến `get_queryset` / `get_serializer_class`

```python
class Employees(...):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        qs = Employee.objects.all()
        branch = self.request.query_params.get('branch')
        if branch:
            qs = qs.filter(designation__icontains=branch)
        return qs
```

---

## 5) So sánh 3 cách viết View

| Cách                                                                          | Độ gọn      | Linh hoạt | Khi dùng                       |
| ----------------------------------------------------------------------------- | ----------- | --------- | ------------------------------ |
| `APIView` thuần                                                               | Trung bình  | Rất cao   | Khi muốn kiểm soát mọi thứ     |
| `mixins + GenericAPIView`                                                     | Gọn         | Cao       | CRUD chuẩn + còn muốn tuỳ biến |
| **Generics “đóng gói”** (`ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`) | **Rất gọn** | Vừa đủ    | CRUD nhanh, chuẩn REST         |

**Tương đương Generics (ngắn gọn hơn):**

```python
from rest_framework import generics

class Employees(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
```

---

## 6) Test nhanh (cURL)

```bash
# List
curl -X GET http://127.0.0.1:8000/employees/

# Create
curl -X POST http://127.0.0.1:8000/employees/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Huy","last_name":"Minh","designation":"Backend Dev","phone_number":"0900000000","email":"huy@example.com"}'

# Retrieve
curl -X GET http://127.0.0.1:8000/employees/1/

# Update (PUT toàn phần)
curl -X PUT http://127.0.0.1:8000/employees/1/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Huy","last_name":"Minh","designation":"Senior Backend","phone_number":"0900000000","email":"huy@example.com"}'

# Partial update (PATCH)
curl -X PATCH http://127.0.0.1:8000/employees/1/ \
  -H "Content-Type: application/json" \
  -d '{"designation":"Lead Backend"}'

# Delete
curl -X DELETE http://127.0.0.1:8000/employees/1/
```

---

## 7) Lỗi thường gặp & cách né

- **Quên `.as_view()`** trong `urls.py` → lỗi `TypeError`.
- **Nhầm `lookup_field`/`lookup_url_kwarg`** → 404 dù data có thật.
- **PUT thiếu trường** (toàn phần) → validate fail; dùng PATCH cho cập nhật một phần.
- **Không cấu hình pagination/filter** mà gọi query params → không có tác dụng.
- **Thiếu `serializer_class`/`queryset`** → mixins không hoạt động.

---

## 8) Checklist hoàn thành

- [x] Hiểu `GenericAPIView` + mixins action.
- [x] `Employees` dùng `ListModelMixin` + `CreateModelMixin`.
- [x] `EmployeeDetail` dùng `Retrieve` + `Update` + `Destroy`.
- [x] Thêm **PATCH** (optional).
- [x] URLs chuẩn.
- [x] (Optional) Pagination, Search, Ordering, Permissions.

---

Bạn muốn mình **nâng cấp lên ViewSet + Router** ở bài tiếp theo (càng gọn hơn nữa, 1 class quản hết CRUD, auto route) không? Mình sẽ giữ nguyên style này để học liền mạch.
