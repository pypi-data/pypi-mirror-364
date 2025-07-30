${framework}

${composer_json_url}

${tag}

```bash
docker compose build
docker compose up
docker compose exec -w /app app php artisan route:list --json --no-ansi --except-vendor --no-interaction
```