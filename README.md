# FastAPI starter

Based on https://github.com/zhanymkanov/fastapi_production_template

This repo is kind of a template I use when starting up new FastAPI projects:
- production-ready
    - gunicorn with dynamic workers configuration (stolen from [@tiangolo](https://github.com/tiangolo))
    - Dockerfile optimized for small size and fast builds with a non-root user
    - JSON logs
    - sentry for deployed envs
- easy local development
    - environment with configured postgres and redis
    - script to lint code with `black`, `autoflake`, `isort` (also stolen from [@tiangolo](https://github.com/tiangolo))
    - configured pytest with `async-asgi-testclient`, `pytest-env`, `pytest-asyncio`
    - fully typed to comply with `mypy`
- SQLAlchemy with slightly configured `alembic`
    - async db calls with `asyncpg`
    - set up `sqlalchemy2-stubs`
    - migrations set in easy to sort format (`YYYY-MM-DD_slug`)
- pre-installed JWT authorization
    - short-lived access token
    - long-lived refresh token which is stored in http-only cookies
    - salted password storage with `bcrypt`
- global pydantic model with
    - `orjson`
    - explicit timezone setting during JSON export
- and some other extras like global exceptions, sqlalchemy keys naming convention, shortcut scripts for alembic, etc.

## Local Development

### First Build Only
1. `cp .env.example .env`
2. `docker network create traefik_webgateway`
3. make sure you have `starter_postgres` volume `docker volume create starter_postgres`
3. `docker-compose up -d --build`

### Linters
Format the code
```shell
docker compose exec app format
```

### Migrations
- Create an automatic migration from changes in `src/database.py`
```shell
docker compose exec app makemigrations *migration_name*
```
- Run migrations
```shell
docker compose exec app migrate
```
- Downgrade migrations
```shell
docker compose exec app downgrade -1  # or -2 or base or hash of the migration
```
### Tests
All tests are integrational and require DB connection.

One of the choices I've made is to use default database (`postgres`), separated from app's `app` database.
- Using default database makes it easier to run tests in CI/CD environments, since there is no need to setup additional databases
- Tests are run with `force_rollback=True`, i.e. every transaction made is then reverted

Run tests
```shell
docker compose exec app pytest
```


## Database backup

Set backup job with Crontab
```bash
crontab -e

# add the following line, update path if needed
0 1 * * * sh /home/ubuntu/polskiearchiwa.pl/archiwum/etc/backup_database.sh
```

### Restore

1. From backups file copy file with dump, for example
```bash
cp backups/postgres/archiwum_backup_13-07-2023.sql backup.sql
```
2. In `docker-compose.production.yml` uncomment volume with backup.sql file.
```yaml
  - ./backup.sql:/tmp/backup.sql 
```
3. Re-run docker db container
```bash
docker-compose -f docker-compose.production.yml up -d db
# or using available alias
dcupd db 
```
4. Login to db container bash
```bash
docker-compose -f docker-compose.production.yml exec db bash
# or using available alias
dce db bash
```
5. In docker db container login to PostgreSQL database and recreate database
```bash
psql -U postgres 
```
```postgresql
-- create temporary database because we can't drop current used database
CREATE DATABASE temp;
-- enter to temp database
\c temp
-- now we can recreate our database
DROP DATABASE postgres;
CREATE DATABASE postgres;
-- back to bash
\q
```
6. Now we have empty/fresh database, let's import dump file
```bash
psql -U postgres -d postgres < /tmp/backup.sql
```
7. Scroll to check for errors
8. You can exit from docker container
```bash
exit
```

```bash
psql -U postgres -d postgres < /tmp/backup.sql
```


## TODO (order by priority)

- celery flower - add labels for traefik
- add basic auth on production for celery flower https://doc.traefik.io/traefik/middlewares/http/basicauth/
- multi stage builds for production Dockerfile https://testdriven.io/blog/docker-best-practices/#use-multi-stage-builds
