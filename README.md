# IT Helpdesk Ticket Management System
Flask + MySQL app to create, track, search and update IT support tickets.

## Run (Windows)
1. `mysql -u root -p < database.sql`
2. `python -m venv venv` then `venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and put your MySQL password in it.
5. `python app.py` and open http://127.0.0.1:5000
