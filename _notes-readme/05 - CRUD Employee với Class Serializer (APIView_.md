Dưới đây là **bản tổng hợp (đẹp, Notion-ready)** về Lesson: build `Employee` list & detail bằng **Class-Based View (APIView)** trong Django REST Framework.

---

# 📘 Lesson: Employees (List/Create) & EmployeeDetail (Retrieve/Update/Delete) với `APIView`

> Mục tiêu: Hiểu rõ **Class-Based View** trong DRF, cách ánh xạ **HTTP methods → thao tác CRUD**, dùng **Serializer** để validate/convert dữ liệu, và xử lý lỗi/HTTP status chuẩn.

---

## 0) Chuẩn bị (tóm tắt)

```bash
pip install django djangorestframework
```

`settings.py`

```python
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'employees',     # app của bạn
]
```

---

## 1) Mô hình dữ liệu & Serializer (tham khảo)

> Nếu bạn đã có `Employee` rồi, có thể bỏ qua. Dưới đây là một ví dụ tối thiểu.

**`employees/models.py`**

```python
from django.db import models

class Employee(models.Model):
    first_name   = models.CharField(max_length=50)
    last_name    = models.CharField(max_length=50, blank=True)
    designation  = models.CharField(max_length=100)  # chức danh
    phone_number = models.CharField(max_length=20, blank=True)
    email        = models.EmailField(unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()
```

**`employees/serializers.py`**

```python
from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = Employee
        fields = ('id', 'first_name', 'last_name', 'full_name',
                  'designation', 'phone_number', 'email')

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
```

---

## 2) Class-Based Views với `APIView`

> Sử dụng **`APIView`** giúp bạn điều khiển chi tiết từng method (`get`, `post`, `put`, `delete`…), logic trả về `Response`, status code và lỗi.

**`employees/views.py`**

```python
from django.http import Http404
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Employee
from .serializers import EmployeeSerializer


class Employees(APIView):
    """
    GET  /employees/  -> Danh sách nhân viên
    POST /employees/  -> Tạo mới 1 nhân viên
    """

    def get(self, request: HttpRequest):
        employees = Employee.objects.all().order_by('id')
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: HttpRequest):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            # (tuỳ chọn) trả Location header
            headers = {'Location': f"/employees/{instance.pk}/"}
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetail(APIView):
    """
    GET    /employees/<pk>/ -> Lấy chi tiết 1 nhân viên
    PUT    /employees/<pk>/ -> Cập nhật toàn phần
    DELETE /employees/<pk>/ -> Xoá
    """

    def get_object(self, pk: int):
        try:
            return Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            raise Http404

    def get(self, request: HttpRequest, pk: int):
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: HttpRequest, pk: int):
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee, data=request.data)  # cập nhật toàn phần
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Gợi ý thêm PATCH nếu muốn cập nhật một phần
    # def patch(self, request: HttpRequest, pk: int):
    #     employee = self.get_object(pk)
    #     serializer = EmployeeSerializer(employee, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: HttpRequest, pk: int):
        employee = self.get_object(pk)
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

**`employees/urls.py`**

```python
from django.urls import path
from .views import Employees, EmployeeDetail

urlpatterns = [
    path('', Employees.as_view(), name='employees-list-create'),
    path('<int:pk>/', EmployeeDetail.as_view(), name='employee-detail'),
]
```

**`project/urls.py`**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('employees/', include('employees.urls')),
]
```

---

## 3) Mapping HTTP → CRUD & HTTP Status

| Method | Endpoint           | Ý nghĩa                         | Trả về (thường)           |
| ------ | ------------------ | ------------------------------- | ------------------------- |
| GET    | `/employees/`      | Lấy danh sách                   | 200 OK + JSON list        |
| POST   | `/employees/`      | Tạo mới                         | 201 Created + object JSON |
| GET    | `/employees/<pk>/` | Lấy chi tiết                    | 200 OK + object JSON      |
| PUT    | `/employees/<pk>/` | Cập nhật **toàn phần**          | 200 OK + object JSON      |
| PATCH  | `/employees/<pk>/` | Cập nhật **một phần** _(gợi ý)_ | 200 OK + object JSON      |
| DELETE | `/employees/<pk>/` | Xoá                             | 204 No Content            |

> 🔎 **Idempotency**: `GET`, `PUT`, `DELETE` là idempotent; `POST` không idempotent.
> 🧩 `PUT` yêu cầu gửi **đầy đủ** field; dùng `PATCH` nếu chỉ cập nhật một phần (`partial=True`).

---

## 4) Test nhanh (cURL)

**GET list**

```bash
curl -X GET http://127.0.0.1:8000/employees/
```

**POST tạo mới**

```bash
curl -X POST http://127.0.0.1:8000/employees/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Huy","last_name":"Minh","designation":"Backend Dev","phone_number":"0900000000","email":"huy@example.com"}'
```

**GET detail**

```bash
curl -X GET http://127.0.0.1:8000/employees/1/
```

**PUT cập nhật toàn phần**

```bash
curl -X PUT http://127.0.0.1:8000/employees/1/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Huy","last_name":"Minh","designation":"Senior Backend","phone_number":"0900000000","email":"huy@example.com"}'
```

**DELETE**

```bash
curl -X DELETE http://127.0.0.1:8000/employees/1/
```

---

## 5) Giải thích chi tiết & mẹo thực chiến

- **`APIView`**: cho quyền kiểm soát chi tiết từng method, phù hợp khi bạn muốn custom logic/tác vụ phụ (log, audit, side-effects…).

  > Nếu muốn nhanh gọn, cân nhắc **Generic Views**: `ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`.

- **`get_object` + `Http404`**: tách logic lấy 1 bản ghi; đảm bảo mọi method (GET/PUT/DELETE) dùng chung cách xử lý **not found (404)**.

- **`serializer.is_valid()`**: check dữ liệu đầu vào.

  > Shortcut: `serializer.is_valid(raise_exception=True)` để DRF tự trả 400 + error detail.

- **`many=True`**: bắt buộc khi serialize **QuerySet/list** (ví dụ list employees).

- **Status codes**:

  - 200 OK (GET/PUT/PATCH thành công)
  - 201 Created (POST tạo mới)
  - 204 No Content (DELETE thành công)
  - 400 Bad Request (validate fail)
  - 404 Not Found (không tìm thấy)

- **Location header khi POST** (tuỳ chọn): trả URL resource mới tạo → tốt cho client theo chuẩn REST.

- **PATCH vs PUT**:

  - **PUT**: cập nhật **toàn bộ** (nên gửi đủ field).
  - **PATCH**: cập nhật **một phần** (`partial=True`).

- **Bảo mật/Phân quyền** (gợi ý):

  ```python
  from rest_framework.permissions import IsAuthenticated

  class Employees(APIView):
      permission_classes = [IsAuthenticated]
      ...
  ```

  Hoặc cấu hình global trong `REST_FRAMEWORK` (`DEFAULT_PERMISSION_CLASSES`).

- **Pagination/Filter/Search**: Dùng `GenericAPIView + mixins` hoặc `ListCreateAPIView` để dùng sẵn `pagination_class`, `filter_backends`,…

---

## 6) So sánh nhanh: `APIView` vs Generics

| Tiêu chí    | `APIView`                  | Generics (`ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`) |
| ----------- | -------------------------- | -------------------------------------------------------------- |
| Mức độ code | Viết tay các method        | Rất gọn, khai báo `queryset`, `serializer_class`               |
| Linh hoạt   | Rất linh hoạt              | Linh hoạt vừa đủ (override được)                               |
| Phù hợp     | Khi cần custom logic nhiều | Khi muốn CRUD nhanh, đúng chuẩn DRF                            |

**Ví dụ Generics (rút gọn):**

```python
from rest_framework import generics
from .models import Employee
from .serializers import EmployeeSerializer

class EmployeeListCreate(generics.ListCreateAPIView):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer

class EmployeeRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
```

---

## 7) Lỗi thường gặp & cách xử lý

- **Quên `.as_view()`** ở `urls.py` → 500/TypeError.
- **Thiếu `many=True`** khi serialize list → lỗi/format không đúng.
- **PUT gửi thiếu field** → validate fail (nếu serializer yêu cầu đủ).
- **Không raise 404** → trả 500 khi object không tồn tại.
- **Quên add app/DRF vào `INSTALLED_APPS`** → serializer/browsable API không hoạt động.
- **Không trả status đúng** → client khó xử lý (ví dụ POST nên 201, DELETE nên 204).

---

## 8) Checklist hoàn thành

- [x] Model + Serializer cho `Employee`.
- [x] `Employees(APIView)`: `GET` (list), `POST` (create).
- [x] `EmployeeDetail(APIView)`: `GET` (retrieve), `PUT` (update), `DELETE` (remove).
- [x] URL mapping chuẩn.
- [x] Trả status code chính xác & xử lý 404.
- [x] Test bằng cURL/Postman.

---

Bạn muốn mình làm **phiên bản dùng Generics** + **Pagination** + **Filter theo `designation`** ở bài tiếp theo không? Mình sẽ giữ nguyên style tài liệu này để bạn học liền mạch.
