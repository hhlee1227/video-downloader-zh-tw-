from pathlib import Path
import plistlib,struct,json,hashlib
import aea
from cryptography import x509
from cryptography.hazmat.primitives import serialization
import argparse
parser=argparse.ArgumentParser(description='Verify AEA using embedded leaf key and decode workflow; does not establish Apple certificate trust.')
parser.add_argument('input',nargs='?',default='original/Snap-Video-2026-10.shortcut')
parser.add_argument('--output-dir',default='original')
args=parser.parse_args();out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
p=Path(args.input); d=p.read_bytes()
n=struct.unpack_from('<I',d,8)[0]; auth=d[12:12+n]
(out/'auth.plist').write_bytes(auth)
c=x509.load_der_x509_certificate(plistlib.loads(auth)['SigningCertificateChain'][0])
k=c.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo)
a=aea.decode(d,signature_pub=k); (out/'payload.aar').write_bytes(a)
# This supplied archive has one directory entry and one Shortcut.wflow entry.
# Bound the plist by the AA DATA size instead of blindly scanning to EOF.
pos=0;payloads=[]
while pos<len(a):
 assert a[pos:pos+4]==b'AA01','unsupported Apple Archive record'
 size=struct.unpack_from('<H',a,pos+4)[0];header=a[pos:pos+size]
 assert len(header)==size and size>=6
 if b'TYP1F' in header:
  assert b'Shortcut.wflow' in header and header[-6:-2]==b'DATA','unsupported file header'
  length=int.from_bytes(header[-2:],'little');start=pos+size
  assert start+length<=len(a);payloads.append(a[start:start+length]);pos=start+length
 else:
  assert b'TYP1D' in header,'unexpected record type';pos+=size
assert len(payloads)==1
b=payloads[0]; w=plistlib.loads(b)
(out/'workflow.bplist').write_bytes(b)
(out/'workflow.plist').write_bytes(plistlib.dumps(w))
(out/'workflow.json').write_text(json.dumps(w,ensure_ascii=False,indent=2,default=lambda x:{'base64':__import__('base64').b64encode(x).decode()}),encoding='utf8')
(out/'signature-check.json').write_text(json.dumps({'sha256':hashlib.sha256(d).hexdigest(),'profile':int.from_bytes(d[4:7],'little'),'embedded_key_signature':'PASS','AEA_MAC_checksums':'PASS','Apple_trust_chain':'NOT VALIDATED','subject':c.subject.rfc4514_string(),'issuer':c.issuer.rfc4514_string(),'not_before':str(c.not_valid_before_utc),'not_after':str(c.not_valid_after_utc)},indent=2),encoding='utf8')
print('actions',len(w['WFWorkflowActions']))
