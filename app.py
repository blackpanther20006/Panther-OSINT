import os
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/")
def index():
    return render_template_string(PAGE)

PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Panther OSINT | Public Footprint Search</title>
<style>
:root{color-scheme:dark;font-family:Inter,system-ui,Arial,sans-serif;background:#07101e;color:#eef7ff}*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:radial-gradient(ellipse at top,#143557 0,#07101e 60%)}
header{padding:24px max(20px,calc((100% - 1050px)/2));border-bottom:1px solid #254363;display:flex;justify-content:space-between;gap:20px}
.brand{font-weight:900;color:#54cbff;letter-spacing:1px}.tag{color:#82efd4;font-size:12px}
main{max-width:1050px;margin:auto;padding:55px 20px 80px}h1{font-size:clamp(32px,5vw,55px);margin:12px 0}h1 span{color:#37b7ff}
p{color:#b2c9dd;line-height:1.65}.eyebrow{color:#5cd0ff;font-size:12px;letter-spacing:2px;text-transform:uppercase}
.panel{margin-top:28px;padding:28px;background:#101f33;border:1px solid #294762;border-radius:18px}
label{display:block;font-weight:700;margin:0 0 12px}
input{width:100%;padding:16px;border:1px solid #426281;border-radius:10px;background:#0a1526;color:white;font-size:16px}
button{background:#087cce;border:0;border-radius:10px;padding:15px 22px;margin-top:14px;color:white;font-size:15px;font-weight:800;cursor:pointer}
button:hover{background:#19a4ef}.hidden{display:none}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:15px;margin-top:22px}
.tile{padding:23px;background:#11243a;border:1px solid #2b4b65;border-radius:13px}
.tile a{color:#59cfff;font-weight:800;text-decoration:none}.tile p{font-size:13px;margin-bottom:0}
.badge{color:#8ff3b8;font-size:12px}.caution{font-size:13px;color:#bed0e0}
footer{text-align:center;border-top:1px solid #29415c;padding:20px;color:#819bb6}
@media(max-width:630px){.grid{grid-template-columns:1fr}main{padding-top:33px}.panel{padding:20px}}
</style></head><body>
<header><div class="brand">◈ PANTHER OSINT</div><div class="tag">PUBLIC DATA ONLY</div></header>
<main><div class="eyebrow">Digital footprint intelligence</div>
<h1>Explore the <span>public web.</span></h1>
<p>Search publicly indexed mentions of an email address or matching username. No OTP needed for public searches. This tool does not verify that a profile belongs to the email owner.</p>
<section class="panel"><label for="email">Email address</label>
<input type="email" id="email" placeholder="name@example.com" autocomplete="off">
<button id="search">Explore public sources</button>
<p class="caution" id="message" role="status">Do not enter passwords or confidential data. Email searches are opened directly on third-party sites.</p></section>
<section id="results" class="hidden"><h2>Public search sources</h2>
<p id="details"></p>
<div class="grid">
<div class="tile"><a id="exact" target="_blank" rel="noopener noreferrer">Exact email search ↗</a><p>Look for indexed pages containing this exact email.</p></div>
<div class="tile"><a id="username" target="_blank" rel="noopener noreferrer">Username search ↗</a><p>Find pages mentioning the email local-part; matches may be unrelated.</p></div>
<div class="tile"><a id="github" target="_blank" rel="noopener noreferrer">GitHub code search ↗</a><p>Inspect public code mentions (may require sign-in).</p></div>
<div class="tile"><a id="breach" href="https://haveibeenpwned.com/" target="_blank" rel="noopener noreferrer">Breach checking ↗</a><p>Use the official site to check exposure yourself.</p></div>
<div class="tile"><a href="https://myaccount.google.com/connections" target="_blank" rel="noopener noreferrer">My connected Google apps ↗</a><p>Sign in to your own Google account to view connected third-party services.</p></div>
<div class="tile"><a href="https://myaccount.google.com/device-activity" target="_blank" rel="noopener noreferrer">My Google devices ↗</a><p>Authorized device activity is available only to the account owner.</p></div>
</div><p class="caution">A personal IP, legal name, active logins, precise location or private account details cannot be reliably determined from an email alone. These links are searches, not confirmed results.</p></section>
</main><footer>© 2026 Panther OSINT · Public footprint self-audit</footer>
<script>
const el=id=>document.getElementById(id);
el("search").onclick=()=>{
 const email=el("email").value.trim().toLowerCase();
 if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)||email.length>254){
 el("message").textContent="Enter a valid email address.";el("results").classList.add("hidden");return;
 }
 const name=email.split("@")[0],domain=email.split("@")[1];
 el("exact").href="https://www.google.com/search?q="+encodeURIComponent('"'+email+'"');
 el("username").href="https://www.google.com/search?q="+encodeURIComponent('"'+name+'"');
 el("github").href="https://github.com/search?q="+encodeURIComponent('"'+email+'"')+"&type=code";
 el("details").textContent="Address: "+email+" | Domain: "+domain+" | Username text: "+name;
 el("results").classList.remove("hidden");
 el("message").textContent="Links ready. Open each source to view public search results; no private data has been accessed.";
};
</script></body></html>'''
if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", "5000")))
