# Barbershop / Salon Booking System

A full-stack booking system for barbershops, salons, and appointment-based service businesses. The project combines a public customer booking flow, a protected admin panel, Stripe deposit payments, email confirmations, and a Telegram operations bot.

This is more than a landing page. It automates the real booking workflow: customers select a service, master, date, and available time slot; the backend validates availability and creates a Stripe PaymentIntent; confirmed payments create bookings; customers receive a manage link; and staff can operate through the admin panel or Telegram bot.

The current deployment target is a portfolio/demo environment on Railway using Docker, Stripe test mode, and SQLite with a persistent volume. For real production use, the same architecture can be extended with PostgreSQL, migrations, queue-backed notifications, monitoring, and production email infrastructure.

## Key Features

### Public Customer Flow

- Browse active services and masters.
- Select date and time from backend-calculated availability.
- Pay a deposit with Stripe PaymentElement in test mode.
- Success, delayed confirmation, and error handling after payment.
- Booking confirmation email with appointment details.
- Secure manage booking link.
- Reschedule or cancel by manage token, subject to backend cutoff rules.

### Backend

- FastAPI API with SQLAlchemy models and SQLite storage.
- Backend is the source of truth for services, masters, schedules, availability, conflicts, and payment amounts.
- Stripe PaymentIntent creation with server-side amount calculation.
- Stripe webhook route for `payment_intent.succeeded`.
- Fallback confirmation endpoint that verifies the PaymentIntent directly with Stripe if the webhook is delayed or unavailable.
- Idempotent booking creation keyed by Stripe PaymentIntent ID to prevent duplicate bookings.
- Email and Telegram notifications are best-effort side effects after booking creation.
- Core operational entities use status or active flags where applicable instead of hard deletion.

### Admin Panel

- Protected admin login.
- Services management.
- Masters management.
- Schedule management.
- Bookings management.
- Reports.
- Telegram account management.
- Booking status workflows such as cancel, refund, complete, and no-show where supported by the admin views.

### Telegram Bot

- aiogram 3 bot located in `backend/telegram_bot`.
- Manager and barber role-based access.
- `TelegramAccount` records in the database are the source of truth for access and routing.
- The bot calls the FastAPI backend and does not access the database directly.
- Commands such as `/today`, `/tomorrow`, and `/now`.
- Manager summaries.
- Same-day booking notifications.
- Barber appointment reminders.
- Unknown or inactive Telegram users are denied access.

### Deployment

- Docker support for frontend and backend.
- Railway-ready service layout.
- Separate deployable services for frontend, backend API, and Telegram bot.
- SQLite volume support for demo deployments.
- Stripe test mode support.

## Tech Stack

### Frontend

- React
- Vite
- TypeScript
- React Router
- Stripe.js and Stripe PaymentElement

### Backend

- FastAPI
- SQLAlchemy
- SQLite
- PyJWT admin sessions
- Stripe Python SDK
- Resend transactional email API

### Bot

- aiogram 3
- httpx

### Deployment

- Docker
- Railway

## Architecture

The frontend is a client application. It does not own booking, payment, schedule, or availability rules. The Telegram bot is also a client/worker and communicates through backend APIs. The FastAPI backend is the source of truth.

Stripe webhook handling is implemented as a backend route, not as a separate service. Email and Telegram notifications happen after booking creation and are treated as side effects so notification failures do not break the booking flow.

Admin APIs are protected by admin authentication. Public booking and manage-token endpoints remain separate from admin APIs. Bot endpoints are separate and validate bot access using the bot token and `TelegramAccount` authorization rules.

```text
Customer Browser
  -> Frontend
  -> FastAPI Backend
  -> SQLite
  -> Stripe API
  -> Resend Email API
  -> Telegram Bot API

Stripe
  -> /api/stripe/webhook

Telegram Bot Service
  -> FastAPI Backend
```

## Repository Structure

The frontend is located at the repository root. The backend and Telegram bot are located under `backend/`.

```text
.
├── Dockerfile
├── package.json
├── src/
├── public/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   └── modules/
│   └── telegram_bot/
└── README.md
```

## Environment Variables

Do not commit `.env` files. Use placeholders in examples and configure real values in local `.env` files or Railway service variables.

Vite environment variables are build-time variables. Backend and bot variables are runtime variables.

### Frontend

