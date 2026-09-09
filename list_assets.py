import urllib.request, json
try:
    req = urllib.request.Request("https://api.github.com/repos/Omegaplexx/hpwnr/releases/latest", headers={"User-Agent": "Mozilla/5.0"})
    data = json.loads(urllib.request.urlopen(req).read().decode())
    print("=== ДОСТУПНЫЕ ФАЙЛЫ ===")
    for a in data.get('assets', []):
        print(a['browser_download_url'])
except Exception as e:
    print("Ошибка:", e)
