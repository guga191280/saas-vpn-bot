import subprocess
import requests
import base64
import re

def extract_vless_keys(happ_link):
    happ_link = happ_link.strip()
    keys = set()
    sub_url = ""
    try:
        # 1. Запуск бинарника hpwnr
        result = subprocess.check_output(
            ['/opt/v1bot/hpwnr', happ_link], 
            stderr=subprocess.STDOUT, 
            timeout=15
        ).decode('utf-8').strip()
        
        sub_url = result
        raw_text = result

        # 2. Умный поиск URL
        url_match = re.search(r'https?://[^\s"\'{]+', result)
        if url_match:
            target_url = url_match.group(0)
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(target_url, headers=headers, timeout=10)
                fetched_text = response.text
                raw_text += "\n" + fetched_text
                
                # 3. Декодирование Base64
                if not re.search(r'(vless|vmess|trojan|ss|ssr|hy2)://', fetched_text):
                    try:
                        padded_text = fetched_text.strip()
                        padded_text += "=" * ((4 - len(padded_text) % 4) % 4)
                        decoded = base64.b64decode(padded_text).decode('utf-8', errors='ignore')
                        raw_text += "\n" + decoded
                    except Exception:
                        pass
            except Exception as e:
                raw_text += f"\n[HTTP_ERROR]: {e}"

        # 4. Финальный поиск ключей
        pattern = re.compile(r'(vless|vmess|trojan|ss|ssr|hy2)://[^\s]+')
        for match in pattern.finditer(raw_text):
            clean_key = match.group(0).strip().rstrip('<>\'"()\\')
            if len(clean_key) > 20:
                keys.add(clean_key)
        
        unique_keys = list(keys)
        
        # 5. ОТЛАДКА
        if not unique_keys:
            unique_keys = [
                "vless://00000000-0000-0000-0000-000000000000@127.0.0.1:443?security=none#ОШИБКА",
                "--- ОТПРАВЬ МНЕ ЭТОТ ФАЙЛ ---",
                result,
                "--- СКАЧАННЫЙ ТЕКСТ ---",
                raw_text
            ]
        
        return sub_url, unique_keys
    except Exception as e:
        print(f"Extraction error: {e}")
        return None, None
