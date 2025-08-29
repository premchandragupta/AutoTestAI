
# Backend (FastAPI)

Endpoints:
- POST /api/auth/token  (x-api-key header) => returns JWT
- POST /api/upload (Authorization: Bearer <token>) => upload .txt and generate test cases
- GET /api/documents/{doc_id}/testcases (protected)
- GET /api/documents/{doc_id}/export/csv (protected)
- GET /api/documents/{doc_id}/export/pdf (protected)

Notes:
- Configure DATABASE_URL, OPENAI_API_KEY, REDIS_URL, JWT_SECRET, ALLOWED_ORIGINS in env.
- Use docker-compose up --build for local development.
