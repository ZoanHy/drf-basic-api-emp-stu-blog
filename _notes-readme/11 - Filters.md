Dưới đây là **bài học (Notion-ready)** về **Filtering trong Django REST Framework (DRF)**, gồm: cài đặt global, dùng **django-filter** với `FilterSet` tùy biến (id range), kết hợp **Search/Ordering** tích hợp sẵn của DRF, ví dụ URL query và lỗi thường gặp.

---

# 📘 Lesson: DRF Filtering — `django-filter`, Search, Ordering

> Mục tiêu:
>
> - Bật **lọc** theo field qua query params (ví dụ `?designation=Dev&emp_name=huy`).
> - Tạo **filter tùy biến** (lọc theo khoảng id).
> - Kết hợp **search** toàn văn bản và **ordering**.

---

## 1) Cài đặt & cấu hình cơ bản

### 1.1) Cài gói & khai báo app

```bash
pip install django-filter
```

`settings.py`

```python
INSTALLED_APPS = [
    ...,
    'django_filters',  # 👈 bắt buộc khi dùng django-filter
]
```

### 1.2) Bật filter backend + đổi tên query params (tùy chọn)

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'  # dùng FilterSet
    ],
    'SEARCH_PARAM': 'q',          # mặc định là 'search'
    'ORDERING_PARAM': 'order-by', # mặc định là 'ordering'
}
```

---

## 2) Khai báo `FilterSet` (django-filter)

Ví dụ model (tham khảo):

```python
# employees/models.py
from django.db import models

class Employee(models.Model):
    emp_id = models.IntegerField(unique=True)   # ID nội bộ (khác pk tự tăng)
    emp_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    ...
```

`FilterSet` tùy biến:

```python
# employees/filters.py
import django_filters
from .models import Employee

class EmployeeFilter(django_filters.FilterSet):
    # Lọc theo tên (chứa, không phân biệt hoa thường)
    emp_name   = django_filters.CharFilter(field_name='emp_name', lookup_expr='icontains')
    # Lọc theo chức danh (so khớp chính xác, không phân biệt hoa thường)
    designation = django_filters.CharFilter(field_name='designation', lookup_expr='iexact')

    # Cách 1 (gợi ý, gọn gàng): dùng RangeFilter cho số
    # emp_id = django_filters.RangeFilter(field_name='emp_id')

    # Cách 2 (theo ví dụ của bạn): hai tham số min/max + method tùy biến
    id_min = django_filters.NumberFilter(method='filter_by_id_range', label='From EMP ID')
    id_max = django_filters.NumberFilter(method='filter_by_id_range', label='To EMP ID')

    class Meta:
        model = Employee
        fields = ['designation', 'emp_name', 'id_min', 'id_max']  # hoặc 'emp_id' nếu dùng RangeFilter

    def filter_by_id_range(self, queryset, name, value):
        # name == 'id_min' hoặc 'id_max'
        if name == 'id_min':
            return queryset.filter(emp_id__gte=value)
        elif name == 'id_max':
            return queryset.filter(emp_id__lte=value)
        return queryset
```

> 🔎 **Giải thích & lưu ý**
>
> - Dùng **`NumberFilter`** (hoặc `RangeFilter`) cho trường số; tránh `CharFilter` để so sánh số.
> - Nếu model **không có `emp_id`** mà chỉ có `id` (pk), hãy sửa lại `field_name` thành `id` tương ứng.
> - `RangeFilter` cho phép gọi: `?emp_id_min=…&emp_id_max=…` qua 1 param duy nhất `emp_id_min/emp_id_max` nếu bạn cấu hình theo tài liệu, hoặc dùng `?emp_id_min=&emp_id_max=` theo cách custom. Cách ở trên cho bạn 2 param tách bạch `id_min` và `id_max`.

---

## 3) Gắn Filter vào View (Generics/ViewSet)

### 3.1) Dùng FilterSet (lọc theo field cụ thể)

```python
# employees/views.py
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee
from .serializers import EmployeeSerializer
from .filters import EmployeeFilter

class EmployeesView(generics.ListAPIView):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend]  # có thể để global trong settings
    filterset_class = EmployeeFilter         # 👈 dùng FilterSet custom
```

**Ví dụ gọi API:**

```
/employees/?emp_name=huy&designation=dev
/employees/?id_min=100&id_max=200
```

### 3.2) Dùng **Search** & **Ordering** (DRF built-ins)

```python
from rest_framework.filters import SearchFilter, OrderingFilter

