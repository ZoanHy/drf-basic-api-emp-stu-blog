Dưới đây là **bài học (Notion-ready)** về **Pagination trong Django REST Framework (DRF)**: gồm cấu hình **global**, **cách gọi trong view/generics/viewset**, và **viết Custom Pagination** với response tuỳ biến.

---

# 📘 Lesson: DRF Pagination (Global & Custom)

> Mục tiêu: Hiểu 3 kiểu phân trang hay dùng (**PageNumber**, **LimitOffset**, **Cursor**) và cách **viết CustomPagination** để kiểm soát query params + cấu trúc JSON trả về.

---

## 1) Vì sao cần Pagination?

- Giảm tải dữ liệu trả về mỗi request → **nhanh hơn**, **ít RAM**.
- Trải nghiệm tốt hơn cho UI: **infinite scroll**, **next/prev**, **page số**.
- Dễ kết hợp với **search**, **ordering**, **filter**.

---

## 2) Cấu hình Global Pagination

> Cấu hình trong `settings.py` để áp dụng mặc định cho **mọi** view hỗ trợ pagination (ví dụ ListAPIView, ListCreateAPIView, ViewSet list).

### 2.1) LimitOffsetPagination (phù hợp infinite scroll, load-more)

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 2,  # default limit nếu client không truyền ?limit=
}
```

- Query params mặc định:

  - `?limit=2&offset=0` → trang đầu
  - `?limit=2&offset=2` → trang kế tiếp

- Ưu điểm: linh hoạt “nhảy” đến bất kỳ vị trí nào; hợp với **load-more**.
- Nhược: offset lớn → query **chậm** khi dữ liệu cực lớn.

### 2.2) PageNumberPagination (phù hợp danh sách có số trang)

```python
# settings.py
# REST_FRAMEWORK = {
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'PAGE_SIZE': 2,
# }
```

- Query param mặc định: `?page=1`, `?page=2`, …
- Ưu điểm: thân thiện người dùng (số trang).
- Nhược: khó “điều hướng” chính xác nếu nội dung thay đổi liên tục.

> 🔎 **Ghi nhớ**: Pagination **trên từng view** (qua `pagination_class`) sẽ **ghi đè** cấu hình global.

---

## 3) Custom Pagination (PageNumberPagination)

> Tạo file `pagination.py` (ví dụ trong app `api/`), viết class kế thừa **PageNumberPagination** và **tuỳ biến query params + response**.

```python
# api/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'page_size'  # client có thể đổi page size: ?page_size=5
    page_query_param = 'page_num'        # đổi tên 'page' -> 'page_num'
    max_page_size = 1                    # giới hạn tối đa mỗi trang (demo)

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'page_size': self.page_size,
            'results': data
        })
```

> 💡 **Lưu ý**
>
> - `max_page_size = 1` chỉ là **ví dụ demo**; thực tế bạn nên đặt giá trị hợp lý (ví dụ 50, 100) để tránh client kéo quá nặng.
> - `page_query_param = 'page_num'` giúp bạn **đổi** tên param cho phù hợp UI/FE.

**Cách dùng trong view (generics hoặc viewset):**

```python
# views.py
from rest_framework import generics, viewsets
from .pagination import CustomPagination
from .models import Employee
from .serializers import EmployeeSerializer

class EmployeesView(generics.ListCreateAPIView):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer
    pagination_class = CustomPagination   # 👈 ghi đè global

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer
    pagination_class = CustomPagination   # 👈 cũng tương tự
