// Cloudflare Worker: a minimal relay so the webpage can read public Google Patents pages.
// It only fetches patents.google.com/patent/<number>/en and adds a CORS header. It stores nothing.
export default {
  async fetch(req) {
    const cors = { "Access-Control-Allow-Origin": "*" };
    const id = (new URL(req.url).searchParams.get("patent") || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
    if (!/^[A-Z]{2}[0-9]{4,}[A-Z0-9]{0,2}$/.test(id))
      return new Response("Enter a patent number like US7654321B2", { status: 400, headers: cors });
    const r = await fetch(`https://patents.google.com/patent/${id}/en`, {
      headers: { "User-Agent": "Mozilla/5.0 (compatible; OpenPatentDefenseAI)" },
      cf: { cacheTtl: 86400, cacheEverything: true },
    });
    return new Response(r.ok ? await r.text() : `Google Patents returned ${r.status}`, {
      status: r.ok ? 200 : r.status,
      headers: { ...cors, "Content-Type": "text/html; charset=utf-8" },
    });
  },
};
