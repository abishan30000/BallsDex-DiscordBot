const ORIGIN = "https://ballsdex-discordbot-8ez0.onrender.com";

export default {
  async fetch(request) {
    const incoming = new URL(request.url);
    const upstream = new URL(incoming.pathname + incoming.search, ORIGIN);
    const forwarded = new Request(request);
    forwarded.headers.set("X-Forwarded-Host", incoming.host);
    forwarded.headers.set("X-Forwarded-Proto", "https");

    // Access adds a signed assertion after its allow policy succeeds.
    // Render verifies its signature, issuer, and audience before serving the panel.
    return fetch(new Request(upstream, forwarded));
  },
};
