import express from "express";
import fetch from "node-fetch";
import dotenv from "dotenv";
import crypto from "crypto";
import NodeCache from "node-cache";

dotenv.config();

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const secret = process.env.SECRET;
const accessToken = process.env.ACCESS_TOKEN;
const allowedMethods = ["post", "get", "put", "delete"];
const restrictedEndpoints = ["token", "authorize", "profile", "image"];
      // these endpoints either allow unnecessary spam or can be used for hacking through the library,
      // so let's not accept those
const cache = new NodeCache({ stdTTL: 60 });

const connectedClients = {};

function generateUserToken(size = 16) {
  return crypto.randomBytes(size).toString("hex").toUpperCase();
}

function getToken(auth) {
  const collection = connectedClients[auth];
  return collection ? collection.token : null;
}

app.post("/c", async (req, res) => {
  let { token } = req.body;
  if (!token) return res.status(400).json({ success: false, reason: "Missing argument 'token'" });
  if (typeof token !== "string") return res.status(400).json({ success: false, reason: "'token' must be a string!" });

  const data = new URLSearchParams({
    grant_type: "authorization_code",
    code: token,
    redirect_uri,
    client_id,
    client_secret: secret,
  });

  try {
    const response = await fetch(token_url, { method: "POST", body: data });
    const jsonr = await response.json();

    if (response.ok) {
      const accessToken = jsonr.access_token;
      const ttl = jsonr.expires_in;

      if (accessToken && ttl) {
        let userToken;
        do {
          userToken = generateUserToken(token_size);
        } while (connectedClients[userToken]);

        connectedClients[userToken] = { token: accessToken, ttl: Math.round(Date.now() / 1000) + ttl };
        return res.status(200).json({ success: true, token: userToken });
      } else {
        return res.status(500).json({ success: false, reason: "Jona seems to have updated the Chat API, please reach out to Bjarnos on Chat" });
      }
    } else if (response.status === 401) {
      return res.status(400).json({ success: false, reason: "Token must be refreshed!" });
    } else {
      return res.status(400).json({ success: false, reason: "Token appears to be invalid" });
    }
  } catch (err) {
    return res.status(500).json({ success: false, reason: err.message });
  }
});

app.post("/r", async (req, res) => {
  const data = req.body;
  if (typeof data !== "object") return res.status(400).json({ success: false, reason: "Data must be valid json!" });

  const { auth, method, endpoint, data: bodyData } = data;
  if (auth !== null && typeof auth !== "string") return res.status(400).json({ success: false, reason: "'auth' must be a string or null!" });
  if (typeof method !== "string") return res.status(400).json({ success: false, reason: "'method' must be a string!" });
  if (typeof endpoint !== "string") return res.status(400).json({ success: false, reason: "'endpoint' must be a string!" });
  if (typeof bodyData !== "object") return res.status(400).json({ success: false, reason: "'data' must be an object!" });

  const lowerMethod = method.toLowerCase();
  const cleanEndpoint = endpoint.split("?")[0].trim().toLowerCase(); // no bypass please :)
  if (restrictedEndpoints.includes(cleanEndpoint) && !(lowerMethod == "get" && cleanEndpoint == "image")) return res.status(403).json({ success: false, reason: "Endpoint not allowed" });
  if (!allowedMethods.includes(lowerMethod)) return res.status(400).json({ success: false, reason: `Method must be in ${allowedMethods} (case insensitive)!` });

  const token = auth ? getToken(auth) : accessToken;
  if (!token) return res.status(401).json({ success: false, reason: "Invalid auth" });

  const fullUrl = `${api_url}/${endpoint}`;

  try {
    if (lowerMethod === "get") {
      const urlParams = new URLSearchParams(bodyData).toString();
      const cacheKey = `${fullUrl}?${urlParams}`;
      const cached = cache.get(cacheKey);
      if (cached) return res.status(200).json({ success: true, json: cached });

      const response = await fetch(`${fullUrl}?${urlParams}`, { method: "GET", headers: { Authorization: `Bearer ${token}` } });
      const json = await response.json();
      if (response.ok) cache.set(cacheKey, json);
      return response.ok ? res.status(200).json({ success: true, json }) : res.status(500).json({ success: false, reason: "Endpoint failed. Check your token." });
    } else {
      const response = await fetch(fullUrl, {
        method: lowerMethod.toUpperCase(),
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify(bodyData)
      });
      const json = await response.json();
      return response.ok ? res.status(200).json({ success: true, json }) : res.status(500).json({ success: false, reason: "Endpoint failed. Check your token." });
    }
  } catch (err) {
    return res.status(500).json({ success: false, reason: err.message });
  }
});

app.listen(3000, () => console.log("Server running on port 3000"));
