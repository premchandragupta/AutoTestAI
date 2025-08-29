
INSERT INTO users (username, email, api_key) VALUES ('demo', 'demo@example.com', 'demo-api-key-12345') ON CONFLICT DO NOTHING;

INSERT INTO documents (user_id, filename, content) VALUES
(1, 'login_requirements.txt', 'The application shall allow users to login using email and password. Password must be at least 8 characters. After 5 failed attempts account is locked for 30 minutes.');

INSERT INTO test_cases (document_id, title, description, type, steps, expected_result)
VALUES
(1, 'Valid Login', 'User can login with valid credentials', 'positive', '1. Go to login. 2. Enter valid credentials. 3. Submit.', 'User is logged in and redirected.');
