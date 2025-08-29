
# SOP: Deploy AutoTestAI to Supabase + Render + Vercel
1. Push repo to GitHub.
2. Create Supabase project, get DATABASE_URL, run database/schema.sql and database/seed_supabase.sql in SQL editor.
3. Create Render Web Service for backend, set environment variables: DATABASE_URL, OPENAI_API_KEY, REDIS_URL, JWT_SECRET, ALLOWED_ORIGINS.
4. Create Vercel project for frontend, set VITE_BACKEND_URL to backend URL.
5. Add GitHub Secrets: RENDER_API_KEY, RENDER_SERVICE_ID, VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID
6. Push to main branch; Actions will build. Use Render API or integrate deploy step to trigger.