class BlogListView(generics.ListAPIView):
    queryset = Blog.objects.all().order_by('id')
    serializer_class = BlogSerializer
    filter_backends = [SearchFilter, OrderingFilter]  # 👈 tích hợp sẵn của DRF
    search_fields = ['blog_title', 'blog_body']       # full-text basic
    ordering_fields = ['id', 'blog_title']            # các field cho phép sort
    ordering = ['id']                                 # mặc định sort

# Với settings đã đổi tên param:
#   search param  : ?q=keyword
#   ordering param: ?order-by=blog_title hoặc ?order-by=-blog_title
```

**Ví dụ gọi API:**

```
/blogs/?q=drf
/blogs/?q=serializer&order-by=-blog_title
```

> 💡 Bạn có thể **kết hợp** DjangoFilterBackend **cùng** Search/Ordering:

```python
class EmployeesView(generics.ListAPIView):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = ['emp_name', 'designation']
    ordering_fields = ['id', 'emp_id', 'emp_name']
```

---

## 4) Mẫu URL/Query thường dùng

- Lọc theo field cụ thể (FilterSet):

  - `/employees/?designation=QA`
  - `/employees/?emp_name=huy`
  - `/employees/?id_min=100&id_max=300`

- Search (fuzzy cơ bản, nhiều field):

  - `/employees/?q=backend`

- Ordering:

  - `/employees/?order-by=emp_name`
  - `/employees/?order-by=-emp_name`

> **Kết hợp**:

```
/employees/?emp_name=huy&q=backend&order-by=-emp_id&id_min=100
```

---

## 5) Mẹo thực chiến & hiệu năng

- **Index** DB cho các cột hay lọc/sort: `emp_id`, `designation`, `emp_name`…
  → tăng tốc `WHERE emp_id >= ? AND emp_id <= ?`, `ORDER BY emp_name`.
- `icontains`/`iexact` lọc text cơ bản; với dữ liệu lớn cần search nâng cao, cân nhắc:

  - **Postgres**: trigram (`pg_trgm`), full-text search.
  - Hoặc dùng thư viện search (Elastic/OpenSearch) khi nhu cầu phức tạp.

- Lọc theo quan hệ: dùng `field_name='related__field'` trong `FilterSet`.
- **Kết hợp Pagination** để tránh trả về quá nhiều dòng một lúc.
- Đặt **giới hạn** query param (whitelist fields) → an toàn & tránh query nặng bất ngờ.

---

## 6) Test nhanh (cURL)

```bash
# Lọc theo tên (icontains) + designation (iexact)
curl -X GET "http://127.0.0.1:8000/employees/?emp_name=huy&designation=dev"

# Lọc theo khoảng id
curl -X GET "http://127.0.0.1:8000/employees/?id_min=100&id_max=200"

# Search & Ordering (đã đổi tên param)
curl -X GET "http://127.0.0.1:8000/blogs/?q=drf&order-by=-blog_title"
```

---

## 7) Lỗi thường gặp & cách né

- **Mismatch field name**: `filter_by_id_range` dùng `emp_id__gte` nhưng model **không có `emp_id`** → 500.
  ✅ Sửa `emp_id` → `id` (hoặc thêm `emp_id` vào model đúng kiểu).
- **Dùng `CharFilter` cho số** → so sánh chuỗi sai (ví dụ `"100" < "20"`).
  ✅ Dùng `NumberFilter`/`RangeFilter`.
- Quên thêm `'django_filters'` vào `INSTALLED_APPS` hoặc quên filter backend → query params **không có tác dụng**.
- Quên `filter_backends` hoặc `filterset_class` trong view → filter custom **không chạy**.
- Không đặt index cho cột lọc → **chậm** khi dữ liệu lớn.

---

## ✅ Checklist

- [x] Cài `django-filter` + add `django_filters` vào `INSTALLED_APPS`.
- [x] Bật `DjangoFilterBackend` (global hoặc per-view).
- [x] Tạo `EmployeeFilter` (text, exact, **range id**).
- [x] Gắn `filterset_class` vào view.
- [x] Bật **SearchFilter/OrderingFilter** và **đổi tên param** (`q`, `order-by`) nếu muốn.
- [x] Viết ví dụ cURL & test thực tế.
- [x] Tối ưu với index & pagination.

---

Bạn muốn mình tiếp tục bài **Filtering nâng cao** (lọc theo quan hệ `department__name`, many-to-many, ngày/giờ với `DateFromToRangeFilter`, preset filtersets và docs tự động với `drf-spectacular`/`drf-yasg`) không?
