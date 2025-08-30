# DJO Corvee
Repository for the DJO Corvee.

### How to test on a local machine
1. Clone the repository.
2. Create a venv:
    ```bash
    python3 -m venv venv
    ```
3. Activate the venv:
    ```bash
    source venv/bin/activate
    ```
    (This is a Linux command, the command may differ on other operating systems.)
4. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Build/update the database:
    ```bash
    python3 manage.py migrate
    ```
6. Create a superuser:
    ```bash
    python3 manage.py createsuperuser
    ```
7. Run the server:
    ```bash
    python3 manage.py runserver
    ```
8. Navigate to `http://localhost:8000/admin` and log in with the superuser you created.
9. Go to the `Personen` table and add some people.
10. Navigate to `http://localhost:8000/main` to get your very own corvee dashboard!
