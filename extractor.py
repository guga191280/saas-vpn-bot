import subprocess
import os

def extract_vless_keys(happ_link):
    happ_bin = "/root/happ_extracted/opt/happ/bin/Happ"
    core_file = "/tmp/happ_ram.core"
    
    if os.path.exists(core_file):
        try:
            os.remove(core_file)
        except:
            pass
            
    cmd = f'xvfb-run gdb -batch -ex "b exit" -ex "run --test-crypt5 \\"{happ_link}\\"" -ex "gcore {core_file}" {happ_bin} > /opt/v1bot/logs/gdb.log 2>&1'
    
    try:
        subprocess.run(cmd, shell=True, timeout=20)
        
        if not os.path.exists(core_file):
            return None
            
        extract_cmd = f'strings {core_file} | grep -oE "vless://[^\\" ]+" | sort -u'
        result = subprocess.check_output(extract_cmd, shell=True, text=True)
        
        keys = [line for line in result.splitlines() if line.startswith("vless://")]
        valid_keys = [k for k in keys if len(k) > 40 and "vless://" in k]
        return valid_keys if valid_keys else None
    except Exception as e:
        return None
