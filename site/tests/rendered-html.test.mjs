import assert from "node:assert/strict";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(new Request("http://localhost/", { headers: { accept: "text/html" } }), { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } }, { waitUntil() {}, passThroughOnException() {} });
}

test("server-renders the O2C implementation site", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /O2C Deployment Workbench/);
  assert.match(html, /Conditional go/);
  assert.match(html, /Synthetic ERP exports/);
  assert.match(html, /80\.7%/);
  assert.match(html, /OpenTelemetry/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|Your site is taking shape/i);
});
