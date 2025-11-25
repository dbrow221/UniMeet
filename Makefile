# ================================
# UniMeet Automation Makefile
# -------see note below-------
# ================================

SHELL := cmd.exe

# Directories
FRONTEND_DIR = frontend
BACKEND_DIR = backend
VENV_DIR = env

# --------------------------------
# Create & Activate Environment
# --------------------------------
env:
	python -m venv $(VENV_DIR)

install-backend:
	$(VENV_DIR)\Scripts\pip install -r requirements.txt

run-backend:
	$(VENV_DIR)\Scripts\activate && cd $(BACKEND_DIR) && python manage.py runserver

# --------------------------------
# Frontend
# --------------------------------
install-frontend:
	cd $(FRONTEND_DIR) && npm install

run-frontend:
	cd $(FRONTEND_DIR) && npm run dev

# --------------------------------
# RUN BOTH (Backend + Frontend)
# --------------------------------
start: run-backend

start-both:
	start /B make run-backend
	start /B make run-frontend

# --------------------------------
# CLEAN (remove venv)
# --------------------------------
clean:
	rmdir /S /Q $(VENV_DIR)

# -----------------------------------------------------------
# 💻 How to Run the Project After Adding the Makefile
# Once the Makefile is placed at the root of the project (UniMeet-main), follow the steps below.

# 🧱 First-Time Setup (Run Only Once)
# 1️⃣ Create Python virtual environment
# make env

# 2️⃣ Install backend dependencies (Django, JWT, etc.)
# make install-backend

# 3️⃣ Install frontend dependencies (React/Vite)
# make install-frontend

# 🚀 Run the Project (Backend + Frontend)
# To start both servers automatically:
# make start-both

# 💡 This launches Django and React/Vite at the same time.

# 🔁 Future Runs (Daily Use)
# You do NOT need to reinstall anything again.
# Simply run:
# make start-both

# ✔️ That’s it — the full system boots up.
# -----------------------------------------------------------