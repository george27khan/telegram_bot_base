FROM python:3.9.0

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install poetry

COPY ./.env ./.env
COPY pyproject.toml poetry.lock ./
COPY ./main.py ./main.py

RUN poetry config virtualenvs.create false \
    && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

ENTRYPOINT ["python3", "main.py"]