const ORIGIN = "https://ballsdex-discordbot-8ez0.onrender.com";

export default {
  async fetch(request) {
    const incoming = new URL(request.url);
    const upstream = new URL(incoming.pathname + incoming.search, ORIGIN);
    const headers = new Headers(request.headers);
    headers.set("X-Forwarded-Host", incoming.host);
    headers.set("X-Forwarded-Proto", "https");

    // Cloudflare Access adds its signed assertion after the allow policy succeeds.
    // Render verifies the signature, issuer, and audience before serving any panel route.
    return fetch(new Request(upstream, new Request(request, { headers, redirect: "manual" })));
  },
};
