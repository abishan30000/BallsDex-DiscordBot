# Private admin panel access

The Worker in worker.js proxies requests to the Render service. Cloudflare Access must protect every Worker URL with an Allow rule for the owner's exact email address.

## Render configuration

Set the Render health check path to /health and configure these environment variables:

- DJANGO_SECRET_KEY: use Render's Generate button; keep it in Render only.
- CF_ACCESS_ISSUER: the Cloudflare Zero Trust team issuer URL.
- CF_ACCESS_AUD: the audience tag for the Worker Access application.
- ADMIN_PUBLIC_HOST: the Worker's full workers.dev hostname.
- BALLSDEXBOT_TOKEN: enter the Discord bot token separately when ready.

The Render app serves /health publicly for health checks. All other routes require a valid, signed Cloudflare Access JWT.
