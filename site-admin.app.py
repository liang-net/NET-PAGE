from flask import Flask, request, Response, jsonify
import json, datetime, subprocess, shlex, re, urllib.request, urllib.parse, os
from pathlib import Path

app = Flask(__name__)
USER=os.getenv('ADMIN_USER','admin')
PASS=os.getenv('ADMIN_PASS','change-me-please')
AUTH_JSON=Path('/data/auth.json')
DATA=Path('/data/site.json')
STATS=Path('/data/stats.json')
ADMIN_HTML=Path('/app/admin.html')
SSL_JSON=Path('/data/ssl.json')

DEFAULT_DATA={
 'siteTitle':'NET-PAGE','title':'欢迎来到 NET-PAGE','subtitle':'轻量、可自托管的个人主页模板（Docker Edition）。',
 'sectionTitle1':'我是谁','sectionTitle2':'我在做什么','sectionTitle3':'如何联系',
 'about1':'一名专注于自动化和运维实践的创作者，喜欢把复杂问题做成简单可复用的流程。',
 'about2':'服务器管理、部署优化、工作流自动化，以及面向中文用户的实用技术内容。',
 'about3':'可以在此处放 Telegram、邮箱、GitHub、博客等入口，统一对外展示。',
 'contact':'邮箱：hello@example.com','projectsTitle':'项目展示','timeZone':'Asia/Shanghai','backgroundImageUrl':'',
 'projects':[{'name':'项目A','desc':'示例项目描述','status':'进行中','link':'#'}]
}
DEFAULT_SSL={'domain':'','cfToken':'','cfZoneId':'','enabled':False}

def run(cmd):
    p=subprocess.run(cmd,shell=True,text=True,capture_output=True)
    return p.returncode,p.stdout.strip(),p.stderr.strip()


def load_auth():
    global USER, PASS
    if not AUTH_JSON.exists():
        AUTH_JSON.parent.mkdir(parents=True, exist_ok=True)
        AUTH_JSON.write_text(json.dumps({'user':USER,'pass':PASS},ensure_ascii=False,indent=2),encoding='utf-8')
        return
    try:
        a=json.loads(AUTH_JSON.read_text(encoding='utf-8'))
        USER=a.get('user') or USER
        PASS=a.get('pass') or PASS
    except Exception:
        pass

def save_auth(user, pwd):
    global USER, PASS
    USER=user
    PASS=pwd
    AUTH_JSON.write_text(json.dumps({'user':USER,'pass':PASS},ensure_ascii=False,indent=2),encoding='utf-8')

def ensure_data():
    if not DATA.exists():
        DATA.parent.mkdir(parents=True, exist_ok=True)
        DATA.write_text(json.dumps(DEFAULT_DATA,ensure_ascii=False,indent=2),encoding='utf-8')
    d=json.loads(DATA.read_text(encoding='utf-8'))
    for k,v in DEFAULT_DATA.items(): d.setdefault(k,v)
    return d

def save_data(d): DATA.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')

def load_ssl():
    if not SSL_JSON.exists():
        SSL_JSON.write_text(json.dumps(DEFAULT_SSL,ensure_ascii=False,indent=2),encoding='utf-8')
    s=json.loads(SSL_JSON.read_text(encoding='utf-8'))
    for k,v in DEFAULT_SSL.items(): s.setdefault(k,v)
    return s

def save_ssl(s): SSL_JSON.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')

def check(auth): return auth and auth.username==USER and auth.password==PASS

def need_auth(): return Response('Auth required',401,{'WWW-Authenticate':'Basic realm="Admin"'})

