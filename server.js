// Imports
import express from "express"
import fetch from "node-fetch"
import dotenv from "dotenv"
import crypto from "crypto"
import NodeCache from "node-cache"
import fs from "fs";
import path from "path";

// Startup and variables
dotenv.config()

const app = express()
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

const redirectUri = "https://bjarnos.dev/"
const clientId = "E5F3304E-41BF-4793-A4CD-A36C04FD4B5C"
const apiUrl = "https://chat.jonazwetsloot.nl/api/v1"
const tokenUrl = `${apiUrl}/token`

const tokenSize = 24
const inactivityLimit = 75 * 60; // 1 hour, 15 minutes (client should ping every hour)

const secret = process.env.SECRET
const accessToken = process.env.ACCESS_TOKEN
const webhookUrl = process.env.DISCORD_WEBHOOK
const allowedMethods = ["post", "get", "put", "delete"]

const blockedEndpoints = {
  token: allowedMethods,
  authorize: allowedMethods,
  profile: ["post"],
  image: ["post"]
}

const cache = new NodeCache({ stdTTL: 60 })
const connectedClients = {}

// Local datastore
const dataFile = path.join(process.cwd(), "datastore.json");
function datastoreSave() {
  fs.writeFileSync(dataFile, JSON.stringify(connectedClients, null, 2), "utf-8");
}

function datastoreLoad() {
  if (fs.existsSync(dataFile)) {
    try {
      const data = fs.readFileSync(dataFile, "utf-8");
      Object.assign(connectedClients, JSON.parse(data));
    } catch (err) {
      console.error("Failed to load datastore:", err);
    }
  }
}

datastoreLoad()
setInterval(datastoreSave, 60 * 1000);
process.on("exit", datastoreSave);
process.on("SIGINT", () => { datastoreSave(); process.exit(); });
process.on("SIGTERM", () => { datastoreSave(); process.exit(); });

// Functions
const generateToken = (size = 16) =>
  crypto.randomBytes(size).toString("hex").toUpperCase()

async function sendToDiscord(content) { // log internal errors up to 10k characters
  if (typeof content !== "string" || !content.trim())
    content = "<unknown>" // gracious handling

  const token = generateToken(6)
  content = `# Ticket #${token}\n${content}\n<@820933303616012288>`

  const parts = []
  while (content.length > 0 && parts.length < 5) {
    parts.push(content.slice(0, 2000))
    content = content.slice(2000)
  }

  for (const part of parts) {
    await fetch(webhookUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: part })
    })
  }

  return token
}

// App
app.get("/ping", (req, res) => res.status(200).send("pong!"))

app.post("/active", (req, res) => {
  const { auth } = req.body
  if (!auth || typeof auth !== "string") return res.status(400).json({ success: false, reason: "Missing or invalid 'auth'" })

  const session = connectedClients[auth]
  if (!session) return res.status(403).json({ success: false, reason: "Invalid auth" })

  session.lastActive = Math.floor(Date.now() / 1000)
  return res.status(200).json({ success: true, message: "Success" })
})

app.delete("/active", (req, res) => {
  const { auth } = req.body
  if (!auth || typeof auth !== "string") return res.status(400).json({ success: false, reason: "Missing or invalid 'auth'" })

  const session = connectedClients[auth]
  if (!session) return res.status(403).json({ success: false, reason: "Invalid auth" })

  delete connectedClients[auth]
  return res.status(200).json({ success: true, message: "Success" })
})

app.post("/connect", async (req, res) => {
  const { token } = req.body
  if (!token) return res.status(400).json({ success: false, reason: "Missing argument 'token'" })
  if (typeof token !== "string") return res.status(400).json({ success: false, reason: "'token' must be a string!" })

  const params = new URLSearchParams({
    grant_type: "authorization_code",
    code: token,
    redirect_uri: redirectUri,
    client_id: clientId,
    client_secret: secret
  })

  try {
    const response = await fetch(tokenUrl, { method: "POST", body: params })
    const json = await response.json()

    if (response.ok) {
      const { access_token: aT, expires_in: ttl, refresh_token: refresh } = json
      if (!aT || !ttl || !refresh)
        return res.status(500).json({ success: false, reason: "API update detected — contact Bjarnos" })

      let userToken
      do {
        userToken = generateToken(tokenSize)
      } while (connectedClients[userToken])

      connectedClients[userToken] = { token: aT, ttl: Math.floor(Date.now() / 1000) + ttl, refresh, lastActive: Math.floor(Date.now() / 1000) }
      return res.status(200).json({ success: true, token: userToken })
    }

    return res.status(response.status === 401 ? 400 : 400).json({
      success: false,
      reason: response.status === 401 ? "Token must be refreshed!" : "Token appears to be invalid"
    })
  } catch (err) {
    const ticket = await sendToDiscord(`Fail in connect: ${err.message}`)
    return res.status(500).json({ success: false, reason: `Error logged internally, ticket #${ticket}`, ticket: ticket })
  }
})

