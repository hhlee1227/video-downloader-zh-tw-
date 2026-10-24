import sys
import struct
import plistlib
import json
import uuid
import datetime
import argparse
import cryptography.x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import aea

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return "<bytes>"
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)

def extract_logic_to_txt(shortcut_dict, txt_path):
    actions = shortcut_dict.get('WFWorkflowActions', [])
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=== SHORTCUT LOGIC ===\n\n")
        for i, action in enumerate(actions):
            identifier = action.get('WFWorkflowActionIdentifier', 'Unknown Action')
            # Make the identifier cleaner (e.g., is.workflow.actions.filter.photos -> filter.photos)
            clean_id = identifier.replace('is.workflow.actions.', '')
            f.write(f"[{i+1}] {clean_id}\n")
            
            params = action.get('WFWorkflowActionParameters', {})
            for k, v in params.items():
                if k == 'UUID': continue
                
                # Simplify nested dictionaries for readability
                if isinstance(v, dict) and 'Value' in v:
                    v = v['Value']
                
                # Truncate very long strings or bytes
                v_str = str(v)
                if len(v_str) > 200:
                    v_str = v_str[:200] + "... (truncated)"
                    
                f.write(f"    - {k}: {v_str}\n")
            f.write("\n")

def decode_shortcut(file_path):
    import os
    base_path = os.path.splitext(file_path)[0]
    out_path = base_path + ".json"
    txt_path = base_path + ".txt"

    print(f"[*] Reading shortcut file: {file_path}")
    with open(file_path, 'rb') as f:
        data = f.read()

    shortcut_dict = None

    if not data.startswith(b"AEA1"):
        print("[-] Not a signed iOS 15+ shortcut (no AEA1 header).")
        try:
            shortcut_dict = plistlib.loads(data)
        except Exception as e:
            print(f"[-] Failed to parse as raw bplist: {e}")
            return
    else:
        try:
            auth_size = struct.unpack("<I", data[8:12])[0]
            auth_data = data[12:12+auth_size]
            
            print("[*] Extracting certificate and public key from metadata...")
            metadata = plistlib.loads(auth_data)
            if 'SigningCertificateChain' not in metadata:
                print("[-] No SigningCertificateChain found in metadata.")
                return
                
            cert_data = metadata['SigningCertificateChain'][0]
            cert = cryptography.x509.load_der_x509_certificate(cert_data, default_backend())
            pem_bytes = cert.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            print("[*] Decrypting and decompressing AEA payload...")
            decoded_payload = aea.decode(data, signature_pub=pem_bytes)
            
            if decoded_payload.startswith(b"AA01"):
                print("[*] Inner payload is an Apple Archive (AA01). Extracting bplist...")
                bplist_idx = decoded_payload.find(b"bplist00")
                if bplist_idx == -1:
                    print("[-] Could not find bplist00 inside the Apple Archive.")
                    return
                final_bplist_data = decoded_payload[bplist_idx:]
            else:
                final_bplist_data = decoded_payload
                
            print("[*] Parsing shortcut logic...")
            shortcut_dict = plistlib.loads(final_bplist_data)
        except Exception as e:
            print(f"[-] Error decoding shortcut: {e}")
            import traceback
            traceback.print_exc()
            return

    if shortcut_dict:
        try:
            with open(out_path, 'w', encoding='utf-8') as f_out:
                json.dump(shortcut_dict, f_out, cls=CustomEncoder, indent=2, ensure_ascii=False)
            print(f"[+] Successfully saved full JSON to {out_path}")
            
            extract_logic_to_txt(shortcut_dict, txt_path)
            print(f"[+] Successfully saved readable logic to {txt_path}")
        except Exception as e:
            print(f"[-] Error saving output files: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Kéo thả file .shortcut vào tool (hoặc chạy từ CMD: iOSShortcutDecoder.exe <file.shortcut>)")
    else:
        # Lấy file đầu tiên từ argv (hỗ trợ kéo thả)
        file_path = sys.argv[1]
        decode_shortcut(file_path)
    
    print("\n")
    input("Nhan Enter de thoat...")
