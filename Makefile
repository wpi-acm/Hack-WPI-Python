SHELL := /bin/bash
all: clean

# Clean up temp files
#------------------------------------------------------------------
clean:
	@echo "Cleaning up temp files"
	@find . -name '*~' -ls -delete
	@find . -name '*.bak' -ls -delete
	@echo "Cleaning up __pycache__ directories"
	@find . -name __pycache__ -type d -not -path "./.venv/*" -ls -exec rm -r {} +
	@echo "Cleaning up logfiles"
	@find ./logs -name '*.log*' -ls -delete
	@echo "Cleaning up flask_session"
	@find . -name flask_session -type d -not -path "./.venv/*" -ls -exec rm -r {} +

init_env:
	python3 -m venv .venv
	source .venv/bin/activate && pip3 install --upgrade pip
	source .venv/bin/activate && pip3 install -r requirements.txt txt

upgrade_env:
	source .venv/bin/activate && pip3 install --upgrade -r requirements.txt

make_migrations:
	source .venv/bin/activate && flask db migrate

run_migrations:
	source .venv/bin/activate && flask db upgrade

daemon:
	@echo "--- STARTING UWSGI DAEMON ---"
	@echo ""
	@echo ""	
	source .venv/bin/activate && flask --debug run
	@echo ""
	@echo ""
	@echo "--- STARTING UWSGI DAEMON ---"	
	
post_upgrade: upgrade_env run_migrations
	# Make sure a tmp directory exists
	@mkdir -p acmsite/tmp
	# Create upload directory
	@mkdir -p acmsite/uploads

