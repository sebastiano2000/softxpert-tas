# Support Ticket Assignment System

This project implements a Django-based API for a customer support platform where thousands of agents handle support tickets. The system ensures that each agent receives a unique batch of unassigned tickets, preventing duplication and ensuring efficient concurrency handling.

## Table of Contents
- [Background](#background)
- [Features](#features)
- [Technical Considerations](#technical-considerations)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)
- [Containerization](#containerization)
- [Production Considerations](#production-considerations)
- [License](#license)

## Background

The goal of this project is to create an efficient support ticket assignment system with the following requirements:

- **Actors:**  
  - **Admin:** Can create, update, and delete tickets.
  - **Agent:** Can fetch a batch (15 max) of unassigned tickets and sell tickets that are assigned to them.
- **Ticket Assignment Logic:**  
  - When an agent requests tickets, if they have fewer than 15 unsold tickets assigned:
    - Assign enough unassigned tickets (in creation order) to reach a total of 15.
  - If the agent already has 15 assigned tickets, simply return those.
  - If no unassigned tickets are available, return the current assignment (or an empty list).
- **Concurrency & Scalability:**  
  - The system uses database transactions and `select_for_update(skip_locked=True)` to prevent race conditions.
  - Optimized queries ensure performance under high concurrency.
- **Security:**  
  - Agents can only fetch and sell tickets assigned to them.
  - Admin endpoints are restricted to admin users.

## Features

- **Admin API Endpoints:**
  - Create, update, and delete tickets.
- **Agent API Endpoints:**
  - Fetch (assign) a batch of up to 15 tickets.
  - Sell a ticket (mark as sold) that is assigned to the agent.
- **Concurrency Handling:**
  - Uses database-level locking to prevent race conditions.
- **Containerization:**
  - Docker and Docker Compose configurations provided.
- **API Tests:**
  - Comprehensive tests verifying endpoint correctness and concurrent ticket assignment.

## Technical Considerations

- **Concurrency:**  
  Prevents race conditions by using `transaction.atomic()` and `select_for_update(skip_locked=True)`.
- **Scalability:**  
  Efficient database queries and batching ensure smooth operation for thousands of concurrent agents.
- **Security:**  
  Custom permission classes ensure that agents can only operate on their own tickets, while admins have full control.

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd support_system
   ```
2. **Create a virtual environment and activate it:**
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

## Environment Variables

Create a `.env` file in the root directory with the following content:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings (for PostgreSQL)
POSTGRES_DB=support_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=support_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

## API Endpoints

### Admin Endpoints
- **Create Ticket:** `POST /api/admin/tickets/`
- **Update Ticket:** `PUT /api/admin/tickets/<ticket_id>/`
- **Delete Ticket:** `DELETE /api/admin/tickets/<ticket_id>/`
- **List Tickets:** `GET /api/admin/tickets/`

### Agent Endpoints
- **Assign/Fetch Tickets:** `GET /api/agent/tickets/assign/`  
  - Returns a batch of up to 15 tickets (assigning new tickets if necessary).
- **Sell Ticket:** `POST /api/agent/tickets/sell/<ticket_id>/`  
  - Marks the specified ticket (assigned to the agent) as sold.

## Running Tests

To run tests, execute:
```bash
python manage.py test
```

## Containerization

### Using Docker
1. **Build the Docker image:**
   ```bash
   docker build -t support_system .
   ```
2. **Run the container:**
   ```bash
   docker run -p 8000:8000 support_system
   ```

### Using Docker Compose
1. **Start services:**
   ```bash
   docker-compose up --build
   ```
2. **Access the app:**
   Open `http://localhost:8000` in your browser.

## Production Considerations

- **WSGI Server:** Use Gunicorn for production.
- **Static Files:** Use WhiteNoise or serve via a dedicated server.
- **Logging & Monitoring:** Configure structured logging and monitoring tools.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.