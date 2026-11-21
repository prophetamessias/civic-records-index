import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/worker.mjs";
const get = (path, env={}) => worker.fetch(new Request("https://api.records.dcmc.ca"+path),env);
test("health endpoint only on approved API hostname",async()=>{
  const r=await get("/health"); assert.equal(r.status,200);
  assert.equal((await r.json()).status,"ok");
  const wrong=await worker.fetch(new Request("https://evil.example/health"),{});
  assert.equal(wrong.status,404);
});
test("landing page contains public project only",async()=>{
  const r=await worker.fetch(new Request("https://records.dcmc.ca/"),{});
  assert.equal(r.status,200);
  assert.match(await r.text(),/Live indexing is not active/);
  assert.equal((await worker.fetch(new Request("https://records.dcmc.ca/v1/agenda-items"),{})).status,404);
});
test("public data endpoint fails closed without D1",async()=>{
 const r=await get("/v1/agenda-items");
 assert.equal(r.status,503);
 assert.deepEqual(await r.json(),{error:"temporarily_unavailable"});
});
test("only uses approved/verified/reuse-cleared records query",async()=>{
 let sql="", bound;
 const DB={prepare(query){sql=query; return {bind(n){bound=n;return {async all(){return {results:[]}}}}}}};
 const r=await get("/v1/agenda-items",{DB});
 assert.equal(r.status,200);
 assert.deepEqual((await r.json()).records,[]);
 assert.match(sql,/disposition_verified\s*=\s*1/);
 assert.match(sql,/pr\.status\s*=\s*'approved'/);
 assert.match(sql,/dv\.verification_status\s*=\s*'verified'/);
 assert.match(sql,/dv\.rights_review\s*=\s*'approved'/);
 assert.equal(bound,50);
});
test("database errors never expose internals",async()=>{
 const DB={prepare(){throw new Error("sensitive database error")}};
 const r=await get("/v1/agenda-items",{DB});
 assert.deepEqual(await r.json(),{error:"temporarily_unavailable"});
});
test("no mutation methods, HEAD supported",async()=>{
 const r=await worker.fetch(new Request("https://api.records.dcmc.ca/v1/agenda-items",{method:"POST"}),{});
 assert.equal(r.status,405);
 const h=await worker.fetch(new Request("https://api.records.dcmc.ca/health",{method:"HEAD"}),{});
 assert.equal(h.status,200);
 assert.equal(await h.text(),"");
});