def valid_domain(d): return bool(re.fullmatch(r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}", d or ''))

@app.route('/admin')
def admin():
    if not check(request.authorization): return need_auth()
    return Response(ADMIN_HTML.read_text(encoding='utf-8'), mimetype='text/html')

@app.route('/api/data', methods=['GET','POST'])
def api_data():
    if not check(request.authorization): return need_auth()
    if request.method=='GET':
        d=ensure_data(); s=load_ssl()
        today=datetime.date.today().isoformat(); st={'total':0,'todayDate':today,'today':0}
        if STATS.exists(): st.update(json.loads(STATS.read_text(encoding='utf-8')))
        if st.get('todayDate')!=today: st['todayDate']=today; st['today']=0
        s_red={**s,'cfToken':('***'+s['cfToken'][-4:] if s.get('cfToken') else '')}
        return jsonify({'data':d,'stats':{'today':st.get('today',0),'total':st.get('total',0)},'ssl':s_red})

    payload=request.get_json(silent=True) or {}
    d=ensure_data()
    for k in ['siteTitle','title','subtitle','sectionTitle1','sectionTitle2','sectionTitle3','about1','about2','about3','projectsTitle','contact','timeZone','backgroundImageUrl']:
        if k in payload: d[k]=payload.get(k,'')
    projects=payload.get('projects',[])
    d['projects']=projects if isinstance(projects,list) else []
    save_data(d)

    if 'ssl' in payload and isinstance(payload['ssl'],dict):
        cur=load_ssl(); inc=payload['ssl']
        for k in ['domain','cfZoneId','enabled']:
            if k in inc: cur[k]=inc[k]
        if inc.get('cfToken'): cur['cfToken']=inc['cfToken']
        save_ssl(cur)
    return jsonify({'ok':True})

@app.route('/api/domain/apply', methods=['POST'])
def api_domain_apply():
    if not check(request.authorization): return need_auth()
    s=load_ssl(); domain=s.get('domain','').strip()
    if not valid_domain(domain): return jsonify({'ok':False,'error':'域名格式无效'})

    cert=f"/root/.acme.sh/{domain}_ecc/fullchain.cer"
    key=f"/root/.acme.sh/{domain}_ecc/{domain}.key"
    conf=f'''server {{\n    listen 80 default_server;\n    listen [::]:80 default_server;\n    server_name _ {domain};\n    return 301 https://$host$request_uri;\n}}\n\nserver {{\n    listen 443 ssl http2;\n    listen [::]:443 ssl http2;\n    server_name {domain};\n\n    ssl_certificate {cert};\n    ssl_certificate_key {key};\n\n    root /var/www/html;\n    index index.html;\n\n    location / {{ try_files $uri $uri/ =404; }}\n    location /admin {{ proxy_pass http://127.0.0.1:5005/admin; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; }}\n    location /api/ {{ proxy_pass http://127.0.0.1:5005/api/; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; }}\n}}\n'''
    Path('/etc/nginx/sites-available/default').write_text(conf,encoding='utf-8')
    rc,out,err=run('nginx -t && systemctl reload nginx')
    return jsonify({'ok': rc==0, 'out': out, 'err': err})

@app.route('/api/cert/issue', methods=['POST'])
def api_cert_issue():
    if not check(request.authorization): return need_auth()
    s=load_ssl(); domain=s.get('domain','').strip(); token=s.get('cfToken','').strip(); zone=s.get('cfZoneId','').strip()
    if not valid_domain(domain): return jsonify({'ok':False,'error':'请先配置有效域名'})
    if not token or not zone: return jsonify({'ok':False,'error':'请先配置 Cloudflare Token 与 Zone ID'})

    cmd=(
      f"export CF_Token={shlex.quote(token)} CF_Zone_ID={shlex.quote(zone)}; "
      f"~/.acme.sh/acme.sh --set-default-ca --server letsencrypt --force >/dev/null 2>&1; "
      f"~/.acme.sh/acme.sh --issue --dns dns_cf -d {shlex.quote(domain)} --keylength ec-256 --server letsencrypt --force"
    )
    rc,out,err=run(cmd)
    ok=(rc==0)
    msg=(out+"\n"+err).strip()[-2500:]
    return jsonify({'ok':ok,'log':msg})

@app.route('/api/cert/status')
def api_cert_status():
    if not check(request.authorization): return need_auth()
    s=load_ssl(); domain=s.get('domain','').strip()
    if not valid_domain(domain): return jsonify({'ok':False,'error':'未配置域名'})
    cert=Path(f"/root/.acme.sh/{domain}_ecc/fullchain.cer")
    if not cert.exists(): return jsonify({'ok':False,'exists':False,'error':'证书不存在'})
    rc,out,err=run(f"openssl x509 -in {shlex.quote(str(cert))} -noout -subject -issuer -dates")
    return jsonify({'ok':rc==0,'exists':True,'info':out if rc==0 else err})




@app.route('/api/auth/change', methods=['POST'])
def api_auth_change():
    if not check(request.authorization):
        return need_auth()
    payload=request.get_json(silent=True) or {}
    current=payload.get('currentPassword','')
    new_user=(payload.get('newUsername','') or '').strip()
    new_pass=payload.get('newPassword','') or ''

    if current != PASS:
        return jsonify({'ok':False,'error':'当前密码不正确'})
    if not new_user or len(new_user) < 3:
        return jsonify({'ok':False,'error':'新账号至少 3 位'})
    if len(new_pass) < 8:
        return jsonify({'ok':False,'error':'新密码至少 8 位'})

    save_auth(new_user, new_pass)
    return jsonify({'ok':True})

@app.route('/api/public-info')
def api_public_info():
    # best-effort public IP from headers
    xff=request.headers.get('X-Forwarded-For','').split(',')[0].strip()
    rip=request.headers.get('CF-Connecting-IP') or request.headers.get('X-Real-IP') or request.remote_addr or ''
    ip=xff or rip

    def jget(url, timeout=8):
        req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8','ignore'))

    geo={}
    # geo by ip first
    try:
        if ip and ip not in ('127.0.0.1','::1'):
            g=jget('https://ipwho.is/'+urllib.parse.quote(ip))
            if g and g.get('success', True) is not False:
                geo={'ip':ip,'latitude':g.get('latitude'),'longitude':g.get('longitude'),'city':g.get('city'),'region':g.get('region'),'country_name':g.get('country'),'country_code':g.get('country_code')}
    except Exception:
        pass

    if not geo:
        try:
            g=jget('https://ipwho.is/')
            if g and g.get('success', True) is not False:
                geo={'ip':g.get('ip') or ip,'latitude':g.get('latitude'),'longitude':g.get('longitude'),'city':g.get('city'),'region':g.get('region'),'country_name':g.get('country'),'country_code':g.get('country_code')}
        except Exception:
            geo={'ip':ip}

    placeZh=placeEn=''
    weather={}
    lat,lon=geo.get('latitude'),geo.get('longitude')
    try:
        if lat is not None and lon is not None:
            bzh=jget(f'https://api-bdc.io/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=zh')
            ben=jget(f'https://api-bdc.io/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en')
            placeZh=bzh.get('city') or bzh.get('locality') or bzh.get('principalSubdivision') or ''
            placeEn=ben.get('city') or ben.get('locality') or ben.get('principalSubdivision') or ''
            w=jget(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&timezone=auto')
            c=w.get('current',{}) if isinstance(w,dict) else {}
            weather={'temp':c.get('temperature_2m'),'code':c.get('weather_code')}
    except Exception:
        pass

    return jsonify({'ok':True,'geo':geo,'placeZh':placeZh,'placeEn':placeEn,'weather':weather})

@app.route('/api/stats')
def stats():
    today=datetime.date.today().isoformat(); s={'total':0,'todayDate':today,'today':0}
    if STATS.exists(): s.update(json.loads(STATS.read_text(encoding='utf-8')))
    if s.get('todayDate')!=today: s['todayDate']=today; s['today']=0
    s['total']=int(s.get('total',0))+1; s['today']=int(s.get('today',0))+1
    STATS.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
    return jsonify({'date':today,'today':s['today'],'total':s['total']})

if __name__=='__main__':
    ensure_data(); load_ssl(); load_auth(); app.run('0.0.0.0',5005)
