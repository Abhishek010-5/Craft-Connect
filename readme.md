# Craft-Connect API

**Craft-Connect API** powers a web application for workers (e.g., painters, carpenters, plumbers, electricians) to scan coupon codes, redeem schemes, and manage points-based rewards. Built with **Flask** and **PostgreSQL**, it includes admin functionalities for user verification, scheme management, and account deletion for abnormal activity. Authentication uses **JWT tokens**, with a `TTLCache` for temporary data storage (e.g., OTPs during password resets).

## Database Schema
- **users**: Stores user data (`id`, `name`, `email` (unique), `password`, `create_on`). Linked to `user_points` and `schemes_redemption`.
- **user_points**: Tracks user points (`id`, `email` (FK to `users.email`), `points`).
- **otp_verification**: Manages OTPs for email verification (`id`, `email`, `otp`, `created`, `valid_till`).
- **pending_signups**: Holds signup requests for admin review (`id`, `name`, `email` (unique), `password`, `created`, `status` (pending/approved/rejected), `email_status` (verified/unverified)).
- **points**: Stores point codes (`points_code` (PK), `status` (scanned/not_scanned), `points_value`, `expiry_date`).
- **scheme**: Defines schemes (`scheme_id`, `scheme_title`, `scheme_valid_from`, `scheme_valid_to`, `scheme_perks`, `points`).
- **schemes_redemption**: Tracks redemptions (`id`, `name`, `email` (unique), `scheme_status` (pending/approved/rejected), `scheme_id` (FK to `scheme.scheme_id`)).
- **admin**: Stores admin credentials (`email` (PK), `password`).

## API Routes

### User Routes (`/user`)
- **`GET/POST /get_user_profile`**: Retrieves user details from `users` by `email`. Returns `name`, `email`, etc. (200) or errors (400: invalid JSON/email, 404: user not found, 500: database error).
- **`POST /redeem_scheme`**: Redeems a scheme by `email` and `scheme_id`. Checks `schemes_redemption` for prior applications and compares `user_points.points` with `scheme.points`. Inserts into `schemes_redemption` with `pending` status. Returns success (200) or errors (400: insufficient points/already applied, 500: database error).
- **`GET /top_users`**: Fetches top users from `user_points` ordered by `points`, limited by `limit`. Returns user list (200) or errors (400: invalid limit, 500: database error).
- **`GET /get_users`**: Lists users from `users`, with optional `limit` (default 10). Returns user list (200) or errors (400: invalid limit, 500: database error).
- **`POST /scheme_status`**: Retrieves `scheme_status` from `schemes_redemption` by `email`. Returns status (200) or errors (400: invalid JSON, 404: no schemes, 500: database error).
- **`GET /get_schemes_for_user`** (token-required): Lists schemes from `scheme` available for users. Returns schemes (200) or errors (404: no schemes, 500: database error).

### Points Routes (`/points`)
- **`PUT /redeem_points`**: Deducts `points` from `user_points` by `email`. Validates sufficient points. Returns remaining points (200) or errors (400: invalid points/email, 500: database error).
- **`GET/POST /get_points`**: Retrieves `points` from `user_points` by `email`. Returns points (200) or errors (400: invalid email, 500: database error).
- **`PUT /validate_points`**: Validates `points_code` in `points`, updates `status` to `scanned`, and adds `points_value` to `user_points.points`. Returns updated points (200) or errors (400: invalid code, 500: database error).

### Authentication Routes (`/auth`)
- **`GET/POST /login`**: Authenticates users with `email` and `password` from `users`. Returns **JWT token** (200) or errors (400: invalid credentials, 500: server error).
- **`GET/POST /signup`**: Inserts signup requests into `pending_signups` with `name`, `email`, `password`, and `status=pending`. Sends OTP to `otp_verification`. Returns signup status (201) or errors (400: invalid input/existing user, 500: database error).
- **`GET/PUT /forgot_password`**: Stores `email` and `password` in `TTLCache` and sends OTP to `otp_verification`. Returns status (200) or errors (400: invalid email, 500: server error).
- **`POST /logout`** (token-required): Invalidates session. Returns success (200) or error (500).
- **`POST /refresh`** (token-required): Refreshes **JWT token** for the user. Returns new token (200).
- **`POST /verify_email/<email>/<field>`**: Verifies OTP in `otp_verification`. For `signup`, updates `pending_signups.email_status` to `verified`. For `forgot`, resets `users.password`. Deletes OTP after verification. Returns success (200) or errors (400: invalid OTP/timeout, 500: database error).

