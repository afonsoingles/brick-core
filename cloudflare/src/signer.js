function base64ToBytes(b64) {
  return Uint8Array.from(atob(b64), c => c.charCodeAt(0));
}

export async function signPayload(body, timestamp, privateKeyB64) {
  const keyBytes = base64ToBytes(privateKeyB64);

  const privateKey = await crypto.subtle.importKey(
    "pkcs8",
    keyBytes,
    {
      name: "ECDSA",
      namedCurve: "P-256",
    },
    false,
    ["sign"]
  );

  const data = new TextEncoder().encode(
    `${timestamp}.${body}`
  );

  console.log(`SIGN DEBUG: data string=${timestamp}.${body}`);
  console.log(`SIGN DEBUG: timestamp type=${typeof timestamp}, timestamp=${timestamp}`);

  const signature = await crypto.subtle.sign(
    { name: "ECDSA", hash: "SHA-256" },
    privateKey,
    data
  );

  const sigBytes = new Uint8Array(signature);
  console.log(`SIGN DEBUG: signature bytes length=${sigBytes.length}`);
  console.log(`SIGN DEBUG: signature bytes=${Array.from(sigBytes).map(b => b.toString(16).padStart(2, '0')).join('')}`);

  const encoded = btoa(String.fromCharCode(...sigBytes));
  console.log(`SIGN DEBUG: base64 encoded=${encoded}`);
  
  return encoded;
}
