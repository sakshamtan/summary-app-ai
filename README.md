# Summary Generator App

A full-stack application that generates summaries and bullet points from text using AI. Built with FastAPI (Python) for the backend and Next.js (React) for the frontend.

## Features

- User authentication with secure cookie-based sessions
- Text summarization using Groq's AI models
- Bullet point generation from text
- Modern, responsive UI
- Secure API endpoints with authentication

## Tech Stack

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- JWT for authentication
- Groq API for AI text processing
- SQLite database

### Frontend
- Next.js 15
- React
- TypeScript
- Axios for API calls
- Tailwind CSS for styling

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- Groq API key

## Setup Instructions

### Backend Setup

1. Create and activate a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory with:
```
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
```

4. Initialize the database:
```bash
python -c "from database import init_db; init_db()"
```

5. Start the backend server:
```bash
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /token` - Login and get authentication token
- `POST /logout` - Logout and clear session

### Text Processing
- `POST /generate-summary/` - Generate a summary from text
- `POST /generate-bullet-points/` - Generate bullet points from text

## Default User Credentials

For testing purposes, use:
- Username: `testuser`
- Password: `secret`

## Project Structure

```
summary-app/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── database.py       # Database models and setup
│   ├── requirements.txt  # Python dependencies
│   └── .env             # Environment variables
└── frontend/
    ├── src/
    │   ├── app/         # Next.js pages
    │   ├── lib/         # API client and utilities
    │   └── types/       # TypeScript type definitions
    └── package.json     # Node.js dependencies
```

## Security Features

- HTTP-only cookies for token storage
- Secure password hashing with bcrypt
- CORS protection
- JWT token validation
- Protected API endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 