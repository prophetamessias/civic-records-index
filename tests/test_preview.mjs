import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/worker.mjs";

const host = "civic-records-index-dev.example.workers.dev";
const token = "fixture-only-preview-token-never-use-real-000000000";
const configured = {
  PREVIEW_ENABLED: "true",
  PREVIEW_HOST: host,
  PREVIEW_TOKEN: token,
};
const preview = (path, env=configured, authorization) =>
  worker.fetch(new Request(`https://${host}${path}`,
    {headers: authorization ? {authorization} : {}}), env);

test("preview host does not work unless explicitly enabled", async () => {
  const r = await preview("/health", {...configured, PREVIEW_ENABLED:"false"}, `Bearer ${token}`);
  assert.equal(r.status,404);
  const q = await preview("/health", {...configured, PREVIEW_TOKEN:undefined}, `Bearer ${token}`);
  assert.equal(q.status,404);
});
test("preview host rejects requests without valid authentication", async () => {
  assert.equal((await preview("/health")).status,404);
  assert.equal((await preview("/health",configured,"Bearer wrong")).status,404);
  assert.equal((await preview("/health",configured,`Bearer ${token}extra`)).status,404);
});
test("preview host gives only read-only API access to authorized callers", async () => {
  const r = await preview("/health", configured, `Bearer ${token}`);
  assert.equal(r.status,200);
  const a = await preview("/v1/agenda-items",configured,`Bearer ${token}`);
  assert.equal(a.status,503); // no D1 binding, fail closed
  const landing = await preview("/",configured,`Bearer ${token}`);
  assert.equal(landing.status,404);
  const post = await worker.fetch(new Request(`https://${host}/health`,{
    method:"POST",headers:{authorization:`Bearer ${token}`},
  }),configured);
  assert.equal(post.status,405);
});
test("preview token never appears in error payloads", async () => {
  const r = await preview("/health",configured,`Bearer invalid-token-of-matching-length-000000`);
  assert.doesNotMatch(await r.text(),/fixture-only-preview-token/);
});
test("preview access does not alter production hostname rules", async () => {
  const r = await worker.fetch(new Request("https://api.records.dcmc.ca/health"),configured);
  assert.equal(r.status,200);
  assert.equal((await worker.fetch(new Request("https://wrong.example/health",{
    headers:{authorization:`Bearer ${token}`},
  }),configured)).status,404);
});