```

**Gọi API mẫu:**

```
GET /employees/?page_num=1&page_size=1
```

**Response mẫu:**

```json
{
  "next": "http://127.0.0.1:8000/employees/?page_num=2&page_size=1",
  "previous": null,
  "count": 5,
  "page_size": 1,
  "results": [
    { "id": 1, "first_name": "Huy", "last_name": "Minh", "...": "..." }
  ]
}
```

---

## 4) So sánh nhanh các kiểu Pagination

| Kiểu                      | Query params              | Ưu                                          | Nhược                                               | Dùng khi                           |
| ------------------------- | ------------------------- | ------------------------------------------- | --------------------------------------------------- | ---------------------------------- |
| **PageNumberPagination**  | `?page=2` (hoặc tuỳ biến) | Dễ hiểu với người dùng                      | Trang có thể lệch nếu dữ liệu thay đổi              | Danh sách ổn định, UI có số trang  |
| **LimitOffsetPagination** | `?limit=20&offset=40`     | Linh hoạt “nhảy” vị trí                     | Offset lớn chậm trên bảng rất to                    | Infinite scroll, load-more         |
| **CursorPagination**      | `?cursor=...`             | Ổn định với dữ liệu thay đổi; hiệu năng tốt | Khó debug/nhảy tùy ý; cần trường `ordering` cố định | Feeds thời gian thực, chat, stream |

> **CursorPagination (bonus)**
>
> ```python
> from rest_framework.pagination import CursorPagination
> class FeedCursorPagination(CursorPagination):
>     page_size = 20
>     ordering = '-created_at'  # cần trường sắp xếp ổn định/unique
> ```
>
> - Ưu điểm: tránh vấn đề “lệch trang” khi dữ liệu thêm/xoá liên tục.
> - Nhược: không nhảy đến trang số tuỳ ý.

---

## 5) Mẹo hiệu năng & trải nghiệm

- **Luôn `order_by()`** trong queryset khi phân trang để kết quả **ổn định**, ví dụ: `.order_by('id')` hoặc theo `-created_at`.
- Với **list dữ liệu lớn** + **LimitOffset**, chú ý chi phí `COUNT(*)`; có thể cache tổng count hoặc chuyển sang **CursorPagination** cho feed thay đổi nhiều.
- Kết hợp **prefetch/select_related** để hạn chế **N+1 queries** khi serialize nested:

  ```python
  queryset = Blog.objects.all().prefetch_related('comments')
  ```

- Cho phép client điều chỉnh page size nhưng **giới hạn `max_page_size`** để bảo vệ server.
- Muốn **tắt pagination** cho một view:

  ```python
  pagination_class = None
  ```

---

## 6) Test nhanh (cURL)

### 6.1) LimitOffsetPagination (global)

```bash
curl -X GET "http://127.0.0.1:8000/employees/?limit=2&offset=0"
curl -X GET "http://127.0.0.1:8000/employees/?limit=2&offset=2"
```

### 6.2) CustomPagination (PageNumber, đổi tên param)

```bash
curl -X GET "http://127.0.0.1:8000/employees/?page_num=1&page_size=1"
curl -X GET "http://127.0.0.1:8000/employees/?page_num=2&page_size=1"
```

---

## 7) Lỗi thường gặp & cách né

- **Không `order_by` ổn định** → trang 1/2… trả về kết quả “nhảy lung tung”.
- **Đặt `max_page_size` quá nhỏ/lớn** → hoặc gây khó test, hoặc server bị “oằn”.
- Quên gán `pagination_class` trên view khi muốn **ghi đè global**.
- Dùng PageNumber nhưng UI lại truyền `limit/offset` (hoặc ngược lại) → **không có tác dụng**.
- Dataset cực lớn + LimitOffset → `offset` lớn sẽ chậm → cân nhắc **CursorPagination**.

---

## 8) Checklist

- [x] Cấu hình **global pagination** (LimitOffset / PageNumber).
- [x] Viết **CustomPagination**: `page_num`, `page_size`, `get_paginated_response`.
- [x] Gắn `pagination_class` vào **generics/viewset**.
- [x] Thử với query params, kiểm tra **next/previous/count**.
- [x] Áp dụng **order_by** + tối ưu **N+1**.
- [x] Biết khi nào dùng **CursorPagination**.

---

Bạn muốn mình làm **demo CursorPagination** (tạo field `created_at`, sắp xếp ổn định, và ví dụ response có `cursor`) ở bài tiếp theo không?
