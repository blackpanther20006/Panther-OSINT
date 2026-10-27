import os, re, secrets, hashlib, hmac, smtplib, ssl, time
from email.message import EmailMessage
from flask import Flask, request, jsonify, session, render_template_string
from werkzeug.middleware.proxy_fix import ProxyFix

app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY",secrets.token_hex(32))
app.wsgi_app=ProxyFix(app.wsgi_app,x_proto=1,x_host=1)
app.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE="Lax",SESSION_COOKIE_SECURE=os.environ.get("PRODUCTION")=="1",MAX_CONTENT_LENGTH=2048)
PATTERN=re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
codes={}

@app.get("/")
def index():
    return render_template_string(PAGE)

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/api/me")
def me():
    return jsonify(verified=bool(session.get("email")),email=session.get("email"))

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)

@app.post("/api/verify/request")
def request_code():
    email=str((request.get_json(silent=True) or {}).get("email","")).strip().lower()
    if len(email)>254 or not PATTERN.fullmatch(email):
        return jsonify(error="Enter a valid email address."),400
    if not all(os.getenv(k) for k in ("SMTP_HOST","SMTP_USER","SMTP_PASSWORD")):
        return jsonify(error="Email OTP service is not configured yet."),503
    key=hashlib.sha256(email.encode()).hexdigest()
    if codes.get(key,{}).get("cooldown",0)>time.time():
        return jsonify(error="Wait before requesting another code."),429
    code=f"{secrets.randbelow(1000000):06d}"
    codes[key]={"hash":hashlib.sha256((code+app.secret_key).encode()).hexdigest(),"expires":time.time()+600,"cooldown":time.time()+90,"tries":0}
    message=EmailMessage()
    message["Subject"]="Panther OSINT email verification"
    message["From"]=os.getenv("SMTP_FROM") or os.getenv("SMTP_USER")
    message["To"]=email
    message.set_content("Your verification code: "+code+"\nExpires in 10 minutes.")
    try:
        host=os.environ["SMTP_HOST"]
        port=int(os.getenv("SMTP_PORT","465"))
        if port==465:
            with smtplib.SMTP_SSL(host,port,context=ssl.create_default_context(),timeout=10) as smtp:
                smtp.login(os.environ["SMTP_USER"],os.environ["SMTP_PASSWORD"])
                smtp.send_message(message)
        else:
            with smtplib.SMTP(host,port,timeout=10) as smtp:
                smtp.starttls(context=ssl.create_default_context())
                smtp.login(os.environ["SMTP_USER"],os.environ["SMTP_PASSWORD"])
                smtp.send_message(message)
    except Exception:
        app.logger.exception("Unable to send OTP")
        codes.pop(key,None)
        return jsonify(error="Unable to send verification email."),502
    return jsonify(message="Verification code sent.")

@app.post("/api/verify/confirm")
def confirm_code():
    data=request.get_json(silent=True) or {}
    email=str(data.get("email","")).strip().lower()
    code=str(data.get("code","")).strip()
    key=hashlib.sha256(email.encode()).hexdigest()
    entry=codes.get(key)
    if not entry or time.time()>entry["expires"] or entry["tries"]>=5:
        return jsonify(error="Verification expired or unavailable."),400
    entry["tries"]+=1
    digest=hashlib.sha256((code+app.secret_key).encode()).hexdigest()
    if not hmac.compare_digest(digest,entry["hash"]):
        return jsonify(error="Incorrect code."),400
    codes.pop(key,None)
    session.clear()
    session["email"]=email
    return jsonify(message="Email verified.",email=email)

