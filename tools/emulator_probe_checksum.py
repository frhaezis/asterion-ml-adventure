from pathlib import Path
from zipfile import ZipFile
import struct, argparse, hashlib
parser=argparse.ArgumentParser(description='Generate an independent checksum probe from the unmodified Android API35 WebView124 APK. The SDK binary is supplied by the developer, not bundled in this project.')
parser.add_argument('--webview-apk',required=True,type=Path)
parser.add_argument('--output-c',required=True,type=Path)
args=parser.parse_args()
with ZipFile(args.webview_apk) as archive:
 lib=archive.read('lib/x86_64/libwebviewchromium.so')
 blob=archive.read('assets/snapshot_blob_64.bin')
if hashlib.sha256(lib).hexdigest()!='e154b524119b6670b824d3e11a1794bf32e4a497aef18ed5d76fbe6e01d4eded':
 raise SystemExit('Unsupported WebView binary; refusing to use offsets from another build.')
if hashlib.sha256(blob).hexdigest()!='f10aada9cfd5446cb0036ecb879f7262189e0ddeadaaeef33e1b236d49da6d48':
 raise SystemExit('Unexpected snapshot; source APK must be the unmodified API35 system image.')
start=0x1797790
code=bytearray(lib[start:0x1797998])
for disp,end,source in [(0x17977ba,0x17977be,0xcff770),(0x17977c3,0x17977c7,0xcfb3b0),(0x17977cb,0x17977cf,0xd029b0)]:
 while len(code)%16:code.append(0)
 offset=len(code);code.extend(lib[source:source+16]);struct.pack_into('<i',code,disp-start,offset-(end-start))
def arr(name,value):return 'static const unsigned char '+name+'[] = {'+','.join(str(x) for x in value)+'};\n'
s='''#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
'''+arr('code',code)+arr('blob',blob)+'''
uint32_t scalar(const unsigned char* p, size_t n) {
 uint32_t a=0,b=0;
 for(size_t i=0;i<n;i++){a=(a+p[i])%65521;b=(b+a)%65521;}
 return (b<<16)|a;
}
int main(){
 uint32_t expected;memcpy(&expected,blob+8,4);
 void* fn=mmap(NULL,4096,PROT_READ|PROT_WRITE|PROT_EXEC,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
 if(fn==MAP_FAILED){perror("mmap");return 2;}
 memcpy(fn,code,sizeof(code));
 uint32_t (*simd)(uint32_t,const unsigned char*,size_t)=fn;
 uint32_t plain=scalar(blob+12,sizeof(blob)-12);
 uint32_t optimized=simd(0,blob+12,sizeof(blob)-12);
 printf("V8 snapshot bytes=%zu expected=%08x scalar=%08x exactChromiumSIMD=%08x\\n",sizeof(blob),expected,plain,optimized);
 return expected!=plain || expected!=optimized;
}
'''
args.output_c.write_text(s)
