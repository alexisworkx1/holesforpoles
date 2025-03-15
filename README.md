# Holes For Poles

A cloud automation web application built with FastAPI that provides a robust backend API for managing server configurations and authentication.

## Project Description

This project is a web-based application that allows users to manage cloud resources and server configurations. It provides a secure login system and endpoints for server status monitoring and configuration management.

Key features:
- User authentication and authorization
- Server status monitoring
- Configuration management
- Comprehensive logging system
- API endpoints for server automation tasks

## Installation Instructions

### Prerequisites

- Python 3.9+
- pip package manager

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/alexisworkx1/holesforpoles.git
   cd holesforpoles
   ```

2. Install the required packages:
   ```bash
   python -m pip install fastapi uvicorn
   ```

3. For production deployments, install additional dependencies:
   ```bash
   python -m pip install "uvicorn[standard]" python-dotenv
   ```

## Local Development Setup

### Environment Setup

1. Create a `.env` file in the project root:
   ```
   DATABASE_URL=sqlite:///./test.db
   SECRET_KEY=your_secret_key_here
   ENVIRONMENT=development
   ```

2. Start the development server:
   ```bash
   python main.py
   ```
   
   Alternatively, you can use uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

3. The server will start at `http://localhost:8000`

### Development Guidelines

- API routes are defined in the main.py file
- Use the FastAPI automatic documentation at `/docs` to test your endpoints
- Follow PEP 8 style guidelines for Python code

## API Endpoints

The application exposes the following REST API endpoints:

### General Endpoints

- `GET /`: Welcome message and basic application information
- `GET /health`: Server health status
  - Returns: `{"status": "healthy", "timestamp": "YYYY-MM-DD HH:MM:SS"}`

### Authentication Endpoints (Future Implementation)

- `POST /auth/login`: User login
- `POST /auth/register`: User registration
- `GET /auth/me`: Get current user information
- `POST /auth/refresh`: Refresh access token

### Server Management Endpoints (Future Implementation)

- `GET /server/status`: Get detailed server status
- `POST /server/config`: Update server configuration
- `GET /server/logs`: Retrieve server logs

## Deployment Instructions

### Deploying to Render.com

1. Ensure your code is pushed to GitHub:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push
   ```

2. Create a free account on [Render.com](https://render.com)

3. Create a new Web Service:
   - Connect your GitHub repository
   - Select the "holesforpoles" repository
   - Configure the service:
     - Name: holesforpoles
     - Runtime: Python 3
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. Add Environment Variables:
   - Add any required environment variables (such as `SECRET_KEY`)

5. Deploy the service:
   - Render will automatically deploy the application
   - Your app will be available at: https://holesforpoles.onrender.com

### Maintaining the Deployment

1. **Updates**: Push changes to your GitHub repository, and Render will automatically redeploy

2. **Monitoring**: Use Render's built-in logging and monitoring tools

3. **Scaling**: Upgrade your Render plan if you need more resources

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

