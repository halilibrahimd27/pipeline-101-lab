const test = require("node:test");
const assert = require("node:assert");
const { selamla, ortamBilgisi } = require("./index");

test("selamla ismi buyuk harfle baslatir", () => {
  assert.strictEqual(selamla("ayse"), "Merhaba Ayse!");
});

test("ortam bilgisi bir metin dondurur", () => {
  assert.ok(ortamBilgisi().startsWith("Ortam:"));
});