app.post("/request", async (req, res) => {
  const { auth, method, endpoint, data: bodyData } = req.body
  if (typeof req.body !== "object") return res.status(400).json({ success: false, reason: "Data must be valid json!" })
  if (auth !== null && typeof auth !== "string") return res.status(400).json({ success: false, reason: "'auth' must be a string or null!" })
  if (typeof method !== "string") return res.status(400).json({ success: false, reason: "'method' must be a string!" })
  if (typeof endpoint !== "string") return res.status(400).json({ success: false, reason: "'endpoint' must be a string!" })
  if (typeof bodyData !== "object") return res.status(400).json({ success: false, reason: "'data' must be an object!" })

  const lowerMethod = method.toLowerCase()
  const cleanEndpoint = endpoint.split("?")[0].trim().toLowerCase()
  if ((blockedEndpoints[cleanEndpoint] || []).includes(lowerMethod))
    return res.status(403).json({ success: false, reason: "Endpoint not allowed" })
  if (!allowedMethods.includes(lowerMethod))
    return res.status(400).json({ success: false, reason: `Method must be in ${allowedMethods}` })

  let token
  if (auth) {
    const session = connectedClients[auth]
    if (!session) return res.status(403).json({ success: false, reason: "Invalid auth" })

    if (Date.now() / 1000 > session.ttl) {
      const params = new URLSearchParams({
        grant_type: "refresh_token",
        refresh_token: session.refresh,
        client_id: clientId,
        client_secret: secret
      })
      try {
        const response = await fetch(tokenUrl, { method: "POST", body: params })
        const json = await response.json()
        const { access_token: newToken, expires_in: ttl, refresh_token: refresh } = json
        if (!response.ok || !newToken || !ttl || !refresh)
          return res.status(500).json({ success: false, reason: "Refresh token invalid or API update detected" })

        token = newToken
        connectedClients[auth] = { token, ttl: Math.floor(Date.now() / 1000) + ttl, refresh, lastActive: Math.floor(Date.now() / 1000) }
      } catch (err) {
        const ticket = await sendToDiscord(`Fail in refresh: ${err.message}`)
        return res.status(500).json({ success: false, reason: `Error logged internally, ticket #${ticket}`, ticket: ticket })
      }
    } else token = session.token
  } else token = accessToken

  const fullUrl = `${apiUrl}/${endpoint}`

  try {
    if (lowerMethod === "get") {
      const query = new URLSearchParams(bodyData).toString()
      const cacheKey = `${fullUrl}?${query}`
      const cached = cache.get(cacheKey)
      if (cached) return res.status(200).json({ success: true, json: cached })

      const response = await fetch(`${fullUrl}?${query}`, { method: "GET", headers: { Authorization: `Bearer ${token}` } })
      const json = await response.json()
      if (response.ok) cache.set(cacheKey, json)
      return response.ok ? res.status(200).json({ success: true, json }) : res.status(500).json({ success: false, reason: "Endpoint failed. Check your token." })
    }

    const response = await fetch(fullUrl, {
      method: lowerMethod.toUpperCase(),
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(bodyData)
    })
    const json = await response.json()
    return response.ok ? res.status(200).json({ success: true, json }) : res.status(500).json({ success: false, reason: "Endpoint failed. Check your token." })
  } catch (err) {
    const ticket = await sendToDiscord(`Fail in request: ${err.message}`)
    return res.status(500).json({ success: false, reason: `Error logged internally, ticket #${ticket}`, ticket: ticket })
  }
})

// Tasks
setInterval(() => {
  const now = Math.floor(Date.now() / 1000)
  for (const [auth, session] of Object.entries(connectedClients)) {
    if (now - (session.lastActive) > inactivityLimit) {
      delete connectedClients[auth]
    }
  }
}, 5 * 60 * 1000) // cleanup every 5 minutes

// Final start
app.listen(3000, () => console.log("Server running on port 3000"))
