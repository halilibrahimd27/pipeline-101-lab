// Uygulamanin ayarlari.
//
// DIKKAT: asagidaki satir bilerek yanlis yazildi.
// Ortam degiskeni bulunamazsa devreye giren bu "yedek" deger,
// gercek bir API anahtarinin koda gomulmesi demektir.
const config = {
  apiKey: process.env.API_KEY || "sk_live_51H8xY2eZvKq9RtNmB4wPz7Xc",
  ortam: process.env.NODE_ENV || "development",
};

module.exports = config;
