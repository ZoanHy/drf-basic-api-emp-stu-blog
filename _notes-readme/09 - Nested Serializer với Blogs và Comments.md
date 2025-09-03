Dưới đây là **tài liệu Markdown (đẹp, Notion-ready)** cho bài học **Nested Serializer: Blog & Comments** trong Django REST Framework, dựa trên code bạn cung cấp và bổ sung các best-practices, ví dụ chạy thử, tối ưu hiệu năng.

---

# 📘 Lesson: Nested Serializer với `Blog` & `Comment` (DRF)

> Mục tiêu: Hiển thị **danh sách bình luận** (comments) **lồng trong** mỗi blog dùng **nested serializer**, triển khai với **Generic Views**, kèm mẹo tối ưu & cách mở rộng (nested route / writable nested).

---

## 1) Mô hình dữ liệu

**`blogs/models.py`**

```python
from django.db import models

class Blog(models.Model):
    blog_title = models.CharField(max_length=100)
    blog_body = models.TextField()

    def __str__(self):
        return self.blog_title

class Comment(models.Model):
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name='comments'  # 👈 rất quan trọng cho nested
    )
    comment = models.TextField()

    def __str__(self):
        return self.comment
```

**Giải thích nhanh**

- `related_name='comments'`: cho phép truy cập `blog.comments` (reverse relation).
- Khi serialize `Blog`, ta có thể thêm field `comments = CommentSerializer(many=True)` để **lồng danh sách comment** vào Blog.

> Chạy migration:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 2) Serializers (Nested)

**`blogs/serializers.py`**

```python
from rest_framework import serializers
from .models import Blog, Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'   # id, blog, comment

class BlogSerializer(serializers.ModelSerializer):
    # Lấy từ related_name='comments' trên model Comment
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = '__all__'   # id, blog_title, blog_body, comments
```

**Giải thích**

- `comments = CommentSerializer(many=True, read_only=True)`:

  - **many=True** vì là **danh sách** comment.
  - **read_only=True**: chỉ **đọc** (hiển thị) — **không** tạo/sửa comment thông qua `BlogSerializer`.
    (Cách tạo/sửa comment sẽ dùng endpoint riêng hoặc chuyển sang “writable nested” – phần mở rộng bên dưới.)

---

## 3) Views & URLs (Generics)

**`blogs/views.py`**

```python
from rest_framework import generics
from .models import Blog, Comment
from .serializers import BlogSerializer, CommentSerializer

class BlogsView(generics.ListCreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

class CommentsView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
```

**`project/urls.py` hoặc `blogs/urls.py`**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('blogs/', views.BlogsView.as_view()),
    path('comments/', views.CommentsView.as_view()),
]
```

> Khi gọi `GET /blogs/`, mỗi blog sẽ có **mảng `comments`** lồng trong JSON trả về.

---

## 4) Kết quả mong đợi

**`GET /blogs/`**:

```json
[
  {
    "id": 1,
    "blog_title": "Hello DRF",
    "blog_body": "Nested serializer demo",
    "comments": [
      { "id": 10, "blog": 1, "comment": "Great post!" },
      { "id": 11, "blog": 1, "comment": "Thanks for sharing." }
    ]
  },
  {
    "id": 2,
    "blog_title": "Second post",
    "blog_body": "More content...",
    "comments": []
  }
]
```

**`POST /blogs/`** (tạo blog mới):

```json
{ "blog_title": "New Blog", "blog_body": "Body..." }
```

**`POST /comments/`** (tạo comment mới gắn vào blog `id=1`):

```json
{ "blog": 1, "comment": "Nice!" }
```

---

## 5) Tối ưu hiệu năng (tránh N+1)

Khi list blogs và kèm comments, dùng **`prefetch_related`**:

```python
class BlogsView(generics.ListCreateAPIView):
    serializer_class = BlogSerializer

    def get_queryset(self):
        # Prefetch comments để giảm số query
        return Blog.objects.all().prefetch_related('comments').order_by('id')
```

> Nếu có nhiều quan hệ sâu hơn, kết hợp `select_related` (1-1 / many-to-1) và `prefetch_related` (1-n / n-n).

---

## 6) Lọc, phân trang, sắp xếp

### 6.1) Comments theo blog (filter)

Đôi khi bạn muốn **endpoint xem comment theo blog**:

```python
# blogs/views.py
from rest_framework.exceptions import NotFound

class BlogCommentsView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        blog_id = self.kwargs.get('blog_id')
        if not Blog.objects.filter(pk=blog_id).exists():
            raise NotFound("Blog not found")
        return Comment.objects.filter(blog_id=blog_id).order_by('id')

    def perform_create(self, serializer):
        blog_id = self.kwargs.get('blog_id')
        blog = Blog.objects.get(pk=blog_id)
        serializer.save(blog=blog)
