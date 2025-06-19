# SECURA Registration App

This is a Streamlit-based registration and login app for SECURA, connected to a MySQL database.

## Features
- User registration with hashed passwords
- Login system
- Emergency contacts (multiple)
- MySQL backend

## Setup
1. Install dependencies:
```
pip install -r requirements.txt
```

2. Configure MySQL and create a database called `secura_db`

3. Store secrets in Streamlit Cloud → Settings → Secrets:

```toml
db_host = "your-host"
db_user = "your-user"
db_password = "your-password"
db_name = "secura_db"
```

4. Deploy on Streamlit Cloud: https://streamlit.io/cloud