### Admin Routes (`/admin`)
- **`GET /pending_signups`**: Lists records from `pending_signups` with `status=pending`. Returns pending users (200) or error (404: none found, 500: database error).
- **`POST /approve_or_reject_pending_signups`**: Updates `pending_signups.status` by `email`. If `approved`, inserts into `users` and `user_points`. Returns success (200) or errors (400: invalid input, 500: database error).
- **`DELETE /delete_scheme`**: Deletes a scheme from `scheme` by `id`. Returns success (200) or errors (400: invalid ID, 500: database error).
- **`POST /add_scheme`**: Inserts into `scheme` with `scheme_title`, `scheme_valid_from`, `scheme_valid_to`, `scheme_perks`, and `points`. Returns success (200) or errors (400: invalid input, 500: database error).
- **`PUT /update_scheme`**: Updates `scheme` fields by `scheme_title`. Returns success (200) or errors (400: invalid input, 500: database error).
- **`GET /get_schemes`**: Lists all schemes from `scheme`. Returns schemes (200) or error (400: none found, 500: database error).
- **`GET /get_scheme_to_approve`**: Lists `schemes_redemption` records with `scheme_status=pending`. Returns schemes (200) or errors (404: none found, 500: database error).
- **`POST /reject_scheme`**: Updates `schemes_redemption.scheme_status` to `rejected` by `id`. Returns success (200) or errors (400: invalid ID, 500: database error).
- **`PUT /update_user_details`**: Updates `users.name` and `user_points.points` by `email`. Returns success (200) or errors (400: invalid input, 500: database error).
- **`DELETE /delete_user`**: Deletes user from `users`, `user_points`, and `schemes_redemption` by `email` for abnormal activity (e.g., fraudulent redemptions). Returns success (200) or errors (400: invalid email, 500: database error).
- **`POST /send_otp`**: Sends OTP to `otp_verification` for admin `email` (verified in `admin`). Returns success (200) or errors (400: invalid email, 500: server error).
- **`POST /verify_otp`**: Verifies OTP in `otp_verification` for admin `email`. Returns success (200) or errors (400: invalid OTP/timeout, 500: database error).
- **`POST /admin_login`**: Authenticates admins with `email` and `password` from `admin`. Returns **JWT token** (200) or errors (400: invalid credentials, 500: database error).

## Admin Features
- **User Verification**: Admins review `pending_signups` via `/pending_signups` and approve/reject via `/approve_or_reject_pending_signups`. Approved users are moved to `users` and `user_points`.
- **Scheme Management**: Admins add (`/add_scheme`), update (`/update_scheme`), or delete (`/delete_scheme`) schemes in `scheme`. They approve/reject redemptions in `schemes_redemption` via `/get_scheme_to_approve` and `/reject_scheme`.
- **User Account Deletion**: Admins delete users from `users`, `user_points`, and `schemes_redemption` via `/delete_user` for abnormal activity, ensuring system integrity.
- **Admin Authentication**: Admins log in via `/admin_login` and use OTP verification (`/send_otp`, `/verify_otp`) for secure actions.

## Security
- **JWT Authentication**: Uses **JWT tokens** (configured with `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRY_MINUTES`) for user and admin access. Token-required routes enforce authorization.
- **Input Validation**: Ensures JSON payloads, valid email formats, and safe characters to prevent injection. Validates data types (e.g., `int` for `points`, `scheme_id`).
- **Database Safety**: Catches `DatabaseError` for **PostgreSQL** issues, ensuring robust error handling.
- **Caching**: Uses `TTLCache` (maxsize 100, 300s TTL) for temporary storage during password resets.

## Technologies
- **Backend**: **Flask** (Python) for API logic.
- **Database**: **PostgreSQL** for storing user, point, scheme, and admin data.
- **Authentication**: **JWT** for secure access; `TTLCache` for temporary data.


## File Structure
- `.env`: Environment variables for configuration (e.g., `JWT_SECRET_KEY`).
- `.gitignore`: Specifies files/folders to exclude from Git.
- `app_errors.log`: Logs application errors.
- `ERD.txt`: Entity-Relationship Diagram for the database.
- `readme.md`: Project documentation.
- `requirements.txt`: Python dependencies for the project.
- `tables.sql`: SQL scripts for creating database tables.
- `vercel.json`: Configuration for Vercel deployment.
- `__init__.py`: Initializes the Python package.
- **api/**:
  - `app.py`: Main Flask application entry point.
  - `blueprints.py`: Defines Flask blueprints for routing.
  - `config.py`: Configuration settings (e.g., database, JWT).
  - `database.py`: Database connection and setup.
  - `decoraters.py`: Custom decorators (e.g., `token_required`).
  - `test.py`: Unit tests for the API.
  - `__init__.py`: Initializes the API module.
  - **admin_api/**:
    - `queries.py`: SQL queries for admin operations.
    - `routes.py`: Admin API routes (e.g., `/admin_login`, `/add_scheme`).
    - `test.py`: Tests for admin API.
    - **utils/**:
      - `admin_utils.py`: Admin-related utility functions.
      - `scheme_utils.py`: Scheme management utilities.
      - `user_utils.py`: User management utilities.
  - **login_api/**:
    - `queries.py`: SQL queries for authentication.
    - `routes.py`: Authentication routes (e.g., `/login`, `/signup`).
    - `test.py`: Tests for authentication API.
    - `__init__.py`: Initializes the login module.
    - **utils/**:
      - `otp_utlis.py`: OTP generation and sending utilities.
      - `user_utils.py`: User authentication utilities.
      - `validate_utils.py`: Input validation utilities.
  - **points_api/**:
    - `queris.py`: SQL queries for points management.
    - `routes.py`: Points routes (e.g., `/redeem_points`).
    - `test.py`: Tests for points API.
    - `__init__.py`: Initializes the points module.
    - **utils/**:
      - `points_util.py`: Points-related utilities.
  - **user_api/**:
    - `queries.py`: SQL queries for user operations.
    - `routes.py`: User routes (e.g., `/get_user_profile`).
    - `test.py`: Tests for user API.
    - `__init__.py`: Initializes the user module.
    - **utils/**:
      - `users_util.py`: User-related utilities.

> **Note**: Ensure dependencies in `requirements.txt` are installed and the database is set up using `tables.sql` before running the application.

For detailed documentation, request/response formats, or code, refer to the [GitHub repository](https://github.com/Abhishek010-5/Craft-Connect) or contact `abhishekkrana404@gmail.com`.