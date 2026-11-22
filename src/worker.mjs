// Public-only, read-only Worker entry point. NEVER serves source caches, internal notes,
// unreviewed source records, agent logs, credentials or private Council Office data.
const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
  "referrer-policy": "no-referrer",
  "access-control-allow-origin": "*",
};
const PAGE_HEADERS = {
  "content-type": "text/html; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
  "content-security-policy": "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
};
const HOSTS = Object.freeze({
  records: "records.dcmc.ca",
  api: "api.records.dcmc.ca",
});
const MAX_RESULTS = 50;
function json(body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: JSON_HEADERS });
}
function landing() {
  return new Response(`<!doctype html><html lang="en"><meta charset="utf-8">
<title>Civic Records Index</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{font:16px system-ui,sans-serif;max-width:720px;margin:12vh auto;padding:24px;line-height:1.55;color:#17212b}a{color:#174ea6}</style>
<h1>Civic Records Index</h1>
<p>Source-first municipal public-record research infrastructure. Windsor, Ontario is the first planned source.</p>
<p>Public records are published only after source and rights verification and human review. Live indexing is not active.</p>
<p><a href="https://github.com/prophetamessias/civic-records-index">Open-source project on GitHub</a></p>
</html>`, {status: 200, headers: PAGE_HEADERS});
}
// Avoid exposing internal details and ensure all public records pass multiple gates.
const PUBLIC_ITEMS_SQL = `
SELECT ai.id AS id,
       ai.item_number AS item_number,
       ai.title AS title,
       ai.disposition AS disposition,
       m.body AS meeting_body,
       m.meeting_date AS meeting_date
FROM agenda_items AS ai
JOIN meetings AS m ON m.id = ai.meeting_id
WHERE ai.disposition_verified = 1
  AND EXISTS (
    SELECT 1 FROM publication_reviews AS pr
    WHERE pr.item_id = ai.id AND pr.status = 'approved'
      AND pr.reviewer IS NOT NULL AND pr.reviewed_at IS NOT NULL
  )
  AND EXISTS (
    SELECT 1 FROM agenda_item_documents AS aid
    JOIN document_versions AS dv ON dv.id = aid.version_id
    JOIN documents AS d ON d.id = dv.document_id
    WHERE aid.item_id = ai.id
      AND d.current_version_id = dv.id
      AND dv.verification_status = 'verified'
      AND dv.rights_review = 'approved'
  )
ORDER BY m.meeting_date DESC, m.body, ai.item_number
LIMIT ?1`;
function isExpectedHost(hostname) {
  return hostname === HOSTS.api || hostname === HOSTS.records;
}
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!isExpectedHost(url.hostname)) return json({ error: "not_found" }, 404);
    if (request.method !== "GET" && request.method !== "HEAD") return json({ error: "method_not_allowed" }, 405);
    if (url.hostname === HOSTS.records) {
      if (url.pathname !== "/") return json({ error: "not_found" }, 404);
      const response = landing();
      return request.method === "HEAD" ? new Response(null, {status:200, headers:response.headers}) : response;
    }
    if (url.pathname === "/health") {
      return request.method === "HEAD"
        ? new Response(null, {status:200,headers:JSON_HEADERS})
        : json({service:"civic-records-index",status:"ok",version:"pre-release"});
    }
    if (url.pathname === "/v1/agenda-items") {
      if (!env?.DB || typeof env.DB.prepare !== "function") return json({error:"temporarily_unavailable"},503);
      try {
        const result = await env.DB.prepare(PUBLIC_ITEMS_SQL).bind(MAX_RESULTS).all();
        const records = Array.isArray(result?.results) ? result.results.map((r) => ({
          id:r.id, item_number:r.item_number, title:r.title,
          disposition:r.disposition, meeting_body:r.meeting_body,
          meeting_date:r.meeting_date,
        })) : [];
        return request.method === "HEAD"
          ? new Response(null,{status:200,headers:JSON_HEADERS})
          : json({records, count: records.length, limit:MAX_RESULTS});
      } catch {
        return json({error:"temporarily_unavailable"},503);
      }
    }
    return json({error:"not_found"},404);
  },
};
