# Django REST Framework Basic API Project

This project demonstrates how to build RESTful APIs using Django REST Framework (DRF). It includes multiple examples of API implementations with different approaches and features.

## Features

- CRUD operations with different DRF approaches
- Multiple model implementations (Students, Employees, Blogs)
- Different view implementations (APIView, Generic Views, ViewSets)
- Advanced features like pagination, filtering, and nested serializers

## Project Structure

```
├── api/                    # Main API application
├── students/              # Student management API
├── employees/            # Employee management API
├── blogs/               # Blog and comments API with nested relations
└── django_rest_main/   # Project settings and main URLs
```

## Models

### Student

- student_id (CharField)
- name (CharField)
- branch (CharField)

### Employee

- emp_id (CharField)
- emp_name (CharField)
- designation (CharField)

### Blog

- blog_title (CharField)
- blog_body (TextField)
- comments (One-to-Many relation with Comment model)

### Comment

- blog (ForeignKey to Blog)
- comment (TextField)

## API Implementations

This project showcases different ways to implement APIs in Django REST Framework:

1. **Basic API Views** (Students App)

   - Function-based views
   - Basic CRUD operations
   - Custom serializer implementation

2. **Class-based Views** (Employees App)

   - APIView implementation
   - Mixins and Generics
   - ViewSet and ModelViewSet

3. **Advanced Features** (Blogs App)

   - Nested serializers for related models
   - Handling relationships (One-to-Many)

4. **Additional Features**
   - Pagination
   - Filtering
   - Custom serializers

## Setup and Installation

1. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install django djangorestframework
   ```

3. Run migrations:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Students API

- `GET /api/students/` - List all students
- `POST /api/students/` - Create a new student
- `GET /api/students/{id}/` - Retrieve a student
- `PUT /api/students/{id}/` - Update a student
- `DELETE /api/students/{id}/` - Delete a student

### Employees API

- `GET /api/employees/` - List all employees
- `POST /api/employees/` - Create a new employee
- `GET /api/employees/{id}/` - Retrieve an employee
- `PUT /api/employees/{id}/` - Update an employee
- `DELETE /api/employees/{id}/` - Delete an employee

### Blogs API

- `GET /api/blogs/` - List all blogs with comments
- `POST /api/blogs/` - Create a new blog
- `GET /api/blogs/{id}/` - Retrieve a blog with its comments
- `PUT /api/blogs/{id}/` - Update a blog
- `DELETE /api/blogs/{id}/` - Delete a blog

## Features Demonstrated

1. **Serialization**

   - Model Serializers
   - Nested Serializers
   - Custom field mappings

2. **Views**

   - Function Based Views
   - Class Based Views
   - Generic Views
   - ViewSets

3. **Advanced Features**
   - Pagination
   - Filtering
   - Nested Resources
   - Relationships

## Contributing

Feel free to contribute to this project by:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is open-sourced under the MIT license.