```env
VITE_API_BASE_URL=https://backend-url
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Backend

```env
APP_ENV=development
DATABASE_URL=sqlite:///./saloon.db
PUBLIC_FRONTEND_URL=http://localhost:5173
BACKEND_API_URL=http://127.0.0.1:8000

STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

RESEND_API_KEY=your_resend_api_key
EMAIL_FROM=onboarding@resend.dev
EMAIL_FROM_NAME=Saloon Booking

ADMIN_USERNAME=
ADMIN_PASSWORD=
ADMIN_PASSWORD_HASH=
ADMIN_SESSION_SECRET=
ADMIN_SESSION_EXPIRE_MINUTES=1440

CLIENT_MANAGE_CUTOFF_HOURS=

TELEGRAM_BOT_TOKEN=
TELEGRAM_AUTH_SOURCE=db
BOT_TIMEZONE=Europe/Vilnius
BARBER_REMINDER_MINUTES=15
BARBER_REMINDER_CHECK_INTERVAL_SECONDS=60
```

### Telegram Bot Service

```env
TELEGRAM_BOT_TOKEN=
BACKEND_API_URL=https://backend-url
TELEGRAM_AUTH_SOURCE=db
BOT_TIMEZONE=Europe/Vilnius
BARBER_REMINDER_MINUTES=15
BARBER_REMINDER_CHECK_INTERVAL_SECONDS=60
```

The Stripe webhook secret for a deployed Railway backend is different from the local Stripe CLI webhook secret. Configure each environment with the correct `STRIPE_WEBHOOK_SECRET`.

## Local Development Setup

### Frontend

```bash
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Telegram Bot

```bash
cd backend
source .venv/bin/activate
python -m telegram_bot.main
```

### Stripe Local Webhook

```bash
stripe listen --forward-to localhost:8000/api/stripe/webhook
```

For local testing, configure `backend/.env` with test keys and local URLs. Stripe test mode is expected.

If the local webhook is not running, the payment-result fallback can still confirm payment after the customer returns to the success page. The webhook is still important because a customer may close the browser before the success page loads.

### Demo Schedule Seed

To fill demo schedules for masters 1-3 through `2028-12-31`:

```bash
cd backend
source .venv/bin/activate
python scripts/seed_demo_schedule.py
```

The command creates working schedules for the demo masters: master 1 works every day except Sunday from `15:00` to `20:00`, master 2 works every second day except Sunday from `10:00` to `18:00`, and master 3 works every day except Sunday from `09:00` to `20:00`.

The script is idempotent and safe to rerun. If a shift already exists for the same master and date, it updates that row to the demo values or skips it when unchanged. It does not delete schedules, bookings, services, or masters.

## Docker

Dockerfiles are provided for deployment.

### Frontend

```bash
docker build -t saloon-frontend .
docker run --rm -p 3000:3000 -e PORT=3000 saloon-frontend
```

The frontend Docker image builds the Vite app and serves the generated `dist` folder with SPA fallback support, so browser refreshes on routes such as `/admin/login` or booking manage pages still load `index.html`.

### Backend

```bash
docker build -t saloon-backend ./backend
docker run --rm -p 8000:8000 \
  -e PORT=8000 \
  -e DATABASE_URL=sqlite:///./saloon.db \
  saloon-backend
```

The default backend command is:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

The Telegram bot can reuse the backend image with a command override:

```bash
python -m telegram_bot.main
```

## Railway Deployment

The intended Railway setup uses separate services for the frontend, backend API, and Telegram bot.

### Service 1: Frontend

- Root directory: `/` or repository root.
- Dockerfile: `Dockerfile`.
- Public domain enabled.
- Environment variables:

