# Private admin panel route

Deploy `worker.js` as a Cloudflare Worker and enable its `workers.dev` hostname. Create a Cloudflare Access application for that hostname and set an Allow policy for only the account owner's exact email address. Keep all Worker paths under that Access application.

Set the Render health check path to `/health`. Add these Render environment variables:

- `DJANGO_SECRET_KEY`: a randomly generated Django signing secret.
- `CF_ACCESS_ISSUER`: `https://<your-team-name>.cloudflareaccess.com`.
- `CF_ACCESS_AUD`: the Access application's generated AUD tag.
- `ADMIN_PUBLIC_HOST`: the Worker's full `workers.dev` hostname.

The Worker proxies to the fixed Render origin in `worker.js`. The Render ASGI entrypoint serves `/health` publicly and requires a valid Cloudflare Access JWT for every panel route.
