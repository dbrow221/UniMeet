# =====================================================================
# WINDOWS-CMD SUPER MAKEFILE FOR FULL PROJECT AUTOMATION
# UniMeet-Main
# =====================================================================

SHELL := cmd.exe

.PHONY: run frontend backend env

run: env backend frontend

env:
	@echo Activating virtual environment...
	@call env\Scripts\activate.bat

backend:
	@echo Starting backend...
	@cd backend && python manage.py runserver

frontend:
	@echo Starting frontend...
	@cd frontend && npm run dev

# =====================================================================
# ===> Simply bash: make run
#
# Correct Position of Makefile:
# UniMeet-main/
#     frontend/
#     backend/
#     env/
#     Makefile
# =====================================================================
