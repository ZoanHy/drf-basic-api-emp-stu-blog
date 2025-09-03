# 📘 Lesson 2: Tạo API đơn giản trong Django

## 1. Sự khác nhau giữa Web Application Endpoint và API Endpoint

- **Web Application Endpoint**:
  Khi ta dùng cấu hình như sau:

  ```python
  path('students/', include('students.urls')),
  ```

  → URL `/students/` sẽ được map tới **ứng dụng web** (app `students`).
  → Thường sẽ trả về **HTML template** thông qua `render()`.
  → Ví dụ: Trả về danh sách sinh viên dưới dạng giao diện web.

- **API Endpoint**:
  Nếu ta tạo thêm app `api` và định nghĩa route:

  ```python
  path('api/v1/', include('api.urls')),
  ```

  → URL `/api/v1/` sẽ là **endpoint dành cho API**.
  → Dữ liệu trả về ở dạng **JSON** chứ không phải HTML.
  → Đây chính là cách xây dựng **REST API** để client (web, mobile, frontend React/Vue/Angular, …) gọi dữ liệu.

---

## 2. Ví dụ minh họa API đơn giản

Trong `api/views.py`:

```python
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse

def studentsView(request: HttpRequest):
    students = {'id': 1, 'name': 'Linh', 'age': 20}
    return JsonResponse(students)
```

- Ở đây, thay vì dùng `render()` để trả về HTML, ta dùng **`JsonResponse`**.
- `JsonResponse` sẽ tự động chuyển Python dictionary sang **JSON**.
- Khi truy cập `/api/v1/students/`, kết quả trả về:

```json
{
  "id": 1,
  "name": "Linh",
  "age": 20
}
```

---

## 3. So sánh `render()` vs `JsonResponse()`

| Tiêu chí              | `render()` (Web endpoint)          | `JsonResponse()` (API endpoint)  |
| --------------------- | ---------------------------------- | -------------------------------- |
| **Trả về**            | HTML (template)                    | JSON (data)                      |
| **Đối tượng sử dụng** | Người dùng (trình duyệt)           | Client app (web/mobile/React...) |
| **Ví dụ**             | `render(request, 'students.html')` | `return JsonResponse({...})`     |

---

## 4. Cấu trúc URL trong project

- `myproject/urls.py`

  ```python
  from django.urls import path, include

  urlpatterns = [
      path('students/', include('students.urls')),  # Web app
      path('api/v1/', include('api.urls')),         # API endpoint
  ]
  ```

- `api/urls.py`

  ```python
  from django.urls import path
  from . import views

  urlpatterns = [
      path('students/', views.studentsView, name='students-view'),
  ]
  ```

---

## ✅ Tổng kết kiến thức

1. **Web endpoint** (`students/`) → trả về HTML cho người dùng.
2. **API endpoint** (`api/v1/students/`) → trả về JSON cho ứng dụng khác gọi.
3. Sử dụng `JsonResponse` để trả dữ liệu JSON từ Django.
4. Đây là bước đầu tiên để phân biệt **Web App** và **API Service** trong Django.

---

👉 Vậy là ở Lesson 2 bạn đã hiểu: **Django có thể vừa trả về giao diện web, vừa hoạt động như API trả về JSON**.

Bạn có muốn mình làm thêm **sơ đồ so sánh Web Endpoint vs API Endpoint** (kiểu mũi tên từ client → server → response) để bạn dễ hình dung hơn không?
