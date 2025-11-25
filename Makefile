##################################################
# UniMeet Project Automation (Windows Makefile)
# -------------- see note below --------------
##################################################

SHELL := cmd.exe

# Directories
FRONTEND_DIR = frontend
BACKEND_DIR = backend
VENV_DIR = env

# Python paths in virtual environment
PYTHON = $(VENV_DIR)\Scripts\python
PIP = $(VENV_DIR)\Scripts\pip

##################################################
# 1) CREATE PYTHON ENVIRONMENT
##################################################
env:
	python -m venv $(VENV_DIR)
	@echo ✔️ Virtual environment created!

##################################################
# 2) BACKEND INSTALLATION (Auto-create requirements.txt if missing)
##################################################
install-backend:
	@if not exist $(BACKEND_DIR)\requirements.txt ( \
		echo 🛠️ Installing Django backend dependencies... & \
		cd $(BACKEND_DIR) && $(PIP) install django djangorestframework djangorestframework-simplejwt django-cors-headers python-dotenv psycopg2-binary & \
		$(PIP) freeze > $(BACKEND_DIR)\requirements.txt & \
		echo Created $(BACKEND_DIR)\requirements.txt \
	) else ( \
		echo Using existing $(BACKEND_DIR)\requirements.txt & \
		$(PIP) install -r $(BACKEND_DIR)\requirements.txt \
	)
	@echo 🎉 Backend ready!

##################################################
# 3) FRONTEND INSTALLATION
##################################################
install-frontend:
	cd $(FRONTEND_DIR) && npm install
	@echo 🎉 Frontend ready!

##################################################
# 4) RUN BACKEND SERVER (Django)
##################################################
run-backend:
	$(VENV_DIR)\Scripts\activate && cd $(BACKEND_DIR) && $(PYTHON) manage.py runserver

##################################################
# 5) RUN FRONTEND (React/Vite)
##################################################
run-frontend:
	cd $(FRONTEND_DIR) && npm run dev

##################################################
# 6) RUN BOTH SERVERS TOGETHER
##################################################
start-both:
	cmd /c "start /B make run-backend"
	cmd /c "start /B make run-frontend"
	@echo 🚀 UniMeet is now running (backend + frontend)!

##################################################
# 7) DELETE VIRTUAL ENV
##################################################
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
# 1️) Create Python virtual environment
# make env

# 2️) Install backend dependencies (Django, JWT, etc.)
# make install-backend

# 3️) Install frontend dependencies (React/Vite)
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