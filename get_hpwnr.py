import urllib.request, re, os

url_found = ""
try:
    req = urllib.request.urlopen("https://github.com/Omegaplexx/hpwnr/releases/latest")
    html = req.read().decode('utf-8')
    # Ищем все ссылки на скачивание
    links = re.findall(r'href="(/Omegaplexx/hpwnr/releases/download/[^"]+)"', html)
    for link in links:
        link_lower = link.lower()
        # Жесткий фильтр: нужен linux и x86_64, но без arm и lite
        if 'linux' in link_lower and 'arm' not in link_lower and 'lite' not in link_lower and ('x86_64' in link_lower or 'amd64' in link_lower):
            url_found = "https://github.com" + link
            break
except Exception as e:
    print(f"Ошибка парсинга: {e}")

if url_found:
    print(f"✅ Найдена правильная версия: {url_found}")
    os.system(f"wget '{url_found}' -O hpwnr && chmod +x hpwnr")
else:
    print("❌ Не удалось найти x86_64 версию.")
