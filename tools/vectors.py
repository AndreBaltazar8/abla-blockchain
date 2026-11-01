#!/usr/bin/env python3
"""An independent BIP32 in plain Python, private derivation included, for making test vectors from the public Hardhat
mnemonic. It's only for tests, and nothing like it exists in the service."""
import hashlib,hmac
P=2**256-2**32-977;N=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
G=(0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)
def add(a,b):
    if a is None:return b
    if b is None:return a
    if a[0]==b[0] and (a[1]+b[1])%P==0:return None
    l=(3*a[0]*a[0]*pow(2*a[1],-1,P) if a==b else (b[1]-a[1])*pow(b[0]-a[0],-1,P))%P
    x=(l*l-a[0]-b[0])%P;return (x,(l*(a[0]-x)-a[1])%P)
def mul(k,p=G):
    r=None
    while k:
        if k&1:r=add(r,p)
        p=add(p,p);k>>=1
    return r
def comp(p):return bytes([2+(p[1]&1)])+p[0].to_bytes(32,'big')
A='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58c(b):
    b+=hashlib.sha256(hashlib.sha256(b).digest()).digest()[:4];n=int.from_bytes(b,'big');s=''
    while n:n,r=divmod(n,58);s=A[r]+s
    return '1'*(len(b)-len(b.lstrip(b'\0')))+s
def h160(b):return hashlib.new('ripemd160',hashlib.sha256(b).digest()).digest()
def ckd(k,c,i):
    d=(k.to_bytes(32,'big') if i>=2**31 else comp(mul(k)))
    I=hmac.new(c,(b'\0'+d if i>=2**31 else d)+i.to_bytes(4,'big'),hashlib.sha512).digest()
    return (int.from_bytes(I[:32],'big')+k)%N,I[32:]
def derive(seed,ps):
    I=hmac.new(b'Bitcoin seed',seed,hashlib.sha512).digest();k=int.from_bytes(I[:32],'big');c=I[32:];pf=b'\0'*4;d=0;i=0
    for i in ps:
        pf=h160(comp(mul(k)))[:4];k,c=ckd(k,c,i);d+=1
    return k,c,d,pf,i
def xpub(seed,ps,ver):
    k,c,d,pf,i=derive(seed,ps)
    return b58c(ver.to_bytes(4,'big')+bytes([d])+pf+i.to_bytes(4,'big')+c+comp(mul(k)))
CS='qpzry9x8gf2tvdw0s3jn54khce6mua7l'
def pm(v):
    g=[0x3b6a57b2,0x26508e6d,0x1ea119fa,0x3d4233dd,0x2a1462b3];c=1
    for x in v:
        t=c>>25;c=(c&0x1ffffff)<<5^x
        for i in range(5):c^=g[i] if (t>>i)&1 else 0
    return c
def bech32(hrp,h):
    d=[0];acc=0;b=0
    for x in h:
        acc=acc<<8|x;b+=8
        while b>=5:b-=5;d.append(acc>>b&31)
        acc&=(1<<b)-1
    if b:d.append(acc<<(5-b)&31)
    e=[ord(x)>>5 for x in hrp]+[0]+[ord(x)&31 for x in hrp]+d
    m=pm(e+[0]*6)^1
    return hrp+'1'+''.join(CS[x] for x in d+[(m>>5*(5-i))&31 for i in range(6)])
def desc_checksum(s):
    ic="0123456789()[],'/*abcdefgh@:$%{}IJKLMNOPQRSTUVWXYZ&+-.;<=>?!^_|~ijklmnopqrstuvwxyzABCDEFGH`#\"\\ "
    g=[0xF5DEE51989,0xA9FDCA3312,0x1BAB10E32D,0x3706B1677A,0x644D626FFD]
    def st(c,v):
        t=c>>35;c=(c&0x7ffffffff)<<5^v
        for i in range(5):c^=g[i] if (t>>i)&1 else 0
        return c
    c=1;cls=0;n=0
    for ch in s:
        p=ic.find(ch);c=st(c,p&31);cls=cls*3+(p>>5);n+=1
        if n==3:c=st(c,cls);cls=0;n=0
    if n:c=st(c,cls)
    for _ in range(8):c=st(c,0)
    c^=1
    return ''.join(CS[(c>>(5*(7-i)))&31] for i in range(8))
H=2**31
HARDHAT=hashlib.pbkdf2_hmac('sha512',b'test test test test test test test test test test test junk',b'mnemonic',2048)
def child_key(seed,ps):return derive(seed,ps)[0]
if __name__=='__main__':
    s=HARDHAT
    tpub84=xpub(s,[84+H,1+H,H],0x043587CF)
    print('VECTOR_WPKH_0',bech32('tb',h160(comp(mul(child_key(s,[84+H,1+H,H,0,0]))))))
    print('VECTOR_WPKH_5',bech32('tb',h160(comp(mul(child_key(s,[84+H,1+H,H,0,5]))))))
    print('VECTOR_WPKH_CHANGE_0',bech32('tb',h160(comp(mul(child_key(s,[84+H,1+H,H,1,0]))))))
    print('VECTOR_TPUB44',xpub(s,[44+H,1+H,H],0x043587CF))
    print('VECTOR_PKH_0',b58c(bytes([111])+h160(comp(mul(child_key(s,[44+H,1+H,H,0,0]))))))
    print('VECTOR_TPUB49',xpub(s,[49+H,1+H,H],0x043587CF))
    r=b'\0\x14'+h160(comp(mul(child_key(s,[49+H,1+H,H,0,0]))))
    print('VECTOR_SH_0',b58c(bytes([196])+h160(r)))
    print('VECTOR_CHECKSUM',desc_checksum(f'wpkh([d34db33f/84h/1h/0h]{tpub84}/0/*)'))
