from flask import Flask, request, Response
from flask_cors import CORS
import requests
import logging
import json
from typing import Any, Iterable

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# UTF-8 için ayar
app.config['JSON_AS_ASCII'] = False

TARGET_APIS = {
    "adsoyad": "https://api.kahin.org/kahinapi/adsoyad",
    "tc": "https://api.kahin.org/kahinapi/tc",
    "secmen": "https://hanedansystem.alwaysdata.net/hanesiz/secmen.php",
    "ogretmen": "https://hanedansystem.alwaysdata.net/hanesiz/ogretmen.php",
    "smsbomber": "https://hanedansystem.alwaysdata.net/hanesiz/smsbomber.php",
    "yabanci": "https://hanedansystem.alwaysdata.net/hanesiz/yabanci.php",
    "log": "https://hanedansystem.alwaysdata.net/hanesiz/log.php",
    "vesika2": "https://hanedansystem.alwaysdata.net/hanesiz/vesika.php",
    "tapu2": "https://hanedansystem.alwaysdata.net/hanesiz/tapu.php",
    "iskaydi": "https://hanedansystem.alwaysdata.net/hanesiz/iskaydi.php",
    "sertifika2": "https://hanedansystem.alwaysdata.net/hanesiz/sertifika.php",
    "papara": "https://hanedansystem.alwaysdata.net/hanesiz/papara.php",
    "ininal": "https://hanedansystem.alwaysdata.net/hanesiz/ininal.php",
    "turknet": "https://hanedansystem.alwaysdata.net/hanesiz/turknet.php",
    "serino": "https://hanedansystem.alwaysdata.net/hanesiz/serino.php",
    "firma": "https://hanedansystem.alwaysdata.net/hanesiz/firma.php",
    "craftrise": "https://hanedansystem.alwaysdata.net/hanesiz/craftrise.php",
    "sgk2": "https://hanedansystem.alwaysdata.net/hanesiz/sgk.php",
    "plaka2": "https://hanedansystem.alwaysdata.net/hanesiz/plaka.php",
    "plakaismi": "https://hanedansystem.alwaysdata.net/hanesiz/plakaismi.php",
    "plakaborc": "https://hanedansystem.alwaysdata.net/hanesiz/plakaborc.php",
    "akp": "https://hanedansystem.alwaysdata.net/hanesiz/akp.php",
    "aifoto": "https://hanedansystem.alwaysdata.net/hanesiz/AiFoto.php",
    "insta": "https://hanedansystem.alwaysdata.net/hanesiz/insta.php",
    "facebook_hanedan": "https://hanedansystem.alwaysdata.net/hanesiz/facebook.php",
    "uni": "https://hanedansystem.alwaysdata.net/hanesiz/uni.php",
    "lgs_hanedan": "https://hanedansystem.alwaysdata.net/hanesiz/lgs.php",
    "okulno_hanedan": "https://hanedansystem.alwaysdata.net/hanesiz/okulno.php",
    "tc_sorgulama": "https://api.kahin.org/kahinapi/tc",
    "tc_pro_sorgulama": "https://api.kahin.org/kahinapi/tcpro",
    "hayat_hikayesi": "https://api.kahin.org/kahinapi/hayathikayesi.php",
    "ad_soyad": "https://api.kahin.org/kahinapi/adsoyad",
    "ad_soyad_pro": "https://api.kahin.org/kahinapi/tapu",
    "is_yeri": "https://api.kahin.org/kahinapi/isyeri",
    "vergi_no": "https://api.kahin.org/kahinapi/vergino",
    "yas": "https://api.kahin.org/kahinapi/yas",
    "tc_gsm": "https://api.kahin.org/kahinapi/tcgsm",
    "gsm_tc": "https://api.kahin.org/kahinapi/gsmtc",
    "adres": "https://api.kahin.org/kahinapi/adres.php",
    "hane": "https://api.kahin.org/kahinapi/hane",
    "apartman": "https://api.kahin.org/kahinapi/apartman",
    "ada_parsel": "https://api.kahin.org/kahinapi/adaparsel",
    "adi_il_ilce": "https://api.kahin.org/kahinapi/adililce.php",
    "aile": "https://api.kahin.org/kahinapi/aile",
    "aile_pro": "https://api.kahin.org/kahinapi/ailepro",
    "es": "https://api.kahin.org/kahinapi/es",
    "sulale": "https://api.kahin.org/kahinapi/sulale",
    "lgs": "https://api.kahin.org/kahinapi/lgs",
    "e_kurs": "https://api.kahin.org/kahinapi/ekurs",
    "ip": "https://api.kahin.org/kahinapi/ip",
    "dns": "https://api.kahin.org/kahinapi/dns",
    "whois": "https://api.kahin.org/kahinapi/whois",
    "subdomain": "https://api.kahin.org/kahinapi/subdomain.php",
    "leak": "https://api.kahin.org/kahinapi/leak.php",
    "telegram": "https://api.kahin.org/kahinapi/telegram.php",
    "sifre_encrypt": "https://api.kahin.org/kahinapi/encrypt"
}

