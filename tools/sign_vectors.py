#!/usr/bin/env python3
"""Vectors for tests/wallet_test.ab from tools that aren't this library. Run by hand, and the result is committed.
   uv run --no-project --python python3 --with eth-account==0.13.7 tools/sign_vectors.py BIP32_MEDIAWIKI MNEMONIC_VECTORS_JSON STELLAR_WALLET_DIR"""
import hashlib,json,re,sys
from eth_account import Account
from eth_keys import keys
sys.path.insert(0,sys.argv[3])
import stellar_wallet as ed
out={}
# BIP-32's own text: seeds and, for each chain, the extended private and public keys.
text=open(sys.argv[1]).read();vectors=[]
for block in re.split(r'===Test vector \d+===',text)[1:]:
    found=re.search(r'Seed \(hex\): ([0-9a-f]+)',block);chains=[]
    if not found:continue
    seed=found.group(1)
    for path,pub,prv in re.findall(r'\* Chain (m[^\n]*?)\n\*\* ext pub: (\w+)\n\*\* ext prv: (\w+)',block):chains.append(dict(path=path.replace('<sub>H</sub>',"'").strip(),xpub=pub,xprv=prv))
    vectors.append(dict(seed=seed,chains=chains))
out['bip32']=vectors
out['bip39']=[dict(entropy=e,mnemonic=m,seed=s,xprv=x) for e,m,s,x in json.load(open(sys.argv[2]))['english']]
# ECDSA, as eth_keys does it: RFC 6979 and low s, from keys and digests made here by hashing a counter.
out['ecdsa']=[]
for i in range(40):
    key=hashlib.sha256(b'ecdsa key %d'%i).digest();digest=hashlib.sha256(b'ecdsa message %d'%i).digest();s=keys.PrivateKey(key).sign_msg_hash(digest)
    out['ecdsa'].append(dict(key=key.hex(),digest=digest.hex(),r=format(s.r,'064x'),s=format(s.s,'064x'),odd=s.v==1,public=keys.PrivateKey(key).public_key.to_compressed_bytes().hex()))
# EIP-1559, as eth-account signs it.
out['evm']=[]
for i,(to,value,data) in enumerate([('0x3535353535353535353535353535353535353535',10**18,'0x'),('0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',0,'0xa9059cbb'+'35'*12+'35'*20+format(1250000,'064x')),(None,0,'0x6010'),('0x0000000000000000000000000000000000000001',1,'0x00ff')]):
    key=hashlib.sha256(b'evm key %d'%i).digest();t=dict(chainId=11155111,type=2,nonce=i*300,value=value,data=data,gas=21000+i*100000,maxFeePerGas=2*10**9+i,maxPriorityFeePerGas=10**9)
    if to:t['to']=to
    signed=Account.from_key(key).sign_transaction(t)
    out['evm'].append(dict(key=key.hex(),address=Account.from_key(key).address,chain=11155111,nonce=t['nonce'],value=str(value),data=data,gas=t['gas'],maxFee=str(t['maxFeePerGas']),tip=str(t['maxPriorityFeePerGas']),to=to or '',raw='0x'+signed.raw_transaction.hex().removeprefix('0x'),hash='0x'+signed.hash.hex().removeprefix('0x')))
# Ed25519 and Stellar's envelopes, by the plain RFC 8032 test tool in Python.
out['ed25519']=[];out['stellar']=[]
import base64
for i in range(10):
    seed=hashlib.sha256(b'ed key %d'%i).digest();m=hashlib.sha512(b'ed message %d'%i).digest()[:i*6]
    out['ed25519'].append(dict(seed=seed.hex(),message=m.hex(),public=ed.public(seed).hex(),signature=ed.sign(seed,m).hex()))
class Done(Exception):pass
seed=hashlib.sha256(b'stellar key').digest();other=hashlib.sha256(b'stellar other').digest();to=ed.address(other);issuer=ed.address(hashlib.sha256(b'stellar issuer').digest())
for name,ops,memo,model in [('pay',[ed.op_payment(to,12345678)],'memo1',[dict(kind='payment',destination=to,asset='native',amount=12345678)]),('asset',[ed.op_trust(('CGT',issuer)),ed.op_payment(to,5,('OTH',issuer))],None,[dict(kind='change_trust',destination='',asset='CGT:'+issuer,amount=2**63-1),dict(kind='payment',destination=to,asset='OTH:'+issuer,amount=5)]),('create',[ed.op_create_account(to,10**8)],'a memo of twenty-eight bytes',[dict(kind='create_account',destination=to,asset='native',amount=10**8)])]:
    pub=ed.public(seed);m=ed._u32(0) if memo is None else ed._u32(1)+ed._u32(len(memo))+memo.encode().ljust((len(memo)+3)//4*4,b'\0')
    tx=ed._account(pub)+ed._u32(100*len(ops))+ed._i64(777)+ed._u32(0)+m+ed._u32(len(ops))+b''.join(ops)+ed._u32(0);h=hashlib.sha256(ed.NETWORK+ed._u32(2)+tx).digest()
    out['stellar'].append(dict(seed=seed.hex(),sequence=777,memo=memo or '',operations=model,envelope=base64.b64encode(ed._u32(2)+tx+ed._u32(1)+pub[-4:]+ed._u32(64)+ed.sign(seed,h)).decode(),hash=h.hex()))
print(json.dumps(out,indent=0))
