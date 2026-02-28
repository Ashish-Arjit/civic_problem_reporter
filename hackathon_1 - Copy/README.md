# CivicFix | Community Accountability Dashboard

Complete full-stack system for civic complaint management with 48-hour social media escalation.

## Overview
CivicFix is a platform designed to empower citizens by providing a transparent way to report and track local issues. If a reported complaint remains "Pending" for more than 48 hours, the system automatically simulates a social media escalation (Twitter, Facebook, or Instagram) to ensure accountability.

## Tech Stack
- **Frontend**: HTML5, Vanilla CSS, JavaScript (Leaflet.js for maps)
- **Backend**: Python (Flask)
- **Database**: MySQL

## Setup Instructions

### 1. Database Setup
- Ensure MySQL is installed and running on your system.
- Log in to your MySQL terminal and run the contents of `init.sql`:
  ```bash
  mysql -u root -p < init.sql
  ```
  *(This will create the `hackathon_db` and the necessary `complaints` table)*

### 2. Backend Setup
- Clone the repository.
- Create a virtual environment:
  ```bash
  python -m venv venv
  ```
- Activate the virtual environment:
  - Windows: `venv\Scripts\activate`
  - Linux/Mac: `source venv/bin/activate`
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Configure environment variables:
  - Copy `.env.example` to `.env`.
  - Update the `.env` file with your MySQL credentials (host, user, password, database).

### 3. Run the Application
- Start the Flask server:
  ```bash
  python app.py
  ```
- The backend will run on `http://localhost:5050`.
- Open `index.html` in your web browser to use the dashboard.

## API Endpoints

### `POST /submit`
Submit a new complaint using multipart/form-data.
- **Fields**: `username`, `phone`, `latitude`, `longitude`, `priority`, `preferred_platform`, `image` (optional file).

### `GET /get_all_complaints`
Returns a list of all complaints in descending order of creation.

### `GET /check_pending`
Triggers the automated escalation check for complaints older than 48 hours.

### `POST /force_escalation`
Demo Utility: Backdates all "Pending" complaints by 50 hours for immediate escalation testing.

### `POST /mark_resolved/<id>`
Marks a specific complaint as "Resolved".

## License
MIT License. Feel free to use and improve!