```env
VITE_API_BASE_URL=https://backend-url
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Service 2: Backend

- Root directory: `/backend`.
- Dockerfile: `Dockerfile`.
- Public domain enabled.
- Persistent volume mounted at `/data`.
- SQLite demo database:

```env
DATABASE_URL=sqlite:////data/saloon.db
PUBLIC_FRONTEND_URL=https://frontend-url
BACKEND_API_URL=https://backend-url
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
ADMIN_USERNAME=
ADMIN_PASSWORD_HASH=
ADMIN_SESSION_SECRET=
RESEND_API_KEY=your_resend_api_key
EMAIL_FROM=onboarding@resend.dev
EMAIL_FROM_NAME=Saloon Booking
TELEGRAM_BOT_TOKEN=
TELEGRAM_AUTH_SOURCE=db
BOT_TIMEZONE=Europe/Vilnius
BARBER_REMINDER_MINUTES=15
BARBER_REMINDER_CHECK_INTERVAL_SECONDS=60
```

### Service 3: Telegram Bot

- Root directory: `/backend`.
- Dockerfile: `Dockerfile`.
- Public domain not required.
- Start command:

```bash
python -m telegram_bot.main
```

- Environment variables:

```env
TELEGRAM_BOT_TOKEN=
BACKEND_API_URL=https://backend-url
TELEGRAM_AUTH_SOURCE=db
BOT_TIMEZONE=Europe/Vilnius
BARBER_REMINDER_MINUTES=15
BARBER_REMINDER_CHECK_INTERVAL_SECONDS=60
```

### Stripe Webhook

Configure the Stripe webhook endpoint to:

```text
https://backend-url/api/stripe/webhook
```

### Suggested Deployment Order

1. Deploy the backend service.
2. Add the backend public domain.
3. Deploy the frontend service with `VITE_API_BASE_URL` pointing to the backend.
4. Update backend `PUBLIC_FRONTEND_URL` with the frontend URL.
5. Deploy the Telegram bot service with `BACKEND_API_URL` pointing to the backend.
6. Configure the Stripe webhook endpoint.
7. Update `STRIPE_WEBHOOK_SECRET` in Railway.
8. Run a full smoke test.

## Demo Notes

The public demo focuses on the customer booking flow and Stripe test payment. The admin panel is protected and is not intended to be publicly shared. The Telegram bot is protected by Telegram ID and role-based account records. Admin and bot workflows can be demonstrated by video or screen share.

### Demo Payment / Stripe Test Card

The deployed demo uses Stripe test mode for portfolio/demo payments. Use the following Stripe test payment details; no real money is charged.

```text
Card number: 4242 4242 4242 4242
Expiry date: any future date, for example 12/34
CVC: any 3 digits, for example 123
ZIP/postal code: any valid value, for example 12345
Payment mode: Stripe test mode / demo only
```

Emails are sent through the configured Resend transactional email API over HTTPS. Configure real Resend values in Railway service variables; no email provider secrets are committed. Email delivery is treated as a notification side effect, so a provider failure is logged but does not block booking creation or payment confirmation. SQLite is used for demo simplicity; PostgreSQL with backups is recommended for real production deployments.

## Smoke Test Checklist

- Frontend opens.
- Services and masters load.
- Slots load from backend availability.
- PaymentIntent is created with backend-calculated amount.
- Stripe test payment succeeds.
- Booking is created.
- Confirmation email is sent.
- Manage link works.
- Admin panel shows the booking.
- Telegram notification is sent to the appropriate operational account.
- Replaying the webhook does not duplicate the booking.
- Running fallback confirmation after webhook does not duplicate the booking.
- Running fallback confirmation without webhook creates the booking.
- Manage cancel and reschedule respect backend cutoff rules.

## Security / Production Notes

- Do not commit `.env` files.
- Do not commit `saloon.db` or other local database files.
- Rotate any token or key that was ever exposed.
- Use Stripe live keys only for a real production deployment.
- Use a verified sending domain with the transactional email provider for a real client.
- Use PostgreSQL and backups for production data.
- Use a persistent volume if running the SQLite demo on Railway.
- Admin sessions use an HTTP-only cookie.
- Bot endpoints are protected by bot token checks and `TelegramAccount` authorization.
- Manage tokens should be treated as private links and should not be publicly exposed.

## Known Demo Limitations

- SQLite is used for demo deployment.
- Admin and bot tools are protected operational surfaces, not public demo pages.
- SMS notifications are not included.
- Notifications are not backed by a dedicated queue such as Celery.
- Reminder duplicate protection is MVP-level.
- The project can be extended for production with PostgreSQL, Alembic migrations, queued notifications, monitoring, log masking, and provider-grade email delivery.

## Future Improvements

- PostgreSQL.
- Alembic migrations.
- Automated tests.
- Persistent notification logs.
- Production transactional email provider.
- Custom domain.
- Monitoring and log masking.
- CI/CD.
- Role-based admin users.
- Mobile app client.

## License / Portfolio Note

This project is intended as a portfolio/demo project.