# Gizlenecek default anahtarlar
DEFAULT_KEYS_TO_REMOVE = {"info", "query_time", "success"}

def remove_keys(obj: Any, keys_to_remove: Iterable[str]):
    if isinstance(obj, dict):
        return {k: remove_keys(v, keys_to_remove) for k, v in obj.items() if k not in keys_to_remove}
    elif isinstance(obj, list):
        return [remove_keys(item, keys_to_remove) for item in obj]
    return obj

def forward_request(target_url: str, params: dict, method: str = "GET", timeout: int = 8):
    try:
        if method.upper() == "GET":
            resp = requests.get(target_url, params=params, timeout=timeout)
        else:
            resp = requests.post(target_url, json=params, timeout=timeout)

        resp.raise_for_status()
        try:
            return resp.json(), resp.status_code
        except ValueError:
            return {"raw_text": resp.text}, resp.status_code
    except requests.Timeout:
        return {"error": "Hedef API zaman aşımına uğradı."}, 504
    except requests.HTTPError as e:
        code = e.response.status_code if e.response else 502
        try:
            body = e.response.json()
        except Exception:
            body = {"error": e.response.text if e.response else str(e)}
        return body, code
    except Exception as e:
        logging.exception("Forward error")
        return {"error": f"Beklenmedik hata: {str(e)}"}, 500

@app.route("/")
def home():
    """Ana sayfa - API bilgileri"""
    return Response(
        json.dumps({
            "message": "KenevizSystem API",
            "creator": "@Sanalsantaj",
            "telegram_channel": "https://t.me/KenevizApiSystem",
            "available_services": list(TARGET_APIS.keys()),
            "total_services": len(TARGET_APIS)
        }, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )

@app.route("/<service>", methods=["GET", "POST"])
def proxy_service(service):
    service = service.lower()
    if service not in TARGET_APIS:
        return Response(
            json.dumps({
                "ok": False, 
                "error": "Böyle bir servis yok", 
                "available": list(TARGET_APIS.keys()),
                "creator": "@Sanalsantaj",
                "telegram": "https://t.me/KenevizApiSystem"
            }, ensure_ascii=False, indent=2),
            content_type="application/json; charset=utf-8",
            status=404
        )

    target_url = TARGET_APIS[service]
    params = request.args.to_dict() if request.method == "GET" else (request.get_json(silent=True) or request.form.to_dict() or {})

    result, status_code = forward_request(target_url, params, method=request.method)

    hide_param = request.args.get("hide") or (params.get("hide") if isinstance(params, dict) else None)
    keys_to_remove = set([k.strip() for k in hide_param.split(",") if k.strip()]) if hide_param else DEFAULT_KEYS_TO_REMOVE

    sanitized = remove_keys(result, keys_to_remove)

    return Response(
        json.dumps({
            "ok": True,
            "service": service,
            "creator": "@Sanalsantaj",
            "telegram": "https://t.me/KenevizApiSystem",
            "requested_params": params,
            "response": sanitized
        }, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
        status=status_code
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
