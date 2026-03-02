This service acts as the API gateway for all microservices. It now also exposes a simple role-based HTML dashboard at `/dashboard`.

- **Authentication**: uses OAuth2 password bearer tokens forwarded to the auth service.
- **Accounting**: dashboard views are logged via the audit log endpoint.

The application's FastAPI templates are located under `templates/`.

