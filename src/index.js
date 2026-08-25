const _ = require("lodash");
const config = require("./config");

function selamla(isim) {
  return `Merhaba ${_.capitalize(isim)}!`;
}

function ortamBilgisi() {
  return `Ortam: ${config.ortam}`;
}

if (require.main === module) {
  console.log(selamla("dunya"));
  console.log(ortamBilgisi());
}

module.exports = { selamla, ortamBilgisi };
