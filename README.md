# Credit Approval System - Backend

This project is a backend credit approval system developed as part of the Alemeno Backend Internship assignment. It is built using the Python/Django stack and is fully containerized with Docker. The system determines loan eligibility based on historical data, customer information, and a defined credit scoring model.

## Features

-   **RESTful API:** Exposes endpoints for customer registration, loan eligibility checks, loan creation, and viewing loan/customer data.
-   **Data Ingestion:** Populates the initial database from provided `.xlsx` files (`customer_data.xlsx`, `loan_data.xlsx`) using asynchronous background workers.
-   **Credit Scoring Logic:** Implements a custom credit scoring algorithm to determine loan approval and interest rates.
-   **Dockerized Environment:** The entire application and its dependencies (PostgreSQL, Redis, Celery) are containerized, ensuring a consistent and reproducible setup.
-   **Asynchronous Task Processing:** Utilizes Celery and Redis to handle data ingestion in the background without blocking the main application.

## Tech Stack

-   **Backend:** Python, Django, Django REST Framework
-   **Database:** PostgreSQL
-   **Asynchronous Tasks:** Celery
-   **Message Broker / Cache:** Redis
-   **Containerization:** Docker, Docker Compose
-   **Data Handling:** Pandas

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:
-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

---

## Setup and Installation

Follow these steps to get the project up and running locally.

### 1. Clone the Repository

```bash
git clone https://github.com/ChetanVarunKanipakam/credit_approval_backend.git
cd alimeno-assignment
```
### 2. Prepare Data Files

Place the provided `customer_data.xlsx` and `loan_data.xlsx` files inside the `data/` directory in the project root.

### 3. Build and Run the Docker Containers

This command will build the Docker images for the Django application and start all the services (web, celery, db, redis) in detached mode.

```bash
docker-compose up --build -d
```

docker-compose exec web python manage.py sqlsequencereset customers loans | docker-compose exec -T db psql -U alemeno_user -d alemeno_db```

The application is now running and ready to accept API requests at `http://localhost:8000`.

---
### 4. Apply Database Migrations

First, create the migration files for our custom `customers` and `loans` apps.

```bash
docker-compose exec web python manage.py makemigrations customers loans
docker-compose exec web python manage.py migrate
```

### 5. Ingest Initial Data

Run the custom management command to queue the data ingestion tasks. Celery will pick them up and populate the database.

```bash
docker-compose exec web python manage.py ingest_data
```
### 6. Reset Database Sequences

After ingesting data with manually specified primary keys, the database's auto-incrementing sequence counter is out of sync. This command fixes it.

```bash
docker-compose exec web python manage.py sqlsequencereset customers loans | docker-compose exec -T db psql -U alemeno_user -d alemeno_db
```

## API Endpoints

Here are the available API endpoints.

### 1. Register a New Customer

-   **Endpoint:** `/api/register/`
-   **Method:** `POST`
-   **Description:** Adds a new customer to the system and calculates their `approved_limit` based on their monthly salary.
-   **Request Body:**
    ```json
    {
        "first_name": "Jane",
        "last_name": "Smith",
        "age": 28,
        "monthly_income": 75000,
        "phone_number": "9876543210"
    }
    ```
-   **Success Response (201 Created):**
    ```json
    {
        "customer_id": 13,
        "name": "Jane Smith",
        "age": 28,
        "monthly_income": 75000,
        "approved_limit": 2700000,
        "phone_number": "9876543210"
    }
    ```
-   **cURL Example:**
    ```bash
    curl -X POST http://localhost:8000/api/register/ -H "Content-Type: application/json" -d '{"first_name": "Jane", "last_name": "Smith", "age": 28, "monthly_income": 75000, "phone_number": "9876543210"}'
    ```

### 2. Check Loan Eligibility

-   **Endpoint:** `/api/check-eligibility/`
-   **Method:** `POST`
-   **Description:** Checks if a customer is eligible for a loan based on their credit score and other factors. It returns whether the loan can be approved and if the interest rate needs correction.
-   **Request Body:**
    ```json
    {
        "customer_id": 1,
        "loan_amount": 50000,
        "interest_rate": 10.5,
        "tenure": 12
    }
    ```
-   **Success Response (200 OK):**
    ```json
    {
        "customer_id": 1,
        "approval": true,
        "interest_rate": "10.50",
        "corrected_interest_rate": "12.00",
        "tenure": 12,
        "monthly_installment": "4442.44",
        "message": "Loan approved."
    }
    ```
-   **cURL Example:**
    ```bash
    curl -X POST http://localhost:8000/api/check-eligibility/ -H "Content-Type: application/json" -d '{"customer_id": 1, "loan_amount": 50000, "interest_rate": 10.5, "tenure": 12}'
    ```

### 3. Create a New Loan

-   **Endpoint:** `/api/create-loan/`
-   **Method:** `POST`
-   **Description:** Creates a new loan record if the customer is eligible. If not approved, it returns a message explaining why.
-   **Request Body:**
    ```json
    {
        "customer_id": 1,
        "loan_amount": 30000,
        "interest_rate": 13.0,
        "tenure": 6
    }
    ```
-   **Success Response (201 Created):**
    ```json
    {
        "loan_id": 101,
        "customer_id": 1,
        "loan_approved": true,
        "message": "Loan approved and created successfully.",
        "monthly_installment": "5215.15"
    }
    ```
-   **cURL Example:**
    ```bash
    curl -X POST http://localhost:8000/api/create-loan/ -H "Content-Type: application/json" -d '{"customer_id": 1, "loan_amount": 30000, "interest_rate": 13.0, "tenure": 6}'
    ```

### 4. View a Specific Loan

-   **Endpoint:** `/api/view-loan/<loan_id>/`
-   **Method:** `GET`
-   **Description:** Retrieves detailed information about a single loan, including nested customer details.
-   **cURL Example:**
    ```bash
    curl http://localhost:8000/api/view-loan/1/
    ```

### 5. View All Loans for a Customer

-   **Endpoint:** `/api/view-loans/<customer_id>/`
-   **Method:** `GET`
-   **Description:** Retrieves a list of all loans associated with a specific customer.
-   **cURL Example:**
    ```bash
    curl http://localhost:8000/api/view-loans/1/
    ```

---

## Project Structure

The project follows a standard Django structure with a focus on modularity:

-   `alemethod/`: Contains the main project configuration (`settings.py`, `urls.py`, `celery.py`).
-   `apps/`: A directory containing the individual Django apps.
    -   `apps/customers/`: Handles all customer-related models, views, and logic.
    -   `apps/loans/`: Handles all loan-related models, views, serializers, and business logic.
-   `data/`: Directory for storing the initial data `.xlsx` files.