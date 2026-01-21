function base64ToBytes(b64) {
  return Uint8Array.from(atob(b64), c => c.charCodeAt(0));
}

function hexToBytes(hex) {
  const bytes = [];
  for (let i = 0; i < hex.length; i += 2) {
    bytes.push(parseInt(hex.substr(i, 2), 16));
  }
  return new Uint8Array(bytes);
}

function encodeSignatureToDER(r, s) {
  // Convert 32-byte r and s to DER SEQUENCE of two INTEGERs
  const encodeBigInt = (bytes) => {
    let hex = Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
    if (hex[0] >= '8') hex = '00' + hex;
    const len = hex.length / 2;
    return `02${len.toString(16).padStart(2, '0')}${hex}`;
  };

  const rDer = encodeBigInt(r);
  const sDer = encodeBigInt(s);
  const content = rDer + sDer;
  const len = content.length / 2;
  
  return hexToBytes(`30${len.toString(16).padStart(2, '0')}${content}`);
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
  const r = sigBytes.slice(0, 32);
  const s = sigBytes.slice(32, 64);
  
  const derSig = encodeSignatureToDER(r, s);
  const encoded = btoa(String.fromCharCode(...derSig));
  
  console.log(`SIGN DEBUG: raw signature bytes length=${sigBytes.length}`);
  console.log(`SIGN DEBUG: DER encoded length=${derSig.length}`);
  console.log(`SIGN DEBUG: base64=${encoded}`);
  
  return encoded;
}
