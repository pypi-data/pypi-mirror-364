### AI web app for internal corporate use


#### Development notes
Note that `uv run` will inherit and prioritize env variables from parent environment, 
which may lead to unexpected behaviour if for some reason these variables are set,
for example VS Code may automatically inject variables from .env file.

uv run alembic revision --autogenerate -m ""
uv run alembic upgrade head

uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
uv run src/ai_app/admin.py

uv run jupyter notebook --NotebookApp.token=