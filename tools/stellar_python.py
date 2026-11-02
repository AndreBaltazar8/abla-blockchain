#!/usr/bin/env python3
"""Plain RFC 8032 Ed25519 and Stellar's XDR in Python, to check this library against: tools/sign_vectors.py. Not used otherwise, and the network parts here are left over."""
import base64,hashlib,json,os,struct,urllib.parse,urllib.request,urllib.error
from pathlib import Path
HORIZON='https://horizon-testnet.stellar.org'
FILE=Path.home()/'.config/crypto-gateway-test/stellar.json'
NETWORK=hashlib.sha256(b'Test SDF Network ; September 2015').digest()
p=2**255-19;q=2**252+27742317777372353535851937790883648493
d=-121665*pow(121666,-1,p)%p;I=pow(2,(p-1)//4,p)
def _x(y,sign=0):
    xx=(y*y-1)*pow(d*y*y+1,-1,p)%p;x=pow(xx,(p+3)//8,p)
    if (x*x-xx)%p:x=x*I%p
    if x%2!=sign:x=p-x
    return x
B=(_x(4*pow(5,-1,p)%p),4*pow(5,-1,p)%p,1,_x(4*pow(5,-1,p)%p)*(4*pow(5,-1,p)%p)%p)
def _add(P,Q):
    A=(P[1]-P[0])*(Q[1]-Q[0])%p;B_=(P[1]+P[0])*(Q[1]+Q[0])%p;C=2*P[3]*Q[3]*d%p;D=2*P[2]*Q[2]%p;E=B_-A;F=D-C;G=D+C;H=B_+A
    return (E*F%p,G*H%p,F*G%p,E*H%p)
def _mul(s,P):
    Q=(0,1,1,0)
    while s:
        if s&1:Q=_add(Q,P)
        P=_add(P,P);s>>=1
    return Q
def _enc(P):
    zi=pow(P[2],-1,p);x=P[0]*zi%p;y=P[1]*zi%p
    return (y|((x&1)<<255)).to_bytes(32,'little')
def public(seed):
    h=hashlib.sha512(seed).digest();a=int.from_bytes(h[:32],'little')&(2**254-8)|2**254
    return _enc(_mul(a,B))
def sign(seed,msg):
    h=hashlib.sha512(seed).digest();a=int.from_bytes(h[:32],'little')&(2**254-8)|2**254;A=_enc(_mul(a,B))
    r=int.from_bytes(hashlib.sha512(h[32:]+msg).digest(),'little')%q;R=_enc(_mul(r,B))
    k=int.from_bytes(hashlib.sha512(R+A+msg).digest(),'little')%q
    return R+((r+k*a)%q).to_bytes(32,'little')
def _crc(b):
    c=0
    for x in b:
        c^=x<<8
        for _ in range(8):c=((c<<1)^0x1021)&0xffff if c&0x8000 else (c<<1)&0xffff
    return c
def strkey(version,payload):
    b=bytes([version])+payload;return base64.b32encode(b+struct.pack('<H',_crc(b))).decode().rstrip('=')
def address(seed):return strkey(48,public(seed))
def _u32(n):return struct.pack('>I',n)
def _i64(n):return struct.pack('>q',n)
def _account(pub):return _u32(0)+pub
def _pub(g):return base64.b32decode(g+'='*(-len(g)%8))[1:33]
def _asset(a):
    if a is None:return _u32(0)
    code,issuer=a;return _u32(1)+code.encode().ljust(4,b'\0')+_u32(0)+_pub(issuer)
def op_payment(to,amount,asset=None):return _u32(0)+_u32(1)+_account(_pub(to))+_asset(asset)+_i64(amount)
def op_create_account(to,amount):return _u32(0)+_u32(0)+_u32(0)+_pub(to)+_i64(amount)
def op_trust(asset):return _u32(0)+_u32(6)+_asset(asset)+_i64(2**63-1)
def _get(path):
    with urllib.request.urlopen(urllib.request.Request(HORIZON+path,headers={'User-Agent':'crypto-gateway-test'}),timeout=30) as r:return json.load(r)
def submit(seed,ops,memo=None):
    pub=public(seed);g=address(seed);seq=int(_get('/accounts/'+g)['sequence'])+1
    m=_u32(0) if memo is None else _u32(1)+_u32(len(memo))+memo.encode().ljust((len(memo)+3)//4*4,b'\0')
    tx=_account(pub)+_u32(100*len(ops))+_i64(seq)+_u32(0)+m+_u32(len(ops))+b''.join(ops)+_u32(0)
    sig=sign(seed,hashlib.sha256(NETWORK+_u32(2)+tx).digest())
    env=_u32(2)+tx+_u32(1)+pub[-4:]+_u32(64)+sig
    data=urllib.parse.urlencode({'tx':base64.b64encode(env).decode()}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(HORIZON+'/transactions',data=data,headers={'User-Agent':'crypto-gateway-test'}),timeout=60) as r:return json.load(r)
    except urllib.error.HTTPError as e:raise AssertionError(f"Stellar refused it: {e.read()[:500]!r}")
def wallets():
    """payer, merchant and an issuer of a test token: made and funded once, then kept."""
    if FILE.exists():
        assert FILE.stat().st_mode&0o077==0,f'{FILE} has to be 0600'
        seeds={k:bytes.fromhex(v) for k,v in json.loads(FILE.read_text()).items()}
    else:
        FILE.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        seeds={k:os.urandom(32) for k in ('payer','merchant','issuer')}
        fd=os.open(FILE,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f:json.dump({k:v.hex() for k,v in seeds.items()},f)
    for seed in seeds.values():
        g=address(seed)
        try:_get('/accounts/'+g)
        except urllib.error.HTTPError as e:
            if e.code!=404:raise
            with urllib.request.urlopen(urllib.request.Request(f'https://friendbot.stellar.org/?addr={g}',headers={'User-Agent':'crypto-gateway-test'}),timeout=60) as r:r.read()
    return seeds
