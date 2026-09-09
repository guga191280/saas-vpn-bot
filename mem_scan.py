import re, subprocess
try:
    pids = subprocess.check_output("pidof Happ", shell=True).decode().strip().split()
    valid_keys = set()
    pattern = re.compile(b'(vless|vmess|trojan|hysteria2|ss)://[a-zA-Z0-9\-\_\.\@\:\?\,\&\=\#\%\+\/\~\!\;\*\x80-\xFF]+')
    for pid in pids:
        try:
            with open(f"/proc/{pid}/maps", 'r') as map_f, open(f"/proc/{pid}/mem", 'rb', 0) as mem_f:
                for line in map_f:
                    if " r" not in line: continue
                    start, end = [int(x, 16) for x in line.split()[0].split('-')]
                    try:
                        mem_f.seek(start)
                        chunk = mem_f.read(end - start)
                        for match in pattern.finditer(chunk):
                            clean = match.group(0).decode('utf-8', errors='ignore').strip()
                            if len(clean) > 20: valid_keys.add(clean)
                    except: pass
        except: pass
    
    # Сохраняем все ключи в текстовый файл
    with open("/opt/v1bot/extracted_keys.txt", "w", encoding="utf-8") as f:
        for k in valid_keys:
            f.write(k + "\n")
    print(f"✅ Успех! {len(valid_keys)} ключей надежно сохранены в файл: /opt/v1bot/extracted_keys.txt")
except Exception as e:
    print("Ошибка сканирования:", e)
