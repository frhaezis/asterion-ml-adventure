#!/usr/bin/env python3
"""Host-only comparison of exact stock emulator helpers against scalar ISA models."""
import argparse,ctypes,hashlib,json,mmap,random,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from emulator_fix_tcg import find_helper,ALLOWLIST
SPECS={'phaddw':(0x60,0x01),'phaddd':(0x20,0x02),'phaddsw':(0xc0,0x03),
       'phsubw':(0x60,0x05),'phsubd':(0x20,0x06),'phsubsw':(0xc0,0x07),
       'pshufb':(0x2a0,0x00),'palignr':(0x190,None)}
A=ctypes.c_ubyte*16
keep=[]
def code_function(code):
 m=mmap.mmap(-1,len(code),prot=mmap.PROT_READ|mmap.PROT_WRITE|mmap.PROT_EXEC);m.write(code);keep.append(m)
 return ctypes.CFUNCTYPE(None,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint32)(ctypes.addressof(ctypes.c_char.from_buffer(m)))
def call(fn,a,b,alias,count):
 aa,bb=A.from_buffer_copy(a),A.from_buffer_copy(b);fn(None,aa,aa if alias else bb,count);return bytes(aa)
def ref(name,a,b,count=0):
 if name=='pshufb':return bytes(0 if k&128 else a[k&15]for k in b)
 if name=='palignr':return ((b+a)+bytes(256))[count:count+16]
 bits=32 if name.endswith('d') else 16;signed=name.endswith('sw');fmt='<'+('i'if bits==32 else 'h')*(128//bits)
 av,bv=struct.unpack(fmt,a),struct.unpack(fmt,b);out=[]
 for vv in [av,bv]:
  for i in range(0,len(vv),2):
   value=vv[i]+vv[i+1]if name.startswith('phadd')else vv[i]-vv[i+1]
   if signed:value=max(-32768,min(32767,value))
   out.append(value&((1<<bits)-1))
 return struct.pack('<'+('I'if bits==32 else'H')*len(out),*out)
def run(source,report,n,expected_hash=None):
 d=source.read_bytes();assert hashlib.sha256(d).hexdigest()==(expected_hash or ALLOWLIST[source.name])
 rng=random.Random(0x73696d64);records=[]
 for name,(length,opcode)in SPECS.items():
  va,off=find_helper(d,name+'_xmm');original=d[off:off+length];old=code_function(original)
  native=None if opcode is None else bytes.fromhex('f30f6f06f30f6f0a660f38')+bytes([opcode,0xc1])+bytes.fromhex('f30f7f06c3')
  new=code_function(native)if native else None
  failures={False:0,True:0};examples={};total=0
  if name=='palignr':
   cases=((rng.randbytes(16),rng.randbytes(16),count,alias)for alias in[False,True]for count in range(256)for _ in range(256))
  else:
   edge=[bytes(16),b'\xff'*16,bytes(range(16)),bytes(reversed(range(16))),bytes.fromhex('ffff010000800080ff7f010078563412')]
   cases=[(a,b,0,alias)for alias in[False,True]for a in edge for b in edge]
   cases+= [(rng.randbytes(16),rng.randbytes(16),0,alias)for alias in[False,True]for _ in range(n)]
  for a,b,count,alias in cases:
   if alias:b=a
   expected=ref(name,a,b,count);got=call(old,a,b,alias,count)
   if got!=expected:
    failures[alias]+=1
    examples.setdefault(str(alias),{'a':a.hex(),'b':b.hex(),'count':count,'expected':expected.hex(),'actual':got.hex()})
   if new is not None:assert call(new,a,b,alias,count)==expected,(name,a.hex(),b.hex(),alias)
   total+=1
  record={'helper':name+'_xmm','virtual_address':hex(va),'file_offset':hex(off),'function_bytes':length,'original_function_sha256':hashlib.sha256(original).hexdigest(),'cases':total,'failures_distinct':failures[False],'failures_alias':failures[True],'first_failures':examples,'native_replacement_passes_all_cases':new is not None,'before_first_32_hex':original[:32].hex(),'native_replacement_hex':native.hex()if native else None}
  records.append(record);print(json.dumps(record),flush=True)
 report.write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(d).hexdigest(),'records':records},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--cases-per-mode',type=int,default=100000);p.add_argument('--expected-sha256');args=p.parse_args();run(args.source,args.report,args.cases_per_mode,args.expected_sha256)
