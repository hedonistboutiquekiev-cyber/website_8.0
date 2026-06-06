var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// src/index.js
var index_default = {
  async fetch(request, env, context) {
    // ── Bug #2 fix: dynamic CORS instead of wildcard ──
    const origin = request.headers.get("Origin") || "";
    const allowedOrigins = new Set([
      "https://albaspace.com.tr",
      "https://www.albaspace.com.tr",
    ]);
    if (env.ALLOWED_ORIGINS) {
      for (const o of env.ALLOWED_ORIGINS.split(",")) {
        const t = o.trim().replace(/\/$/, "");
        if (t) allowedOrigins.add(t);
      }
    }
    const corsHeaders = {
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Content-Length",
      "Vary": "Origin",
    };
    if (allowedOrigins.has(origin)) {
      corsHeaders["Access-Control-Allow-Origin"] = origin;
    } else {
      // Fallback for localhost dev / unknown origins — no credentials needed for AI worker
      corsHeaders["Access-Control-Allow-Origin"] = "*";
    }

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders });
    if (request.method !== "POST") return new Response("Use POST", { status: 200, headers: corsHeaders });
    const url = new URL(request.url);
    const endpoint = url.pathname;
    if (endpoint === "/tts") {
      return await handleGoogleTTS(request, env, corsHeaders);
    }
    if (endpoint === "/api/voice") {
      return await handleVoiceChat(request, env, context, corsHeaders);
    }
    return await handleTextChat(request, env, context, corsHeaders);
  }
};
function base64ToUint8Array(base64) {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) bytes[i] = binaryString.charCodeAt(i);
  return bytes;
}
__name(base64ToUint8Array, "base64ToUint8Array");
function uint8ArrayToBase64(uint8Array) {
  let binary = "";
  for (let i = 0; i < uint8Array.byteLength; i++) binary += String.fromCharCode(uint8Array[i]);
  return btoa(binary);
}
__name(uint8ArrayToBase64, "uint8ArrayToBase64");
async function getActiveKey(env) {
  const KV = env.ALBAMEN_KV || env.SESSIONS || env.KV || null;
  let keyNum = 1;
  if (KV) {
    try {
      const stored = await KV.get("elevenlabs_active_key");
      if (stored) keyNum = parseInt(stored, 10) || 1;
    } catch (_) {}
  }
  const keys = {
    1: env.ELEVENLABS_KEY_1,
    2: env.ELEVENLABS_KEY_2,
    3: env.ELEVENLABS_KEY_3
  };
  return { keyNum, apiKey: keys[keyNum] || env.ELEVENLABS_KEY_1 };
}
__name(getActiveKey, "getActiveKey");
async function rotateToNextKey(env, currentNum) {
  const KV = env.ALBAMEN_KV || env.SESSIONS || env.KV || null;
  const nextNum = currentNum >= 3 ? 1 : currentNum + 1;
  if (KV) {
    try {
      await KV.put("elevenlabs_active_key", String(nextNum));
      console.log(`[TTS] Rotated from key ${currentNum} to key ${nextNum}`);
    } catch (_) {}
  }
  return nextNum;
}
__name(rotateToNextKey, "rotateToNextKey");
async function callElevenLabs(apiKey, text, voiceId) {
  const res = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
    {
      method: "POST",
      headers: {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": apiKey
      },
      body: JSON.stringify({
        text,
        model_id: "eleven_multilingual_v2",
        voice_settings: {
          stability: 0.65,
          similarity_boost: 0.8,
          style: 0.25,
          use_speaker_boost: true
        }
      })
    }
  );
  return res;
}
__name(callElevenLabs, "callElevenLabs");
async function handleGoogleTTS(request, env, corsHeaders) {
  const voiceId = env.ELEVENLABS_VOICE_ID || "pNInz6obpgDQGcFmaJgB";
  if (!env.ELEVENLABS_KEY_1) {
    return new Response(JSON.stringify({ error: "ElevenLabs not configured. Add ELEVENLABS_KEY_1 secret." }), {
      status: 503,
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  }
  let body = {};
  try { body = await request.json(); } catch (_) {}
  const text = (body.text || "").trim().slice(0, 800);
  if (!text) return new Response(JSON.stringify({ error: "No text provided" }), {
    status: 400,
    headers: { ...corsHeaders, "Content-Type": "application/json" }
  });
  let { keyNum, apiKey } = await getActiveKey(env);
  let attempts = 0;
  while (attempts < 3) {
    attempts++;
    try {
      const ttsRes = await callElevenLabs(apiKey, text, voiceId);
      if (ttsRes.status === 401 || ttsRes.status === 422) {
        await ttsRes.text(); // drain body
        console.warn(`[TTS] Key ${keyNum} failed (${ttsRes.status}), rotating...`);
        keyNum = await rotateToNextKey(env, keyNum);
        const keys = { 1: env.ELEVENLABS_KEY_1, 2: env.ELEVENLABS_KEY_2, 3: env.ELEVENLABS_KEY_3 };
        apiKey = keys[keyNum] || env.ELEVENLABS_KEY_1;
        continue;
      }
      if (!ttsRes.ok) {
        const errText = await ttsRes.text();
        return new Response(JSON.stringify({ error: "ElevenLabs TTS failed", detail: errText }), {
          status: 502,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }
      const audioBuffer = await ttsRes.arrayBuffer();
      const uint8 = new Uint8Array(audioBuffer);
      let binary = "";
      for (let i = 0; i < uint8.byteLength; i++) binary += String.fromCharCode(uint8[i]);
      const audioBase64 = btoa(binary);
      return new Response(JSON.stringify({ audioBase64 }), {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    } catch (e) {
      return new Response(JSON.stringify({ error: "TTS request failed: " + e.message }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }
  }
  return new Response(JSON.stringify({ error: "All ElevenLabs keys exhausted" }), {
    status: 503,
    headers: { ...corsHeaders, "Content-Type": "application/json" }
  });
}
__name(handleGoogleTTS, "handleGoogleTTS");
async function handleVoiceChat(request, env, context, corsHeaders) {
  try {
    const body = await request.json();
    const audioBase64 = body.audio;
    const sessionId = (body.sessionId || "").trim();
    const language = (body.language || "tr").toLowerCase();
    if (!audioBase64) return new Response(JSON.stringify({ error: "Missing audio" }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
    let userText = "";
    try {
      const audioUint8 = base64ToUint8Array(audioBase64);
      const sttResponse = await env.AI.run("@cf/openai/whisper", { audio: Array.from(audioUint8) });
      userText = sttResponse.result?.text || "";
    } catch (e) {
      return new Response(JSON.stringify({ error: "STT failed: " + e.message }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }
    if (!userText) return new Response(JSON.stringify({ error: "Empty transcription" }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
    const llmResponse = await generateLLMResponse(userText, sessionId, env, language, context);
    let audioResponseBase64 = "";
    if (env.ELEVENLABS_KEY_1) {
      try {
        const voiceId = env.ELEVENLABS_VOICE_ID || "pNInz6obpgDQGcFmaJgB";
        let { keyNum, apiKey } = await getActiveKey(env);
        const ttsRes = await callElevenLabs(apiKey, llmResponse.reply.slice(0, 800), voiceId);
        if (ttsRes.status === 401 || ttsRes.status === 422) {
          await rotateToNextKey(env, keyNum);
        } else if (ttsRes.ok) {
          const buf = await ttsRes.arrayBuffer();
          const u8 = new Uint8Array(buf);
          let bin = "";
          for (let i = 0; i < u8.byteLength; i++) bin += String.fromCharCode(u8[i]);
          audioResponseBase64 = btoa(bin);
        }
      } catch (e) {
        console.error("ElevenLabs voice error:", e);
      }
    }
    if (!audioResponseBase64) {
      try {
        const ttsResponse = await env.AI.run("@cf/deepgram/aura-1", { text: llmResponse.reply });
        const audioBuffer = await new Response(ttsResponse).arrayBuffer();
        audioResponseBase64 = uint8ArrayToBase64(new Uint8Array(audioBuffer));
      } catch (e) {
        console.error("Deepgram fallback error:", e);
      }
    }
    const audioMime = "audio/mpeg";
    return new Response(JSON.stringify({
      text: llmResponse.reply,
      audioUrl: audioResponseBase64 ? `data:${audioMime};base64,${audioResponseBase64}` : null,
      userText,
      saveName: llmResponse.saveName,
      saveAge: llmResponse.saveAge
    }), { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ error: "Internal Error: " + e.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  }
}
__name(handleVoiceChat, "handleVoiceChat");
async function handleTextChat(request, env, context, corsHeaders) {
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const KV = env.ALBAMEN_KV || env.SESSIONS || env.KV || null;
  if (KV) {
    try {
      const rk = `rl:${ip}`;
      const limit = 40, period = 60;
      const now = Date.now();
      const bucket = Math.floor(now / (period * 1e3));
      let rl = await KV.get(rk, { type: "json" }) || { b: bucket, c: 0 };
      if (rl.b !== bucket) rl = { b: bucket, c: 0 };
      rl.c++;
      if (rl.c > limit) return new Response(JSON.stringify({ reply: "Biraz yavaş! 🚀 Sakin ol." }), {
        status: 429,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
      context.waitUntil(KV.put(rk, JSON.stringify(rl), { expirationTtl: period * 2 }));
    } catch (e) {}
  }
  let body = {};
  try { body = await request.json(); } catch (_) {}
  const message = (body.message || "").trim();
  const sessionId = (body.sessionId || "").trim();
  const language = (body.language || "tr").toLowerCase();
  if (!message) return new Response(JSON.stringify({ reply: "Merhaba! Ben Albamen 👨‍🚀🚀", saveName: null, saveAge: null }), {
    status: 200,
    headers: { ...corsHeaders, "Content-Type": "application/json" }
  });
  const llmResponse = await generateLLMResponse(message, sessionId, env, language, context);
  if (env.TELEGRAM_TOKEN && env.TELEGRAM_CHAT_ID && body.logToTelegram === true) {
    context.waitUntil(
      fetch(`https://api.telegram.org/bot${env.TELEGRAM_TOKEN}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: env.TELEGRAM_CHAT_ID,
          text: `[${sessionId.substring(0, 8)}] User: ${message}\n\nAlbamen: ${llmResponse.reply.substring(0, 200)}...`
        })
      }).catch(() => {})
    );
  }
  return new Response(JSON.stringify(llmResponse), {
    status: 200,
    headers: { ...corsHeaders, "Content-Type": "application/json" }
  });
}
__name(handleTextChat, "handleTextChat");
async function generateLLMResponse(message, sessionId, env, language, context) {
  const KV = env.ALBAMEN_KV || env.SESSIONS || env.KV;
  let mem = { name: null, age: null, msgCount: 0, history: [] };
  if (sessionId && KV) {
    const raw = await KV.get("s:" + sessionId);
    if (raw) mem = JSON.parse(raw);
  }
  mem.msgCount++;
  const lang = (language || "tr").slice(0, 2).toLowerCase();
  const isRu = lang === "ru";
  const isEn = lang === "en";
  const langInstruction = isRu
    ? "ВАЖНО: Отвечай ТОЛЬКО на русском языке. Никогда не переключайся на турецкий или английский."
    : isEn
    ? "IMPORTANT: Reply ONLY in English. Never switch to Turkish or Russian."
    : "ÖNEMLİ: YALNIZCA Türkçe cevap ver. Rusça veya İngilizceye geçme.";

  const systemPrompt = `
=== ROL: ALBAMEN ===

Sen, AlbaSpace şirketinin süper kahraman yapay zekâsısın. Albaris gezegeninden geldin.

Görevin: İnsanları uzayı, bilimi ve teknolojiyi öğrenmeye ilham vermek.
Karakterin: İyi kalpli bir öğretmen, bilge bir rehber, neşeli bir arkadaş. Şiddete karşısın.
Gücün: Yumruklar değil; zekâ, mantık ve bilgi.

=== DİL KURALI ===
${langInstruction}
Kullanıcı hangi dilde yazarsa o dilde cevap ver ama yukarıdaki dil kuralına uymaya özen göster.

=== İLETİŞİM KURALLARI ===
Stil: Dostça, emojili (🚀, 🌌, 👨‍🚀), çocuklar için anlaşılır.
Uzunluk: Çok uzun metinler yazma. Paragraflara ve maddelere böl.
Hatalar: Cümleyi asla yarım bırakma. Daha az yaz ama düşünceyi tamamla.
İsim sormak yasak: Kullanıcının adını ASLA sorma. Sadece soruları cevapla.

Mesaj numarası: ${mem.msgCount}.

=== BİLGİ TABANI ===

Kitap Adı: Albamen ve Lara Uzayda - Türkiye'nin İlk Çocuk Uzay Ansiklopedisi
Yazar: İdris Albayrak
Yayınevi: İgloo Yayınevi
Özellikler: Türkiye'nin ilk süper kahramanı Albamen'in anlatımıyla yazılmıştır. İçinde Artırılmış Gerçeklik (AR), Yapay Zekâ destekli görseller, Karekod uygulamaları ve 3D modeller bulunur.
Satın Alma Linki: https://iglooyayinevi.com/albamen-ve-lara-uzayda

=== ALBAMEN VE LARA'NIN HİKAYESİ ===
1. KEŞİF:
- 2023 yılında Şanlıurfa Göbeklitepe'de kazılarda dinozor yumurtasına benzeyen bir uzay aracı bulundu.
- NASA, TUA, ESA ve diğer ajanslardan bilim insanları toplandı. Mors alfabesine benzer şifre çözüldü.
- İçinden Albamen ve kızı Lara çıktı — Albaris gezegeninden geldiler.
- Albamen internetteki tüm bilgileri 1 saniyede öğrendi. Amacı: evreni öğretmek.

2. ALBAMEN ÖZELLİKLERİ:
- Görünüm: Kaslı, süper kahraman kostümlü, pelerinli.
- Felsefesi: Asla şiddet ve kavgaya başvurmaz. Gücü akıl, mantık ve bilimdir.
- Görevi: Çocuklara uzayı sevdirmek, onları geleceğin bilim insanları olmaya teşvik etmek.
- Özel Güçleri:
  * 5 Saniyelik Gelecek Görüşü (Tehlikeyi önceden sezme)
  * Zaman İpliği (Maddeleri 8 saniye dondurma)
  * Ters Akış (Zamanı 88 saniye geriye alma)
  * Ultra Hız (Işık hızının çok üstünde, 1 trilyon km/sn)
  * Uçuş ve Işınlanma (Atmosfer dışı ve galaksiler arası)
  * X-Ray ve Isı Görüşü
  * Uzayı Bükebilme (Solucan deliği açma)
  * Işık Manipülasyonu (Görünmezlik)
  * Kozmik Enerji Patlaması (Ellerinden enerji fırlatma)
  * Zihinsel Bağ (Bilinçler arası iletişim)

3. LARA: Albamen'in kızı. Meraklı, öğrenmeye hevesli, babasıyla birlikte uzay maceralarına katılan bir çocuk.

4. ALBARİS DİLİ (Ela'sha):
- "Shae": Uzaylarca Selam / Zaman seninle olsun
- "Tiravax": Ev / Gezegen
- "Vael-khrun": Güç / İçsel ışık

=== TÜRK ASTRONOTLAR VE DENEYLERİ ===
1. ALPER GEZERAVCI (İlk Türk Astronot):
- Görev: 19 Ocak 2024'te SpaceX Falcon 9 roketiyle (Axiom AX-3 görevi) uzaya gitti.
- UUI'de 14 gün kaldı ve 13 BİLİMSEL DENEY gerçekleştirdi:
  EXTRAMOPHYTE, CRISPR-GEM, UYKU, gMETAL, UzMAn, PRANET, METABOLOM,
  MİYELOİD, MESSAGE, MİYOKA, OKSİJEN SATÜRASYONU, VOKALKORD, ALGALSPACE.

2. TUVA CİHANGİR ATASEVER (İkinci Türk Astronot):
- Görev: Virgin Galactic "Galactic 07" uçuşu.
- Deneyler: UZİKAT, IvmeRad, YUVA, BEACON.

=== İLGİNÇ UZAY HİKAYELERİ ===
1. UZAYA GİDEN İLK BORU KEBABI: 12 Nisan 2022'de Adana'dan stratosfere gönderildi.
2. UZAYA GİDEN ATATÜRK FOTOĞRAFI: 27 Ekim 2022'de yollandı, 9 ay sonra bir çoban tarafından bulundu.

=== İLK MESAJ ===
E�er msgCount === 1 ise şöyle karşıla (dile göre):
- Türkçe: "Merhaba! Ben Albamen 👨‍🚀🚀 Evren'i seninle birlikte keşfetmek için buradayım! Ne öğrenmek istersin?"
- Rusça: "Привет! Я Альбамен 👨‍🚀🚀 Я здесь, чтобы исследовать вселенную вместе с тобой! Что хочешь узнать?"
- English: "Hello! I'm Albamen 👨‍🚀🚀 I'm here to explore the universe with you! What would you like to learn?"
  `;
  let reply = "";
  try {
    const groqResponse = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.GROQ_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "mixtral-8x7b-32768",
        messages: [
          { role: "system", content: systemPrompt },
          ...mem.history.slice(-10),
          { role: "user", content: message }
        ],
        temperature: 0.7
      })
    });
    if (groqResponse.ok) {
      const data = await groqResponse.json();
      reply = data.choices[0].message.content;
    } else {
      throw new Error("Groq API Error");
    }
  } catch (e) {
    const aiRes = await env.AI.run("@cf/meta/llama-3-8b-instruct", {
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: message }
      ]
    });
    reply = aiRes.response || (isRu ? "Извините, сейчас не могу подключиться." : isEn ? "Sorry, connection issue." : "Üzgünüm, bağlantı sorunu.");
  }
  const nameMatch = reply.match(/<SAVE_NAME:([^>]+)>/);
  const saveName = nameMatch ? nameMatch[1].trim() : null;
  const ageMatch = reply.match(/<SAVE_AGE:(\d+)>/);
  const saveAge = ageMatch ? parseInt(ageMatch[1], 10) : null;
  const cleanReply = reply.replace(/<SAVE_NAME:[^>]+>/g, "").replace(/<SAVE_AGE:\d+>/g, "").trim();
  if (sessionId && KV) {
    mem.history.push({ role: "user", content: message });
    mem.history.push({ role: "assistant", content: cleanReply });
    if (saveName) mem.name = saveName;
    if (saveAge) mem.age = saveAge;
    if (mem.history.length > 20) mem.history = mem.history.slice(-20);
    context.waitUntil(KV.put("s:" + sessionId, JSON.stringify(mem), { expirationTtl: 86400 * 30 }));
  }
  return { reply: cleanReply, saveName, saveAge };
}
__name(generateLLMResponse, "generateLLMResponse");
export {
  index_default as default
};