```

```python
# blogs/urls.py
urlpatterns = [
    path('blogs/', views.BlogsView.as_view()),
    path('blogs/<int:blog_id>/comments/', views.BlogCommentsView.as_view()),  # nested route
    path('comments/', views.CommentsView.as_view()),
]
```

**Ưu điểm nested route**: rõ ràng quan hệ; dễ phân trang riêng cho comments của 1 blog.

### 6.2) Pagination & Search (global)

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
# blogs/views.py
class BlogsView(generics.ListCreateAPIView):
    serializer_class = BlogSerializer
    search_fields = ["blog_title", "blog_body"]
    ordering_fields = ["id", "blog_title"]
    ordering = ["id"]

    def get_queryset(self):
        return Blog.objects.all().prefetch_related('comments')
```

> Lưu ý: **Phân trang nested comments** **trực tiếp** trong một blog là khó, thường nên tách endpoint (ví dụ `/blogs/<id>/comments/`) để phân trang riêng.

---

## 7) Writable Nested (mở rộng)

Nếu bạn muốn **tạo blog kèm comments** trong **1 request** (nested write), bỏ `read_only=True` và override `create/update` trong `BlogSerializer`:

```python
class BlogSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, required=False)

    class Meta:
        model = Blog
        fields = ('id', 'blog_title', 'blog_body', 'comments')

    def create(self, validated_data):
        comments_data = validated_data.pop('comments', [])
        blog = Blog.objects.create(**validated_data)
        for cdata in comments_data:
            Comment.objects.create(blog=blog, **cdata)
        return blog

    def update(self, instance, validated_data):
        comments_data = validated_data.pop('comments', None)
        instance.blog_title = validated_data.get('blog_title', instance.blog_title)
        instance.blog_body = validated_data.get('blog_body', instance.blog_body)
        instance.save()

        # Tuỳ chiến lược: clear & recreate, hoặc merge cập nhật
        if comments_data is not None:
            instance.comments.all().delete()
            for cdata in comments_data:
                Comment.objects.create(blog=instance, **cdata)
        return instance
```

> ⚠️ Cân nhắc: Nested write phức tạp về logic (thêm/sửa/xoá từng comment). Nhiều team chọn **không** hỗ trợ nested write mà tách **endpoint riêng** cho comments (đơn giản, dễ phân trang & kiểm soát hơn).

---

## 8) Một số mẹo trình bày dữ liệu

### 8.1) `comment_count`

Bạn có thể thêm **tổng số bình luận** để hiển thị nhanh:

```python
class BlogSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Blog
        fields = ('id', 'blog_title', 'blog_body', 'comment_count', 'comments')
```

### 8.2) Chỉ lấy N comment gần nhất

```python
class BlogSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = ('id', 'blog_title', 'blog_body', 'comments')

    def get_comments(self, obj):
        qs = obj.comments.order_by('-id')[:3]  # lấy 3 comment mới nhất
        return CommentSerializer(qs, many=True).data
```

---

## 9) cURL test nhanh

```bash
# Tạo blog
curl -X POST http://127.0.0.1:8000/blogs/ \
  -H "Content-Type: application/json" \
  -d '{"blog_title":"Hello DRF","blog_body":"Nested demo"}'

# Tạo comment cho blog id=1
curl -X POST http://127.0.0.1:8000/comments/ \
  -H "Content-Type: application/json" \
  -d '{"blog":1,"comment":"Great post!"}'

# Hoặc dùng nested route
curl -X POST http://127.0.0.1:8000/blogs/1/comments/ \
  -H "Content-Type: application/json" \
  -d '{"comment":"Via nested route"}'

# Lấy danh sách blog (kèm comments)
curl -X GET http://127.0.0.1:8000/blogs/
```

---

## 10) Lỗi thường gặp & cách né

- **Quên `related_name`** hoặc sai tên → `BlogSerializer` không gọi được `comments`.
- **Quên `many=True`** trong nested → serializer lỗi hoặc trả sai định dạng.
- **N+1 queries** khi list nhiều blog và comments → dùng `prefetch_related('comments')`.
- **Muốn phân trang comments ngay trong blog list** → khó; nên tách route `/blogs/<id>/comments/`.
- **Writable nested** không rõ chiến lược (merge/replace) → dễ lỗi dữ liệu; cân nhắc giữ **read-only** và dùng endpoint riêng để CRUD comment.

---

## ✅ Tổng kết

- **Nested serializer** cho phép **hiển thị** quan hệ 1-n rất tiện (Blog → Comments).
- Dùng `related_name` + `CommentSerializer` lồng trong `BlogSerializer` để render comments.
- **Best practice**: read-only nested để đọc; **CRUD comments** qua endpoint riêng hoặc nested route.
- Tối ưu với `prefetch_related`, cân nhắc phân trang/tìm kiếm/sắp xếp qua endpoint riêng.
- Có thể nâng cấp lên **writable nested** nếu thực sự cần, nhưng phải kiểm soát kỹ logic.

---

Bạn muốn mình làm **phiên bản dùng ViewSet + Router (kèm custom nested route)** cho `blogs/{id}/comments/` và ví dụ **permissions** khác nhau cho blog vs comment ở bài tiếp theo không?
