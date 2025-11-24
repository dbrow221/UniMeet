# =====================================================================
# UniMeet Automated Makefile (Windows CMD)
# - Activates Python venv
# - Installs npm dependencies automatically
# - Runs backend + frontend
# =====================================================================

SHELL := cmd.exe

.PHONY: run env backend frontend deps-frontend

run: env deps-frontend backend frontend

# ----------------------
# PYTHON ENV SETUP
# ----------------------
env:
	@echo Activating virtual environment...
	@call env\Scripts\activate.bat

# ----------------------
# INSTALL FRONTEND DEPS (ONLY IF MISSING)
# ----------------------
deps-frontend:
	@if not exist frontend\\node_modules ( \
		echo Installing frontend dependencies... && \
		cd frontend && npm install \
	) else ( \
		echo Frontend dependencies already installed. \
	)

# ----------------------
# START BACKEND
# ----------------------
backend:
	@echo Starting backend...
	@cd backend && python manage.py runserver

# ----------------------
# START FRONTEND
# ----------------------
frontend:
	@echo Starting frontend...
	@cd frontend && npm run dev
	