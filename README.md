# castle_sevalla

Django website for Castle General Group (castlegengroup.com), with the Plan Room document library.

## Local development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

## Sevalla deployment

1. In Sevalla, create a PostgreSQL database.
2. Create an Application from this GitHub repository (branch `main`). Sevalla builds it with
   Nixpacks, which reads `runtime.txt` (Python 3.12) and runs the `web` process in `Procfile`.
3. Connect the database to the application (**Networking → Connected services**). The app reads
   `DATABASE_URL`, or the `DB_URL` variable Sevalla adds, and refuses to start in production without one.
4. Add these environment variables to the application:
   - `SECRET_KEY`: a long random string
   - `DEBUG=False`
   - `ALLOWED_HOSTS=.sevalla.app,castlegengroup.com,www.castlegengroup.com`
   - `CLOUDINARY_URL`, or `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY` and `CLOUDINARY_API_SECRET`
5. On every deploy, `start.sh` renames legacy app tables, migrates, collects static files and
   starts Gunicorn on `$PORT`.
6. Create an admin user from the application's **Web terminal**: `python manage.py createsuperuser`.

## Custom domain (Cloudflare)

1. In Sevalla: **Domains → Add domain** for `castlegengroup.com` and `www.castlegengroup.com`.
2. In Cloudflare DNS, create the records Sevalla shows (CNAME / TXT verification).
3. Cloudflare **SSL/TLS** mode must be **Full** or **Full (strict)**, not Flexible, or the site
   will loop on HTTPS redirects.

Never commit `.env`, database files, Cloudinary credentials, or secret keys.