PAGE="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Panther OSINT | Digital Footprint Self Audit</title>
<style>
:root{font-family:Inter,system-ui,Arial,sans-serif;color:#e9f4ff;background:#070f1d}*{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at top,#142f52,#070f1d 60%);min-height:100vh}
header{padding:22px max(20px,calc((100% - 1100px)/2));border-bottom:1px solid #24384f;display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:800;letter-spacing:1px;color:#64d4ff}.status{font-size:12px;color:#7dfbc3}
main{max-width:1100px;margin:auto;padding:64px 20px}h1{font-size:clamp(32px,5vw,56px);margin:12px 0}h1 span{color:#39bffb}
p{color:#acc3da;line-height:1.6}.eyebrow{color:#64d4ff;text-transform:uppercase;letter-spacing:2px;font-size:12px}
.panel{border:1px solid #26415d;background:#101e33;padding:28px;border-radius:16px;margin-top:28px}
label{display:block;font-weight:700;margin-bottom:12px}
input{background:#071427;border:1px solid #325171;color:white;padding:14px;border-radius:8px;width:100%;font-size:16px}
button{cursor:pointer;background:#058bd3;color:white;border:0;border-radius:8px;padding:14px 18px;font-weight:750;margin-top:12px}
button:hover{background:#1aaeff}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin:25px 0}
.tile{background:#13243c;border:1px solid #25415d;padding:20px;border-radius:12px}
a{color:#57c8ff;text-decoration:none}.tile a{display:block;font-weight:700;margin-bottom:6px}
.small{font-size:13px;color:#97b1ca}.hide{display:none}#notice{min-height:24px}
footer{padding:24px;text-align:center;color:#7693b0;border-top:1px solid #24384f}
@media(max-width:690px){.grid{grid-template-columns:1fr}main{padding:35px 18px}header{padding:18px}}
</style></head><body>
<header><div class="logo">◈ PANTHER OSINT</div><div class="status">● SELF-AUDIT DASHBOARD</div></header>
<main><div class="eyebrow">Digital security & privacy</div><h1>Know your <span>digital footprint.</span></h1>
<p>Verify an email you own, then access official account-security tools. We do not claim to identify every account or active login from an email address.</p>
<section class="panel"><h2>Email ownership verification</h2><label for="email">Your email address</label>
<input id="email" type="email" placeholder="you@example.com" autocomplete="email">
<button id="send">Send verification code</button>
<div id="verify" class="hide"><label for="code" style="margin-top:18px">6-digit code</label><input id="code" maxlength="6" inputmode="numeric" autocomplete="one-time-code" placeholder="000000"><button id="confirm">Verify email</button></div>
<p id="notice" role="status"></p></section>
<section id="tools" class="hide"><h2>My account security tools</h2><div class="grid">
<div class="tile"><a href="https://myaccount.google.com/connections" target="_blank" rel="noopener noreferrer">Google connected apps ↗</a><div class="small">View supported third-party services linked to your Google account.</div></div>
<div class="tile"><a href="https://myaccount.google.com/device-activity" target="_blank" rel="noopener noreferrer">Google device sessions ↗</a><div class="small">Review devices accessing your Google account.</div></div>
<div class="tile"><a href="https://passwords.google.com" target="_blank" rel="noopener noreferrer">Password Manager ↗</a><div class="small">See logins saved in your own Google Password Manager.</div></div>
<div class="tile"><a href="https://haveibeenpwned.com" target="_blank" rel="noopener noreferrer">Breach exposure ↗</a><div class="small">Check known data breaches using the official service.</div></div>
<div class="tile"><a href="https://myaccount.google.com/security" target="_blank" rel="noopener noreferrer">Google security ↗</a><div class="small">Review sign-in activity and strengthen security.</div></div>
<div class="tile"><a href="https://github.com/settings/security" target="_blank" rel="noopener noreferrer">GitHub security ↗</a><div class="small">Review your GitHub account's security settings.</div></div>
</div><p class="small">These links open official sites. Panther OSINT does not read or store your passwords, active sessions, or connected-app lists.</p>
<button id="logout">Clear verification</button></section>
</main><footer>© 2026 Panther OSINT · Privacy-first self-audit</footer>
<script>
const $=id=>document.getElementById(id);
const notify=t=>$("notice").textContent=t;
async function post(url,body){try{const r=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});const d=await r.json();if(!r.ok)throw Error(d.error||"Request failed");return d}catch(e){throw Error(e.message||"Network error")}}
$("send").onclick=async()=>{notify("Sending...");try{const d=await post("/api/verify/request",{email:$("email").value});notify(d.message);$("verify").classList.remove("hide")}catch(e){notify(e.message)}};
$("confirm").onclick=async()=>{try{const d=await post("/api/verify/confirm",{email:$("email").value,code:$("code").value});notify(d.message);$("tools").classList.remove("hide");$("verify").classList.add("hide")}catch(e){notify(e.message)}};
$("logout").onclick=async()=>{await post("/api/logout",{});$("tools").classList.add("hide");notify("Signed out")};
fetch("/api/me").then(r=>r.json()).then(d=>{if(d.verified){$("email").value=d.email;$("tools").classList.remove("hide");notify("Previously verified")}}).catch(()=>{});
</script></body></html>"""
if __name__=="__main__": app.run(port=int(os.getenv("PORT","5000")))
