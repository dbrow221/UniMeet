# ================================
# UniMeet Automation Makefile (Windows)
# -------- see note below --------
# =====================================

SHELL := cmd.exe

# Directories
FRONTEND_DIR = frontend
BACKEND_DIR = backend
VENV_DIR = env

PYTHON = $(VENV_DIR)\Scripts\python
PIP = $(VENV_DIR)\Scripts\pip

# --------------------------------------------------
# 🧱 1) CREATE PYTHON ENVIRONMENT
# --------------------------------------------------
env:
	python -m venv $(VENV_DIR)
	@echo Virtual environment created.

# --------------------------------------------------
# 📌 2) BACKEND REQUIREMENTS + INSTALLATION
#     (Auto-creates requirements.txt if missing)
# --------------------------------------------------
install-backend: requirements
	$(PIP) install -r requirements.txt
	@echo Backend dependencies installed!

requirements:
	@if not exist requirements.txt ( \
		echo Creating requirements.txt ... & \
		$(PIP) install django djangorestframework djangorestframework-simplejwt django-cors-headers python-dotenv psycopg2-binary & \
		$(PIP) freeze > requirements.txt & \
		echo requirements.txt created successfully! \
	) else ( \
		echo requirements.txt found. Skipping creation. \
	)

# --------------------------------------------------
# 🌐 3) FRONTEND INSTALLATION & RUN
# --------------------------------------------------
install-frontend:
	cd $(FRONTEND_DIR) && npm install

run-frontend:
	cd $(FRONTEND_DIR) && npm run dev

# --------------------------------------------------
# 🚀 4) BACKEND SERVER
# --------------------------------------------------
run-backend:
	$(VENV_DIR)\Scripts\activate && cd $(BACKEND_DIR) && $(PYTHON) manage.py runserver

# --------------------------------------------------
# 🚀 5) RUN BOTH SERVERS TOGETHER
# --------------------------------------------------
start-both:
	cmd /c "start /B make run-backend"
	cmd /c "start /B make run-frontend"
	@echo UniMeet is running! 🎉

# --------------------------------------------------
# 🧹 6) CLEAN ENVIRONMENT
# --------------------------------------------------
clean:
	rmdir /S /Q $(VENV_DIR)
	@echo Virtual environment deleted!

# -----------------------------------------------------------
# How to Run the Project After Adding the Makefile
# Once the Makefile is placed at the root of the project (UniMeet-main), follow the steps below.


# First time setup only:
# make env
# make install-backend
# make install-frontend
# 🔹 To run UniMeet anytime after:
# make start-both


# First-Time Setup (Run Only Once)
# 1️Create Python virtual environment
# make env

# 2️Install backend dependencies (Django, JWT, etc.)
# make install-backend

# 3️Install frontend dependencies (React/Vite)
# make install-frontend

# Run the Project (Backend + Frontend)
# To start both servers automatically:
# make start-both

# This launches Django and React/Vite at the same time.

# Future Runs (Daily Use)
# You do NOT need to reinstall anything again.
# Simply run:
# make start-both

# That’s it — the full system boots up.
# -----------------------------------------------------------