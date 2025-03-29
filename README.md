# ZOHOOR - AR API

A FastAPI-based backend service for the ZOHOOR - AR application, providing a robust API for managing customers, products, inventory, and AI-powered conversations.

## 🚀 Features

- **Authentication & Authorization**: Secure user authentication and role-based access control
- **User Management**: Handle customers and managers with separate endpoints
- **Product Management**: Comprehensive product catalog with categories and colors
- **Inventory Management**: Track inbound and outbound inventory movements
- **Address Management**: User address handling system
- **Carousel Management**: Dynamic content management for carousel displays
- **AI Conversations**: Integration with AI training and conversation management
- **Rating System**: Product rating and review functionality
- **Media Handling**: Static file serving for media content
- **Interactive Documentation**: Auto-generated API documentation with Swagger UI

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL (or your preferred database)
- Virtual environment (recommended)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd zohoor-ar
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Create a superuser:
```bash
python createsuperuser.py
```

## 🚀 Running the Application

Start the development server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

## 📁 Project Structure

```
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── database.py            # Database connection and settings
├── requirements.txt       # Project dependencies
├── pytest.ini            # Test configuration
├── Dockerfile            # Dockerfile
├── docker-compose.yml     # docker-compose.yml
├── createsuperuser.py    # Superuser creation script
│
├── routers/              # API route handlers
│   ├── auth/            # Authentication routes
│   ├── users/           # User management routes
│   ├── good/            # Product management routes
│   ├── inventory/       # Inventory management routes
│   └── ai_training/     # AI conversation routes
│
├── models/              # SQLAlchemy models
├── schemas/            # Pydantic schemas
├── crud/              # Database operations
├── services/          # Business logic
├── middleware/        # Custom middleware
├── utils/            # Utility functions
│
├── media/            # Media storage
└── test/            # Test files
```

## 🔒 Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Obtain a token using the `/auth/login` endpoint
2. Include the token in the Authorization header:
   ```
   Authorization: Bearer <your_token>
   ```

## 🧪 Testing

Run tests using pytest:
```bash
pytest
```

For test coverage report:
```bash
pytest --cov
```

## 📝 API Documentation

The API documentation is automatically generated and can be accessed at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## 📄 License

[Add your license information here]

## 👥 Authors

[Add author information here]

## 📞 Support

[Add support contact information here] 