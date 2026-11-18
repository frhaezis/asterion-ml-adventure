#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <tmmintrin.h>
#include <smmintrin.h>
static void dump(const char* name,__m128i v){uint32_t x[4];_mm_storeu_si128((__m128i*)x,v);printf("%s %08x %08x %08x %08x\n",name,x[0],x[1],x[2],x[3]);}
int main(){
 __m128i a=_mm_set_epi32(4,3,2,1),b=_mm_set_epi32(40,30,20,10);
 __m128i self=a;
 __asm__ volatile("phaddd %0, %0":"+x"(self));
 dump("PHADDD_SELF",self);
 dump("PHADDD_SEPARATE",_mm_hadd_epi32(a,b));
 __m128i m=_mm_set1_epi8((char)255),n=_mm_set1_epi8(1);
 dump("PMADDUBSW_255x1",_mm_maddubs_epi16(m,n));
 dump("PMADDUBSW_1x255",_mm_maddubs_epi16(n,m));
 dump("PMOVSXBW",_mm_cvtepi8_epi16(_mm_set_epi8(0,0,0,0,0,0,0,0,127,-128,-2,-1,4,3,2,1)));
 dump("PMADDWD",_mm_madd_epi16(_mm_set1_epi16(100),_mm_set1_epi16(-2)));
 dump("PSADBW",_mm_sad_epu8(m,_mm_setzero_si128()));
 dump("PADDD",_mm_add_epi32(a,b));
 dump("PSHUFD_FF",_mm_shuffle_epi32(a,255));
 return 0;
}
