#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t v16 __attribute__((vector_size(16)));
static uint32_t seed=0x73696d64;
static uint32_t next(void){seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;return seed;}
static v16 phaddw(v16 a,v16 b,int alias){if(alias)__asm__ volatile("phaddw %0,%0":"+x"(a));else __asm__ volatile("phaddw %1,%0":"+x"(a):"x"(b));return a;}
static v16 phaddd(v16 a,v16 b,int alias){if(alias)__asm__ volatile("phaddd %0,%0":"+x"(a));else __asm__ volatile("phaddd %1,%0":"+x"(a):"x"(b));return a;}
static v16 phaddsw(v16 a,v16 b,int alias){if(alias)__asm__ volatile("phaddsw %0,%0":"+x"(a));else __asm__ volatile("phaddsw %1,%0":"+x"(a):"x"(b));return a;}
static v16 phsubw(v16 a,v16 b,int alias){if(alias)__asm__ volatile("phsubw %0,%0":"+x"(a));else __asm__ volatile("phsubw %1,%0":"+x"(a):"x"(b));return a;}
static v16 phsubd(v16 a,v16 b,int alias){if(alias)__asm__ volatile("phsubd %0,%0":"+x"(a));else __asm__ volatile("phsubd %1,%0":"+x"(a):"x"(b));return a;}
static v16 phsubsw(v16 a,v16 b,int alias){if(alias)__asm__ volatile("phsubsw %0,%0":"+x"(a));else __asm__ volatile("phsubsw %1,%0":"+x"(a):"x"(b));return a;}
static v16 pshufb(v16 a,v16 b,int alias){if(alias)__asm__ volatile("pshufb %0,%0":"+x"(a));else __asm__ volatile("pshufb %1,%0":"+x"(a):"x"(b));return a;}
static v16 palignr(v16 a,v16 b,int alias,unsigned count){switch(count){
case 0:if(alias)__asm__ volatile("palignr $0,%0,%0":"+x"(a));else __asm__ volatile("palignr $0,%1,%0":"+x"(a):"x"(b));break;
case 1:if(alias)__asm__ volatile("palignr $1,%0,%0":"+x"(a));else __asm__ volatile("palignr $1,%1,%0":"+x"(a):"x"(b));break;
case 2:if(alias)__asm__ volatile("palignr $2,%0,%0":"+x"(a));else __asm__ volatile("palignr $2,%1,%0":"+x"(a):"x"(b));break;
case 3:if(alias)__asm__ volatile("palignr $3,%0,%0":"+x"(a));else __asm__ volatile("palignr $3,%1,%0":"+x"(a):"x"(b));break;
case 4:if(alias)__asm__ volatile("palignr $4,%0,%0":"+x"(a));else __asm__ volatile("palignr $4,%1,%0":"+x"(a):"x"(b));break;
case 5:if(alias)__asm__ volatile("palignr $5,%0,%0":"+x"(a));else __asm__ volatile("palignr $5,%1,%0":"+x"(a):"x"(b));break;
case 6:if(alias)__asm__ volatile("palignr $6,%0,%0":"+x"(a));else __asm__ volatile("palignr $6,%1,%0":"+x"(a):"x"(b));break;
case 7:if(alias)__asm__ volatile("palignr $7,%0,%0":"+x"(a));else __asm__ volatile("palignr $7,%1,%0":"+x"(a):"x"(b));break;
case 8:if(alias)__asm__ volatile("palignr $8,%0,%0":"+x"(a));else __asm__ volatile("palignr $8,%1,%0":"+x"(a):"x"(b));break;
case 9:if(alias)__asm__ volatile("palignr $9,%0,%0":"+x"(a));else __asm__ volatile("palignr $9,%1,%0":"+x"(a):"x"(b));break;
case 10:if(alias)__asm__ volatile("palignr $10,%0,%0":"+x"(a));else __asm__ volatile("palignr $10,%1,%0":"+x"(a):"x"(b));break;
case 11:if(alias)__asm__ volatile("palignr $11,%0,%0":"+x"(a));else __asm__ volatile("palignr $11,%1,%0":"+x"(a):"x"(b));break;
case 12:if(alias)__asm__ volatile("palignr $12,%0,%0":"+x"(a));else __asm__ volatile("palignr $12,%1,%0":"+x"(a):"x"(b));break;
case 13:if(alias)__asm__ volatile("palignr $13,%0,%0":"+x"(a));else __asm__ volatile("palignr $13,%1,%0":"+x"(a):"x"(b));break;
case 14:if(alias)__asm__ volatile("palignr $14,%0,%0":"+x"(a));else __asm__ volatile("palignr $14,%1,%0":"+x"(a):"x"(b));break;
case 15:if(alias)__asm__ volatile("palignr $15,%0,%0":"+x"(a));else __asm__ volatile("palignr $15,%1,%0":"+x"(a):"x"(b));break;
case 16:if(alias)__asm__ volatile("palignr $16,%0,%0":"+x"(a));else __asm__ volatile("palignr $16,%1,%0":"+x"(a):"x"(b));break;
case 17:if(alias)__asm__ volatile("palignr $17,%0,%0":"+x"(a));else __asm__ volatile("palignr $17,%1,%0":"+x"(a):"x"(b));break;
case 18:if(alias)__asm__ volatile("palignr $18,%0,%0":"+x"(a));else __asm__ volatile("palignr $18,%1,%0":"+x"(a):"x"(b));break;
case 19:if(alias)__asm__ volatile("palignr $19,%0,%0":"+x"(a));else __asm__ volatile("palignr $19,%1,%0":"+x"(a):"x"(b));break;
case 20:if(alias)__asm__ volatile("palignr $20,%0,%0":"+x"(a));else __asm__ volatile("palignr $20,%1,%0":"+x"(a):"x"(b));break;
case 21:if(alias)__asm__ volatile("palignr $21,%0,%0":"+x"(a));else __asm__ volatile("palignr $21,%1,%0":"+x"(a):"x"(b));break;
case 22:if(alias)__asm__ volatile("palignr $22,%0,%0":"+x"(a));else __asm__ volatile("palignr $22,%1,%0":"+x"(a):"x"(b));break;
case 23:if(alias)__asm__ volatile("palignr $23,%0,%0":"+x"(a));else __asm__ volatile("palignr $23,%1,%0":"+x"(a):"x"(b));break;
case 24:if(alias)__asm__ volatile("palignr $24,%0,%0":"+x"(a));else __asm__ volatile("palignr $24,%1,%0":"+x"(a):"x"(b));break;
case 25:if(alias)__asm__ volatile("palignr $25,%0,%0":"+x"(a));else __asm__ volatile("palignr $25,%1,%0":"+x"(a):"x"(b));break;
case 26:if(alias)__asm__ volatile("palignr $26,%0,%0":"+x"(a));else __asm__ volatile("palignr $26,%1,%0":"+x"(a):"x"(b));break;
case 27:if(alias)__asm__ volatile("palignr $27,%0,%0":"+x"(a));else __asm__ volatile("palignr $27,%1,%0":"+x"(a):"x"(b));break;
case 28:if(alias)__asm__ volatile("palignr $28,%0,%0":"+x"(a));else __asm__ volatile("palignr $28,%1,%0":"+x"(a):"x"(b));break;
case 29:if(alias)__asm__ volatile("palignr $29,%0,%0":"+x"(a));else __asm__ volatile("palignr $29,%1,%0":"+x"(a):"x"(b));break;
case 30:if(alias)__asm__ volatile("palignr $30,%0,%0":"+x"(a));else __asm__ volatile("palignr $30,%1,%0":"+x"(a):"x"(b));break;
case 31:if(alias)__asm__ volatile("palignr $31,%0,%0":"+x"(a));else __asm__ volatile("palignr $31,%1,%0":"+x"(a):"x"(b));break;
case 32:if(alias)__asm__ volatile("palignr $32,%0,%0":"+x"(a));else __asm__ volatile("palignr $32,%1,%0":"+x"(a):"x"(b));break;
case 33:if(alias)__asm__ volatile("palignr $33,%0,%0":"+x"(a));else __asm__ volatile("palignr $33,%1,%0":"+x"(a):"x"(b));break;
case 34:if(alias)__asm__ volatile("palignr $34,%0,%0":"+x"(a));else __asm__ volatile("palignr $34,%1,%0":"+x"(a):"x"(b));break;
case 35:if(alias)__asm__ volatile("palignr $35,%0,%0":"+x"(a));else __asm__ volatile("palignr $35,%1,%0":"+x"(a):"x"(b));break;
case 36:if(alias)__asm__ volatile("palignr $36,%0,%0":"+x"(a));else __asm__ volatile("palignr $36,%1,%0":"+x"(a):"x"(b));break;
case 37:if(alias)__asm__ volatile("palignr $37,%0,%0":"+x"(a));else __asm__ volatile("palignr $37,%1,%0":"+x"(a):"x"(b));break;
case 38:if(alias)__asm__ volatile("palignr $38,%0,%0":"+x"(a));else __asm__ volatile("palignr $38,%1,%0":"+x"(a):"x"(b));break;
case 39:if(alias)__asm__ volatile("palignr $39,%0,%0":"+x"(a));else __asm__ volatile("palignr $39,%1,%0":"+x"(a):"x"(b));break;
case 40:if(alias)__asm__ volatile("palignr $40,%0,%0":"+x"(a));else __asm__ volatile("palignr $40,%1,%0":"+x"(a):"x"(b));break;
case 41:if(alias)__asm__ volatile("palignr $41,%0,%0":"+x"(a));else __asm__ volatile("palignr $41,%1,%0":"+x"(a):"x"(b));break;
case 42:if(alias)__asm__ volatile("palignr $42,%0,%0":"+x"(a));else __asm__ volatile("palignr $42,%1,%0":"+x"(a):"x"(b));break;
case 43:if(alias)__asm__ volatile("palignr $43,%0,%0":"+x"(a));else __asm__ volatile("palignr $43,%1,%0":"+x"(a):"x"(b));break;
case 44:if(alias)__asm__ volatile("palignr $44,%0,%0":"+x"(a));else __asm__ volatile("palignr $44,%1,%0":"+x"(a):"x"(b));break;
case 45:if(alias)__asm__ volatile("palignr $45,%0,%0":"+x"(a));else __asm__ volatile("palignr $45,%1,%0":"+x"(a):"x"(b));break;
case 46:if(alias)__asm__ volatile("palignr $46,%0,%0":"+x"(a));else __asm__ volatile("palignr $46,%1,%0":"+x"(a):"x"(b));break;
case 47:if(alias)__asm__ volatile("palignr $47,%0,%0":"+x"(a));else __asm__ volatile("palignr $47,%1,%0":"+x"(a):"x"(b));break;
case 48:if(alias)__asm__ volatile("palignr $48,%0,%0":"+x"(a));else __asm__ volatile("palignr $48,%1,%0":"+x"(a):"x"(b));break;
case 49:if(alias)__asm__ volatile("palignr $49,%0,%0":"+x"(a));else __asm__ volatile("palignr $49,%1,%0":"+x"(a):"x"(b));break;
case 50:if(alias)__asm__ volatile("palignr $50,%0,%0":"+x"(a));else __asm__ volatile("palignr $50,%1,%0":"+x"(a):"x"(b));break;
case 51:if(alias)__asm__ volatile("palignr $51,%0,%0":"+x"(a));else __asm__ volatile("palignr $51,%1,%0":"+x"(a):"x"(b));break;
case 52:if(alias)__asm__ volatile("palignr $52,%0,%0":"+x"(a));else __asm__ volatile("palignr $52,%1,%0":"+x"(a):"x"(b));break;
case 53:if(alias)__asm__ volatile("palignr $53,%0,%0":"+x"(a));else __asm__ volatile("palignr $53,%1,%0":"+x"(a):"x"(b));break;
case 54:if(alias)__asm__ volatile("palignr $54,%0,%0":"+x"(a));else __asm__ volatile("palignr $54,%1,%0":"+x"(a):"x"(b));break;
case 55:if(alias)__asm__ volatile("palignr $55,%0,%0":"+x"(a));else __asm__ volatile("palignr $55,%1,%0":"+x"(a):"x"(b));break;
case 56:if(alias)__asm__ volatile("palignr $56,%0,%0":"+x"(a));else __asm__ volatile("palignr $56,%1,%0":"+x"(a):"x"(b));break;
case 57:if(alias)__asm__ volatile("palignr $57,%0,%0":"+x"(a));else __asm__ volatile("palignr $57,%1,%0":"+x"(a):"x"(b));break;
case 58:if(alias)__asm__ volatile("palignr $58,%0,%0":"+x"(a));else __asm__ volatile("palignr $58,%1,%0":"+x"(a):"x"(b));break;
case 59:if(alias)__asm__ volatile("palignr $59,%0,%0":"+x"(a));else __asm__ volatile("palignr $59,%1,%0":"+x"(a):"x"(b));break;
case 60:if(alias)__asm__ volatile("palignr $60,%0,%0":"+x"(a));else __asm__ volatile("palignr $60,%1,%0":"+x"(a):"x"(b));break;
case 61:if(alias)__asm__ volatile("palignr $61,%0,%0":"+x"(a));else __asm__ volatile("palignr $61,%1,%0":"+x"(a):"x"(b));break;
case 62:if(alias)__asm__ volatile("palignr $62,%0,%0":"+x"(a));else __asm__ volatile("palignr $62,%1,%0":"+x"(a):"x"(b));break;
case 63:if(alias)__asm__ volatile("palignr $63,%0,%0":"+x"(a));else __asm__ volatile("palignr $63,%1,%0":"+x"(a):"x"(b));break;
case 64:if(alias)__asm__ volatile("palignr $64,%0,%0":"+x"(a));else __asm__ volatile("palignr $64,%1,%0":"+x"(a):"x"(b));break;
case 65:if(alias)__asm__ volatile("palignr $65,%0,%0":"+x"(a));else __asm__ volatile("palignr $65,%1,%0":"+x"(a):"x"(b));break;
case 66:if(alias)__asm__ volatile("palignr $66,%0,%0":"+x"(a));else __asm__ volatile("palignr $66,%1,%0":"+x"(a):"x"(b));break;
case 67:if(alias)__asm__ volatile("palignr $67,%0,%0":"+x"(a));else __asm__ volatile("palignr $67,%1,%0":"+x"(a):"x"(b));break;
case 68:if(alias)__asm__ volatile("palignr $68,%0,%0":"+x"(a));else __asm__ volatile("palignr $68,%1,%0":"+x"(a):"x"(b));break;
case 69:if(alias)__asm__ volatile("palignr $69,%0,%0":"+x"(a));else __asm__ volatile("palignr $69,%1,%0":"+x"(a):"x"(b));break;
case 70:if(alias)__asm__ volatile("palignr $70,%0,%0":"+x"(a));else __asm__ volatile("palignr $70,%1,%0":"+x"(a):"x"(b));break;
case 71:if(alias)__asm__ volatile("palignr $71,%0,%0":"+x"(a));else __asm__ volatile("palignr $71,%1,%0":"+x"(a):"x"(b));break;
case 72:if(alias)__asm__ volatile("palignr $72,%0,%0":"+x"(a));else __asm__ volatile("palignr $72,%1,%0":"+x"(a):"x"(b));break;
case 73:if(alias)__asm__ volatile("palignr $73,%0,%0":"+x"(a));else __asm__ volatile("palignr $73,%1,%0":"+x"(a):"x"(b));break;
case 74:if(alias)__asm__ volatile("palignr $74,%0,%0":"+x"(a));else __asm__ volatile("palignr $74,%1,%0":"+x"(a):"x"(b));break;
case 75:if(alias)__asm__ volatile("palignr $75,%0,%0":"+x"(a));else __asm__ volatile("palignr $75,%1,%0":"+x"(a):"x"(b));break;
case 76:if(alias)__asm__ volatile("palignr $76,%0,%0":"+x"(a));else __asm__ volatile("palignr $76,%1,%0":"+x"(a):"x"(b));break;
case 77:if(alias)__asm__ volatile("palignr $77,%0,%0":"+x"(a));else __asm__ volatile("palignr $77,%1,%0":"+x"(a):"x"(b));break;
case 78:if(alias)__asm__ volatile("palignr $78,%0,%0":"+x"(a));else __asm__ volatile("palignr $78,%1,%0":"+x"(a):"x"(b));break;
case 79:if(alias)__asm__ volatile("palignr $79,%0,%0":"+x"(a));else __asm__ volatile("palignr $79,%1,%0":"+x"(a):"x"(b));break;
case 80:if(alias)__asm__ volatile("palignr $80,%0,%0":"+x"(a));else __asm__ volatile("palignr $80,%1,%0":"+x"(a):"x"(b));break;
case 81:if(alias)__asm__ volatile("palignr $81,%0,%0":"+x"(a));else __asm__ volatile("palignr $81,%1,%0":"+x"(a):"x"(b));break;
case 82:if(alias)__asm__ volatile("palignr $82,%0,%0":"+x"(a));else __asm__ volatile("palignr $82,%1,%0":"+x"(a):"x"(b));break;
case 83:if(alias)__asm__ volatile("palignr $83,%0,%0":"+x"(a));else __asm__ volatile("palignr $83,%1,%0":"+x"(a):"x"(b));break;
case 84:if(alias)__asm__ volatile("palignr $84,%0,%0":"+x"(a));else __asm__ volatile("palignr $84,%1,%0":"+x"(a):"x"(b));break;
case 85:if(alias)__asm__ volatile("palignr $85,%0,%0":"+x"(a));else __asm__ volatile("palignr $85,%1,%0":"+x"(a):"x"(b));break;
case 86:if(alias)__asm__ volatile("palignr $86,%0,%0":"+x"(a));else __asm__ volatile("palignr $86,%1,%0":"+x"(a):"x"(b));break;
case 87:if(alias)__asm__ volatile("palignr $87,%0,%0":"+x"(a));else __asm__ volatile("palignr $87,%1,%0":"+x"(a):"x"(b));break;
case 88:if(alias)__asm__ volatile("palignr $88,%0,%0":"+x"(a));else __asm__ volatile("palignr $88,%1,%0":"+x"(a):"x"(b));break;
case 89:if(alias)__asm__ volatile("palignr $89,%0,%0":"+x"(a));else __asm__ volatile("palignr $89,%1,%0":"+x"(a):"x"(b));break;
case 90:if(alias)__asm__ volatile("palignr $90,%0,%0":"+x"(a));else __asm__ volatile("palignr $90,%1,%0":"+x"(a):"x"(b));break;
case 91:if(alias)__asm__ volatile("palignr $91,%0,%0":"+x"(a));else __asm__ volatile("palignr $91,%1,%0":"+x"(a):"x"(b));break;
case 92:if(alias)__asm__ volatile("palignr $92,%0,%0":"+x"(a));else __asm__ volatile("palignr $92,%1,%0":"+x"(a):"x"(b));break;
case 93:if(alias)__asm__ volatile("palignr $93,%0,%0":"+x"(a));else __asm__ volatile("palignr $93,%1,%0":"+x"(a):"x"(b));break;
case 94:if(alias)__asm__ volatile("palignr $94,%0,%0":"+x"(a));else __asm__ volatile("palignr $94,%1,%0":"+x"(a):"x"(b));break;
case 95:if(alias)__asm__ volatile("palignr $95,%0,%0":"+x"(a));else __asm__ volatile("palignr $95,%1,%0":"+x"(a):"x"(b));break;
case 96:if(alias)__asm__ volatile("palignr $96,%0,%0":"+x"(a));else __asm__ volatile("palignr $96,%1,%0":"+x"(a):"x"(b));break;
case 97:if(alias)__asm__ volatile("palignr $97,%0,%0":"+x"(a));else __asm__ volatile("palignr $97,%1,%0":"+x"(a):"x"(b));break;
case 98:if(alias)__asm__ volatile("palignr $98,%0,%0":"+x"(a));else __asm__ volatile("palignr $98,%1,%0":"+x"(a):"x"(b));break;
case 99:if(alias)__asm__ volatile("palignr $99,%0,%0":"+x"(a));else __asm__ volatile("palignr $99,%1,%0":"+x"(a):"x"(b));break;
case 100:if(alias)__asm__ volatile("palignr $100,%0,%0":"+x"(a));else __asm__ volatile("palignr $100,%1,%0":"+x"(a):"x"(b));break;
case 101:if(alias)__asm__ volatile("palignr $101,%0,%0":"+x"(a));else __asm__ volatile("palignr $101,%1,%0":"+x"(a):"x"(b));break;
case 102:if(alias)__asm__ volatile("palignr $102,%0,%0":"+x"(a));else __asm__ volatile("palignr $102,%1,%0":"+x"(a):"x"(b));break;
case 103:if(alias)__asm__ volatile("palignr $103,%0,%0":"+x"(a));else __asm__ volatile("palignr $103,%1,%0":"+x"(a):"x"(b));break;
case 104:if(alias)__asm__ volatile("palignr $104,%0,%0":"+x"(a));else __asm__ volatile("palignr $104,%1,%0":"+x"(a):"x"(b));break;
case 105:if(alias)__asm__ volatile("palignr $105,%0,%0":"+x"(a));else __asm__ volatile("palignr $105,%1,%0":"+x"(a):"x"(b));break;
case 106:if(alias)__asm__ volatile("palignr $106,%0,%0":"+x"(a));else __asm__ volatile("palignr $106,%1,%0":"+x"(a):"x"(b));break;
case 107:if(alias)__asm__ volatile("palignr $107,%0,%0":"+x"(a));else __asm__ volatile("palignr $107,%1,%0":"+x"(a):"x"(b));break;
case 108:if(alias)__asm__ volatile("palignr $108,%0,%0":"+x"(a));else __asm__ volatile("palignr $108,%1,%0":"+x"(a):"x"(b));break;
case 109:if(alias)__asm__ volatile("palignr $109,%0,%0":"+x"(a));else __asm__ volatile("palignr $109,%1,%0":"+x"(a):"x"(b));break;
case 110:if(alias)__asm__ volatile("palignr $110,%0,%0":"+x"(a));else __asm__ volatile("palignr $110,%1,%0":"+x"(a):"x"(b));break;
case 111:if(alias)__asm__ volatile("palignr $111,%0,%0":"+x"(a));else __asm__ volatile("palignr $111,%1,%0":"+x"(a):"x"(b));break;
case 112:if(alias)__asm__ volatile("palignr $112,%0,%0":"+x"(a));else __asm__ volatile("palignr $112,%1,%0":"+x"(a):"x"(b));break;
case 113:if(alias)__asm__ volatile("palignr $113,%0,%0":"+x"(a));else __asm__ volatile("palignr $113,%1,%0":"+x"(a):"x"(b));break;
case 114:if(alias)__asm__ volatile("palignr $114,%0,%0":"+x"(a));else __asm__ volatile("palignr $114,%1,%0":"+x"(a):"x"(b));break;
case 115:if(alias)__asm__ volatile("palignr $115,%0,%0":"+x"(a));else __asm__ volatile("palignr $115,%1,%0":"+x"(a):"x"(b));break;
case 116:if(alias)__asm__ volatile("palignr $116,%0,%0":"+x"(a));else __asm__ volatile("palignr $116,%1,%0":"+x"(a):"x"(b));break;
case 117:if(alias)__asm__ volatile("palignr $117,%0,%0":"+x"(a));else __asm__ volatile("palignr $117,%1,%0":"+x"(a):"x"(b));break;
case 118:if(alias)__asm__ volatile("palignr $118,%0,%0":"+x"(a));else __asm__ volatile("palignr $118,%1,%0":"+x"(a):"x"(b));break;
case 119:if(alias)__asm__ volatile("palignr $119,%0,%0":"+x"(a));else __asm__ volatile("palignr $119,%1,%0":"+x"(a):"x"(b));break;
case 120:if(alias)__asm__ volatile("palignr $120,%0,%0":"+x"(a));else __asm__ volatile("palignr $120,%1,%0":"+x"(a):"x"(b));break;
case 121:if(alias)__asm__ volatile("palignr $121,%0,%0":"+x"(a));else __asm__ volatile("palignr $121,%1,%0":"+x"(a):"x"(b));break;
case 122:if(alias)__asm__ volatile("palignr $122,%0,%0":"+x"(a));else __asm__ volatile("palignr $122,%1,%0":"+x"(a):"x"(b));break;
case 123:if(alias)__asm__ volatile("palignr $123,%0,%0":"+x"(a));else __asm__ volatile("palignr $123,%1,%0":"+x"(a):"x"(b));break;
case 124:if(alias)__asm__ volatile("palignr $124,%0,%0":"+x"(a));else __asm__ volatile("palignr $124,%1,%0":"+x"(a):"x"(b));break;
case 125:if(alias)__asm__ volatile("palignr $125,%0,%0":"+x"(a));else __asm__ volatile("palignr $125,%1,%0":"+x"(a):"x"(b));break;
case 126:if(alias)__asm__ volatile("palignr $126,%0,%0":"+x"(a));else __asm__ volatile("palignr $126,%1,%0":"+x"(a):"x"(b));break;
case 127:if(alias)__asm__ volatile("palignr $127,%0,%0":"+x"(a));else __asm__ volatile("palignr $127,%1,%0":"+x"(a):"x"(b));break;
case 128:if(alias)__asm__ volatile("palignr $128,%0,%0":"+x"(a));else __asm__ volatile("palignr $128,%1,%0":"+x"(a):"x"(b));break;
case 129:if(alias)__asm__ volatile("palignr $129,%0,%0":"+x"(a));else __asm__ volatile("palignr $129,%1,%0":"+x"(a):"x"(b));break;
case 130:if(alias)__asm__ volatile("palignr $130,%0,%0":"+x"(a));else __asm__ volatile("palignr $130,%1,%0":"+x"(a):"x"(b));break;
case 131:if(alias)__asm__ volatile("palignr $131,%0,%0":"+x"(a));else __asm__ volatile("palignr $131,%1,%0":"+x"(a):"x"(b));break;
case 132:if(alias)__asm__ volatile("palignr $132,%0,%0":"+x"(a));else __asm__ volatile("palignr $132,%1,%0":"+x"(a):"x"(b));break;
case 133:if(alias)__asm__ volatile("palignr $133,%0,%0":"+x"(a));else __asm__ volatile("palignr $133,%1,%0":"+x"(a):"x"(b));break;
case 134:if(alias)__asm__ volatile("palignr $134,%0,%0":"+x"(a));else __asm__ volatile("palignr $134,%1,%0":"+x"(a):"x"(b));break;
case 135:if(alias)__asm__ volatile("palignr $135,%0,%0":"+x"(a));else __asm__ volatile("palignr $135,%1,%0":"+x"(a):"x"(b));break;
case 136:if(alias)__asm__ volatile("palignr $136,%0,%0":"+x"(a));else __asm__ volatile("palignr $136,%1,%0":"+x"(a):"x"(b));break;
case 137:if(alias)__asm__ volatile("palignr $137,%0,%0":"+x"(a));else __asm__ volatile("palignr $137,%1,%0":"+x"(a):"x"(b));break;
case 138:if(alias)__asm__ volatile("palignr $138,%0,%0":"+x"(a));else __asm__ volatile("palignr $138,%1,%0":"+x"(a):"x"(b));break;
case 139:if(alias)__asm__ volatile("palignr $139,%0,%0":"+x"(a));else __asm__ volatile("palignr $139,%1,%0":"+x"(a):"x"(b));break;
case 140:if(alias)__asm__ volatile("palignr $140,%0,%0":"+x"(a));else __asm__ volatile("palignr $140,%1,%0":"+x"(a):"x"(b));break;
case 141:if(alias)__asm__ volatile("palignr $141,%0,%0":"+x"(a));else __asm__ volatile("palignr $141,%1,%0":"+x"(a):"x"(b));break;
case 142:if(alias)__asm__ volatile("palignr $142,%0,%0":"+x"(a));else __asm__ volatile("palignr $142,%1,%0":"+x"(a):"x"(b));break;
case 143:if(alias)__asm__ volatile("palignr $143,%0,%0":"+x"(a));else __asm__ volatile("palignr $143,%1,%0":"+x"(a):"x"(b));break;
case 144:if(alias)__asm__ volatile("palignr $144,%0,%0":"+x"(a));else __asm__ volatile("palignr $144,%1,%0":"+x"(a):"x"(b));break;
case 145:if(alias)__asm__ volatile("palignr $145,%0,%0":"+x"(a));else __asm__ volatile("palignr $145,%1,%0":"+x"(a):"x"(b));break;
case 146:if(alias)__asm__ volatile("palignr $146,%0,%0":"+x"(a));else __asm__ volatile("palignr $146,%1,%0":"+x"(a):"x"(b));break;
case 147:if(alias)__asm__ volatile("palignr $147,%0,%0":"+x"(a));else __asm__ volatile("palignr $147,%1,%0":"+x"(a):"x"(b));break;
case 148:if(alias)__asm__ volatile("palignr $148,%0,%0":"+x"(a));else __asm__ volatile("palignr $148,%1,%0":"+x"(a):"x"(b));break;
case 149:if(alias)__asm__ volatile("palignr $149,%0,%0":"+x"(a));else __asm__ volatile("palignr $149,%1,%0":"+x"(a):"x"(b));break;
case 150:if(alias)__asm__ volatile("palignr $150,%0,%0":"+x"(a));else __asm__ volatile("palignr $150,%1,%0":"+x"(a):"x"(b));break;
case 151:if(alias)__asm__ volatile("palignr $151,%0,%0":"+x"(a));else __asm__ volatile("palignr $151,%1,%0":"+x"(a):"x"(b));break;
case 152:if(alias)__asm__ volatile("palignr $152,%0,%0":"+x"(a));else __asm__ volatile("palignr $152,%1,%0":"+x"(a):"x"(b));break;
case 153:if(alias)__asm__ volatile("palignr $153,%0,%0":"+x"(a));else __asm__ volatile("palignr $153,%1,%0":"+x"(a):"x"(b));break;
case 154:if(alias)__asm__ volatile("palignr $154,%0,%0":"+x"(a));else __asm__ volatile("palignr $154,%1,%0":"+x"(a):"x"(b));break;
case 155:if(alias)__asm__ volatile("palignr $155,%0,%0":"+x"(a));else __asm__ volatile("palignr $155,%1,%0":"+x"(a):"x"(b));break;
case 156:if(alias)__asm__ volatile("palignr $156,%0,%0":"+x"(a));else __asm__ volatile("palignr $156,%1,%0":"+x"(a):"x"(b));break;
case 157:if(alias)__asm__ volatile("palignr $157,%0,%0":"+x"(a));else __asm__ volatile("palignr $157,%1,%0":"+x"(a):"x"(b));break;
case 158:if(alias)__asm__ volatile("palignr $158,%0,%0":"+x"(a));else __asm__ volatile("palignr $158,%1,%0":"+x"(a):"x"(b));break;
case 159:if(alias)__asm__ volatile("palignr $159,%0,%0":"+x"(a));else __asm__ volatile("palignr $159,%1,%0":"+x"(a):"x"(b));break;
case 160:if(alias)__asm__ volatile("palignr $160,%0,%0":"+x"(a));else __asm__ volatile("palignr $160,%1,%0":"+x"(a):"x"(b));break;
case 161:if(alias)__asm__ volatile("palignr $161,%0,%0":"+x"(a));else __asm__ volatile("palignr $161,%1,%0":"+x"(a):"x"(b));break;
case 162:if(alias)__asm__ volatile("palignr $162,%0,%0":"+x"(a));else __asm__ volatile("palignr $162,%1,%0":"+x"(a):"x"(b));break;
case 163:if(alias)__asm__ volatile("palignr $163,%0,%0":"+x"(a));else __asm__ volatile("palignr $163,%1,%0":"+x"(a):"x"(b));break;
case 164:if(alias)__asm__ volatile("palignr $164,%0,%0":"+x"(a));else __asm__ volatile("palignr $164,%1,%0":"+x"(a):"x"(b));break;
case 165:if(alias)__asm__ volatile("palignr $165,%0,%0":"+x"(a));else __asm__ volatile("palignr $165,%1,%0":"+x"(a):"x"(b));break;
case 166:if(alias)__asm__ volatile("palignr $166,%0,%0":"+x"(a));else __asm__ volatile("palignr $166,%1,%0":"+x"(a):"x"(b));break;
case 167:if(alias)__asm__ volatile("palignr $167,%0,%0":"+x"(a));else __asm__ volatile("palignr $167,%1,%0":"+x"(a):"x"(b));break;
case 168:if(alias)__asm__ volatile("palignr $168,%0,%0":"+x"(a));else __asm__ volatile("palignr $168,%1,%0":"+x"(a):"x"(b));break;
case 169:if(alias)__asm__ volatile("palignr $169,%0,%0":"+x"(a));else __asm__ volatile("palignr $169,%1,%0":"+x"(a):"x"(b));break;
case 170:if(alias)__asm__ volatile("palignr $170,%0,%0":"+x"(a));else __asm__ volatile("palignr $170,%1,%0":"+x"(a):"x"(b));break;
case 171:if(alias)__asm__ volatile("palignr $171,%0,%0":"+x"(a));else __asm__ volatile("palignr $171,%1,%0":"+x"(a):"x"(b));break;
case 172:if(alias)__asm__ volatile("palignr $172,%0,%0":"+x"(a));else __asm__ volatile("palignr $172,%1,%0":"+x"(a):"x"(b));break;
case 173:if(alias)__asm__ volatile("palignr $173,%0,%0":"+x"(a));else __asm__ volatile("palignr $173,%1,%0":"+x"(a):"x"(b));break;
case 174:if(alias)__asm__ volatile("palignr $174,%0,%0":"+x"(a));else __asm__ volatile("palignr $174,%1,%0":"+x"(a):"x"(b));break;
case 175:if(alias)__asm__ volatile("palignr $175,%0,%0":"+x"(a));else __asm__ volatile("palignr $175,%1,%0":"+x"(a):"x"(b));break;
case 176:if(alias)__asm__ volatile("palignr $176,%0,%0":"+x"(a));else __asm__ volatile("palignr $176,%1,%0":"+x"(a):"x"(b));break;
case 177:if(alias)__asm__ volatile("palignr $177,%0,%0":"+x"(a));else __asm__ volatile("palignr $177,%1,%0":"+x"(a):"x"(b));break;
case 178:if(alias)__asm__ volatile("palignr $178,%0,%0":"+x"(a));else __asm__ volatile("palignr $178,%1,%0":"+x"(a):"x"(b));break;
case 179:if(alias)__asm__ volatile("palignr $179,%0,%0":"+x"(a));else __asm__ volatile("palignr $179,%1,%0":"+x"(a):"x"(b));break;
case 180:if(alias)__asm__ volatile("palignr $180,%0,%0":"+x"(a));else __asm__ volatile("palignr $180,%1,%0":"+x"(a):"x"(b));break;
case 181:if(alias)__asm__ volatile("palignr $181,%0,%0":"+x"(a));else __asm__ volatile("palignr $181,%1,%0":"+x"(a):"x"(b));break;
case 182:if(alias)__asm__ volatile("palignr $182,%0,%0":"+x"(a));else __asm__ volatile("palignr $182,%1,%0":"+x"(a):"x"(b));break;
case 183:if(alias)__asm__ volatile("palignr $183,%0,%0":"+x"(a));else __asm__ volatile("palignr $183,%1,%0":"+x"(a):"x"(b));break;
case 184:if(alias)__asm__ volatile("palignr $184,%0,%0":"+x"(a));else __asm__ volatile("palignr $184,%1,%0":"+x"(a):"x"(b));break;
case 185:if(alias)__asm__ volatile("palignr $185,%0,%0":"+x"(a));else __asm__ volatile("palignr $185,%1,%0":"+x"(a):"x"(b));break;
case 186:if(alias)__asm__ volatile("palignr $186,%0,%0":"+x"(a));else __asm__ volatile("palignr $186,%1,%0":"+x"(a):"x"(b));break;
case 187:if(alias)__asm__ volatile("palignr $187,%0,%0":"+x"(a));else __asm__ volatile("palignr $187,%1,%0":"+x"(a):"x"(b));break;
case 188:if(alias)__asm__ volatile("palignr $188,%0,%0":"+x"(a));else __asm__ volatile("palignr $188,%1,%0":"+x"(a):"x"(b));break;
case 189:if(alias)__asm__ volatile("palignr $189,%0,%0":"+x"(a));else __asm__ volatile("palignr $189,%1,%0":"+x"(a):"x"(b));break;
case 190:if(alias)__asm__ volatile("palignr $190,%0,%0":"+x"(a));else __asm__ volatile("palignr $190,%1,%0":"+x"(a):"x"(b));break;
case 191:if(alias)__asm__ volatile("palignr $191,%0,%0":"+x"(a));else __asm__ volatile("palignr $191,%1,%0":"+x"(a):"x"(b));break;
case 192:if(alias)__asm__ volatile("palignr $192,%0,%0":"+x"(a));else __asm__ volatile("palignr $192,%1,%0":"+x"(a):"x"(b));break;
case 193:if(alias)__asm__ volatile("palignr $193,%0,%0":"+x"(a));else __asm__ volatile("palignr $193,%1,%0":"+x"(a):"x"(b));break;
case 194:if(alias)__asm__ volatile("palignr $194,%0,%0":"+x"(a));else __asm__ volatile("palignr $194,%1,%0":"+x"(a):"x"(b));break;
case 195:if(alias)__asm__ volatile("palignr $195,%0,%0":"+x"(a));else __asm__ volatile("palignr $195,%1,%0":"+x"(a):"x"(b));break;
case 196:if(alias)__asm__ volatile("palignr $196,%0,%0":"+x"(a));else __asm__ volatile("palignr $196,%1,%0":"+x"(a):"x"(b));break;
case 197:if(alias)__asm__ volatile("palignr $197,%0,%0":"+x"(a));else __asm__ volatile("palignr $197,%1,%0":"+x"(a):"x"(b));break;
case 198:if(alias)__asm__ volatile("palignr $198,%0,%0":"+x"(a));else __asm__ volatile("palignr $198,%1,%0":"+x"(a):"x"(b));break;
case 199:if(alias)__asm__ volatile("palignr $199,%0,%0":"+x"(a));else __asm__ volatile("palignr $199,%1,%0":"+x"(a):"x"(b));break;
case 200:if(alias)__asm__ volatile("palignr $200,%0,%0":"+x"(a));else __asm__ volatile("palignr $200,%1,%0":"+x"(a):"x"(b));break;
case 201:if(alias)__asm__ volatile("palignr $201,%0,%0":"+x"(a));else __asm__ volatile("palignr $201,%1,%0":"+x"(a):"x"(b));break;
case 202:if(alias)__asm__ volatile("palignr $202,%0,%0":"+x"(a));else __asm__ volatile("palignr $202,%1,%0":"+x"(a):"x"(b));break;
case 203:if(alias)__asm__ volatile("palignr $203,%0,%0":"+x"(a));else __asm__ volatile("palignr $203,%1,%0":"+x"(a):"x"(b));break;
case 204:if(alias)__asm__ volatile("palignr $204,%0,%0":"+x"(a));else __asm__ volatile("palignr $204,%1,%0":"+x"(a):"x"(b));break;
case 205:if(alias)__asm__ volatile("palignr $205,%0,%0":"+x"(a));else __asm__ volatile("palignr $205,%1,%0":"+x"(a):"x"(b));break;
case 206:if(alias)__asm__ volatile("palignr $206,%0,%0":"+x"(a));else __asm__ volatile("palignr $206,%1,%0":"+x"(a):"x"(b));break;
case 207:if(alias)__asm__ volatile("palignr $207,%0,%0":"+x"(a));else __asm__ volatile("palignr $207,%1,%0":"+x"(a):"x"(b));break;
case 208:if(alias)__asm__ volatile("palignr $208,%0,%0":"+x"(a));else __asm__ volatile("palignr $208,%1,%0":"+x"(a):"x"(b));break;
case 209:if(alias)__asm__ volatile("palignr $209,%0,%0":"+x"(a));else __asm__ volatile("palignr $209,%1,%0":"+x"(a):"x"(b));break;
case 210:if(alias)__asm__ volatile("palignr $210,%0,%0":"+x"(a));else __asm__ volatile("palignr $210,%1,%0":"+x"(a):"x"(b));break;
case 211:if(alias)__asm__ volatile("palignr $211,%0,%0":"+x"(a));else __asm__ volatile("palignr $211,%1,%0":"+x"(a):"x"(b));break;
case 212:if(alias)__asm__ volatile("palignr $212,%0,%0":"+x"(a));else __asm__ volatile("palignr $212,%1,%0":"+x"(a):"x"(b));break;
case 213:if(alias)__asm__ volatile("palignr $213,%0,%0":"+x"(a));else __asm__ volatile("palignr $213,%1,%0":"+x"(a):"x"(b));break;
case 214:if(alias)__asm__ volatile("palignr $214,%0,%0":"+x"(a));else __asm__ volatile("palignr $214,%1,%0":"+x"(a):"x"(b));break;
case 215:if(alias)__asm__ volatile("palignr $215,%0,%0":"+x"(a));else __asm__ volatile("palignr $215,%1,%0":"+x"(a):"x"(b));break;
case 216:if(alias)__asm__ volatile("palignr $216,%0,%0":"+x"(a));else __asm__ volatile("palignr $216,%1,%0":"+x"(a):"x"(b));break;
case 217:if(alias)__asm__ volatile("palignr $217,%0,%0":"+x"(a));else __asm__ volatile("palignr $217,%1,%0":"+x"(a):"x"(b));break;
case 218:if(alias)__asm__ volatile("palignr $218,%0,%0":"+x"(a));else __asm__ volatile("palignr $218,%1,%0":"+x"(a):"x"(b));break;
case 219:if(alias)__asm__ volatile("palignr $219,%0,%0":"+x"(a));else __asm__ volatile("palignr $219,%1,%0":"+x"(a):"x"(b));break;
case 220:if(alias)__asm__ volatile("palignr $220,%0,%0":"+x"(a));else __asm__ volatile("palignr $220,%1,%0":"+x"(a):"x"(b));break;
case 221:if(alias)__asm__ volatile("palignr $221,%0,%0":"+x"(a));else __asm__ volatile("palignr $221,%1,%0":"+x"(a):"x"(b));break;
case 222:if(alias)__asm__ volatile("palignr $222,%0,%0":"+x"(a));else __asm__ volatile("palignr $222,%1,%0":"+x"(a):"x"(b));break;
case 223:if(alias)__asm__ volatile("palignr $223,%0,%0":"+x"(a));else __asm__ volatile("palignr $223,%1,%0":"+x"(a):"x"(b));break;
case 224:if(alias)__asm__ volatile("palignr $224,%0,%0":"+x"(a));else __asm__ volatile("palignr $224,%1,%0":"+x"(a):"x"(b));break;
case 225:if(alias)__asm__ volatile("palignr $225,%0,%0":"+x"(a));else __asm__ volatile("palignr $225,%1,%0":"+x"(a):"x"(b));break;
case 226:if(alias)__asm__ volatile("palignr $226,%0,%0":"+x"(a));else __asm__ volatile("palignr $226,%1,%0":"+x"(a):"x"(b));break;
case 227:if(alias)__asm__ volatile("palignr $227,%0,%0":"+x"(a));else __asm__ volatile("palignr $227,%1,%0":"+x"(a):"x"(b));break;
case 228:if(alias)__asm__ volatile("palignr $228,%0,%0":"+x"(a));else __asm__ volatile("palignr $228,%1,%0":"+x"(a):"x"(b));break;
case 229:if(alias)__asm__ volatile("palignr $229,%0,%0":"+x"(a));else __asm__ volatile("palignr $229,%1,%0":"+x"(a):"x"(b));break;
case 230:if(alias)__asm__ volatile("palignr $230,%0,%0":"+x"(a));else __asm__ volatile("palignr $230,%1,%0":"+x"(a):"x"(b));break;
case 231:if(alias)__asm__ volatile("palignr $231,%0,%0":"+x"(a));else __asm__ volatile("palignr $231,%1,%0":"+x"(a):"x"(b));break;
case 232:if(alias)__asm__ volatile("palignr $232,%0,%0":"+x"(a));else __asm__ volatile("palignr $232,%1,%0":"+x"(a):"x"(b));break;
case 233:if(alias)__asm__ volatile("palignr $233,%0,%0":"+x"(a));else __asm__ volatile("palignr $233,%1,%0":"+x"(a):"x"(b));break;
case 234:if(alias)__asm__ volatile("palignr $234,%0,%0":"+x"(a));else __asm__ volatile("palignr $234,%1,%0":"+x"(a):"x"(b));break;
case 235:if(alias)__asm__ volatile("palignr $235,%0,%0":"+x"(a));else __asm__ volatile("palignr $235,%1,%0":"+x"(a):"x"(b));break;
case 236:if(alias)__asm__ volatile("palignr $236,%0,%0":"+x"(a));else __asm__ volatile("palignr $236,%1,%0":"+x"(a):"x"(b));break;
case 237:if(alias)__asm__ volatile("palignr $237,%0,%0":"+x"(a));else __asm__ volatile("palignr $237,%1,%0":"+x"(a):"x"(b));break;
case 238:if(alias)__asm__ volatile("palignr $238,%0,%0":"+x"(a));else __asm__ volatile("palignr $238,%1,%0":"+x"(a):"x"(b));break;
case 239:if(alias)__asm__ volatile("palignr $239,%0,%0":"+x"(a));else __asm__ volatile("palignr $239,%1,%0":"+x"(a):"x"(b));break;
case 240:if(alias)__asm__ volatile("palignr $240,%0,%0":"+x"(a));else __asm__ volatile("palignr $240,%1,%0":"+x"(a):"x"(b));break;
case 241:if(alias)__asm__ volatile("palignr $241,%0,%0":"+x"(a));else __asm__ volatile("palignr $241,%1,%0":"+x"(a):"x"(b));break;
case 242:if(alias)__asm__ volatile("palignr $242,%0,%0":"+x"(a));else __asm__ volatile("palignr $242,%1,%0":"+x"(a):"x"(b));break;
case 243:if(alias)__asm__ volatile("palignr $243,%0,%0":"+x"(a));else __asm__ volatile("palignr $243,%1,%0":"+x"(a):"x"(b));break;
case 244:if(alias)__asm__ volatile("palignr $244,%0,%0":"+x"(a));else __asm__ volatile("palignr $244,%1,%0":"+x"(a):"x"(b));break;
case 245:if(alias)__asm__ volatile("palignr $245,%0,%0":"+x"(a));else __asm__ volatile("palignr $245,%1,%0":"+x"(a):"x"(b));break;
case 246:if(alias)__asm__ volatile("palignr $246,%0,%0":"+x"(a));else __asm__ volatile("palignr $246,%1,%0":"+x"(a):"x"(b));break;
case 247:if(alias)__asm__ volatile("palignr $247,%0,%0":"+x"(a));else __asm__ volatile("palignr $247,%1,%0":"+x"(a):"x"(b));break;
case 248:if(alias)__asm__ volatile("palignr $248,%0,%0":"+x"(a));else __asm__ volatile("palignr $248,%1,%0":"+x"(a):"x"(b));break;
case 249:if(alias)__asm__ volatile("palignr $249,%0,%0":"+x"(a));else __asm__ volatile("palignr $249,%1,%0":"+x"(a):"x"(b));break;
case 250:if(alias)__asm__ volatile("palignr $250,%0,%0":"+x"(a));else __asm__ volatile("palignr $250,%1,%0":"+x"(a):"x"(b));break;
case 251:if(alias)__asm__ volatile("palignr $251,%0,%0":"+x"(a));else __asm__ volatile("palignr $251,%1,%0":"+x"(a):"x"(b));break;
case 252:if(alias)__asm__ volatile("palignr $252,%0,%0":"+x"(a));else __asm__ volatile("palignr $252,%1,%0":"+x"(a):"x"(b));break;
case 253:if(alias)__asm__ volatile("palignr $253,%0,%0":"+x"(a));else __asm__ volatile("palignr $253,%1,%0":"+x"(a):"x"(b));break;
case 254:if(alias)__asm__ volatile("palignr $254,%0,%0":"+x"(a));else __asm__ volatile("palignr $254,%1,%0":"+x"(a):"x"(b));break;
case 255:if(alias)__asm__ volatile("palignr $255,%0,%0":"+x"(a));else __asm__ volatile("palignr $255,%1,%0":"+x"(a):"x"(b));break;
}return a;}
static void reference(unsigned op,uint8_t out[16],const uint8_t a[16],const uint8_t b[16],unsigned count){
 if(op==6){for(unsigned i=0;i<16;i++)out[i]=(b[i]&128)?0:a[b[i]&15];return;}
 if(op==7){for(unsigned i=0;i<16;i++){unsigned k=count+i;out[i]=k<16?b[k]:k<32?a[k-16]:0;}return;}
 unsigned bits=(op==1||op==4)?32:16,bytes=bits/8,lanes=16/bytes;
 for(unsigned side=0;side<2;side++)for(unsigned i=0;i<lanes;i+=2){
  const uint8_t *p=(side?b:a)+i*bytes;uint32_t x=0,y=0;memcpy(&x,p,bytes);memcpy(&y,p+bytes,bytes);
  uint32_t z;
  if(op==2||op==5){int32_t sx=(int16_t)x,sy=(int16_t)y,v=op==2?sx+sy:sx-sy;if(v>32767)v=32767;if(v< -32768)v=-32768;z=(uint16_t)v;}
  else z=op<3?x+y:x-y;
  memcpy(out+(side*(lanes/2)+i/2)*bytes,&z,bytes);
 }
}
static void hex(const uint8_t p[16]){for(int i=0;i<16;i++)printf("%02x",p[i]);}
int main(void){
 const char* names[]={"PHADDW","PHADDD","PHADDSW","PHSUBW","PHSUBD","PHSUBSW","PSHUFB","PALIGNR"};
 v16 (*functions[])(v16,v16,int)={phaddw,phaddd,phaddsw,phsubw,phsubd,phsubsw,pshufb};
 unsigned all_fail=0,all_cases=0;
 for(unsigned op=0;op<8;op++){
  unsigned fail[2]={0},cases=0;
  for(int alias=0;alias<2;alias++)for(unsigned test=0;test<(op==7?256*16:10000);test++){
   uint8_t aa[16],bb[16],expected[16],actual[16];for(int i=0;i<16;i++){aa[i]=(uint8_t)next();bb[i]=(uint8_t)next();}
   if(test==0)memset(aa,255,16);
   if(alias)memcpy(bb,aa,16);
   v16 a,b,result;memcpy(&a,aa,16);memcpy(&b,bb,16);unsigned count=test%256;
   reference(op,expected,aa,bb,count);result=op==7?palignr(a,b,alias,count):functions[op](a,b,alias);memcpy(actual,&result,16);
   if(memcmp(expected,actual,16)){
    if(!fail[alias]){printf("FAIL %s alias=%d count=%u a=",names[op],alias,count);hex(aa);printf(" b=");hex(bb);printf(" expected=");hex(expected);printf(" actual=");hex(actual);puts("");}
    fail[alias]++;
   }
   cases++;
  }
  printf("%s cases=%u distinct_fail=%u alias_fail=%u\n",names[op],cases,fail[0],fail[1]);all_fail+=fail[0]+fail[1];all_cases+=cases;
 }
 printf("TOTAL cases=%u failures=%u\n",all_cases,all_fail);return all_fail?1:0;
}
