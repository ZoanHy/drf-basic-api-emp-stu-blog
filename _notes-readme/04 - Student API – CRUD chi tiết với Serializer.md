Ok, mình sẽ tổng hợp lại kiến thức của **lesson này** (tạo Student và viết API cho **GET, POST, PUT, DELETE**) thành một file ghi chú học tập, có giải thích rõ ràng từng bước.

---

# 📝 Lesson: Student API – CRUD chi tiết với Serializer

## 1. Khái niệm chính

- **Serializer**: Chuyển đổi dữ liệu giữa **Python object/Model** và **JSON** (serialize và deserialize).
- **APIView function**: Định nghĩa hành vi cho từng HTTP method (`GET`, `POST`, `PUT`, `DELETE`).
- **@api_view**: Một decorator trong DRF giúp ánh xạ HTTP method đến function view.
- **status codes**:

  - `201 Created`: Tạo thành công.
  - `200 OK`: Trả dữ liệu thành công.
  - `204 No Content`: Xoá thành công, không trả dữ liệu.
  - `400 Bad Request`: Dữ liệu gửi lên sai.
  - `404 Not Found`: Không tìm thấy bản ghi.

---

## 2. Tạo mới `Student`

### Code (POST – `/api/students/`)

```python
elif request.method == "POST":
    serializer = StudentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

📌 **Ý nghĩa**:

- `serializer = StudentSerializer(data=request.data)` → lấy dữ liệu JSON client gửi lên.
- `is_valid()` → kiểm tra hợp lệ (đúng kiểu, không thiếu field).
- `save()` → tạo Student mới trong database.
- Trả về JSON của Student vừa tạo + `201 Created`.

---

## 3. Lấy chi tiết, sửa, xoá `Student`

### Code (GET, PUT, DELETE – `/api/students/<pk>/`)

```python
@api_view(['GET', 'PUT', 'DELETE'])
def studentDetailView(request: HttpRequest, pk: int):
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StudentSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

---

## 4. Giải thích từng method

### 🔹 GET (Read – lấy dữ liệu)

```python
serializer = StudentSerializer(student)
return Response(serializer.data, status=status.HTTP_200_OK)
```

- Chuyển object Student → JSON.
- Trả về thông tin chi tiết của 1 student.

---

### 🔹 PUT (Update – cập nhật dữ liệu)

```python
serializer = StudentSerializer(student, data=request.data)
if serializer.is_valid():
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)
```

- `serializer(student, data=request.data)` → nạp object cũ + dữ liệu mới.
- `save()` → cập nhật bản ghi trong DB.
- Trả JSON student sau khi update.

---

### 🔹 DELETE (Xoá dữ liệu)

```python
student.delete()
return Response(status=status.HTTP_204_NO_CONTENT)
```

- Xoá student trong DB.
- Trả về `204 No Content`.

---

## 5. Luồng API hoàn chỉnh

1. **POST** `/api/students/` → tạo mới Student.
2. **GET** `/api/students/<id>/` → lấy thông tin chi tiết.
3. **PUT** `/api/students/<id>/` → chỉnh sửa Student.
4. **DELETE** `/api/students/<id>/` → xoá Student.

---

✅ **Kết quả học được**:

- Biết cách viết API chi tiết cho một model bằng `Serializer`.
- Hiểu cách dùng `GET`, `POST`, `PUT`, `DELETE` trong DRF.
- Làm quen với `status code` trong REST API.

---

Bạn có muốn mình viết thêm **sơ đồ flow request → serializer → database** để nhìn trực quan hơn không?
