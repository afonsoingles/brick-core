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

  const signature = await crypto.subtle.sign(
    { name: "ECDSA", hash: "SHA-256" },
    privateKey,
    data
  );

  return btoa(
    String.fromCharCode(...new Uint8Array(signature))
  );
}
