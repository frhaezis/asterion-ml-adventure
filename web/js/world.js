/* Lightweight exploration over original illustrated locations. No combat gate. */
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const ROUTES=[
 [[.45,.86],[.53,.69],[.66,.52]],[[.25,.85],[.46,.73],[.69,.57]],
 [[.78,.84],[.65,.71],[.47,.51]],[[.26,.82],[.52,.77],[.72,.54]],
 [[.40,.87],[.52,.68],[.57,.45]],[[.76,.84],[.60,.70],[.43,.55]],
 [[.30,.86],[.48,.68],[.70,.51]],[[.74,.86],[.57,.72],[.43,.52]],
 [[.40,.84],[.57,.71],[.72,.55]],[[.30,.84],[.50,.66],[.66,.49]]
];
export class World{
 constructor(canvas,{onMove=()=>{},onInteract=()=>{},onEvent=()=>{}}={}){
  this.canvas=canvas;this.ctx=canvas.getContext('2d');this.onMove=onMove;this.onInteract=onInteract;this.onEvent=onEvent;
  this.player={x:.45,y:.86};this.chapter=1;this.level={chapter:1,number:1};this.keys=new Set();this.vector={x:0,y:0};this.target=null;this.paused=false;this.reducedMotion=false;this.needsRedraw=true;this.time=0;this.lastFrame=0;this.timeScale=1;this.completed=[];
  this.route=ROUTES[0];this.console={x:this.route[2][0],y:this.route[2][1]};
  this._down=e=>{if(this.paused||/^(INPUT|TEXTAREA|SELECT|BUTTON)$/.test(e.target?.tagName))return;if(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code)){e.preventDefault();this.keys.add(e.code);this.target=null;}if(!e.repeat&&['KeyE','Enter'].includes(e.code)){e.preventDefault();this.onInteract('console');}};
  this._up=e=>this.keys.delete(e.code);this._blur=()=>{this.keys.clear();this.setMoveVector(0,0);};this._pointer=e=>this.pointer(e);
  window.addEventListener('keydown',this._down);window.addEventListener('keyup',this._up);window.addEventListener('blur',this._blur);canvas.addEventListener('pointerdown',this._pointer);
  this.observer=new ResizeObserver(()=>this.resize());this.observer.observe(canvas);this.resize();this.frame=requestAnimationFrame(t=>this.tick(t));
 }
 resize(){const r=this.canvas.getBoundingClientRect(),d=Math.min(devicePixelRatio||1,1.75);this.canvas.width=Math.max(1,Math.round(r.width*d));this.canvas.height=Math.max(1,Math.round(r.height*d));this.needsRedraw=true;}
 setState(state){this.completed=Array.isArray(state.completed)?[...state.completed]:[];this.setLevel({...this.level,chapter:state.chapter||1});if(state.player&&state.player.x>=0&&state.player.x<=1&&state.player.y>=0&&state.player.y<=1)this.player={...state.player};this.needsRedraw=true;}
 setLevel(level){this.level=level;const next=clamp(Number(level?.chapter)||1,1,10);if(next!==this.chapter){this.chapter=next;this.route=ROUTES[next-1];this.player={x:this.route[0][0],y:this.route[0][1]};this.target=null;this.console={x:this.route[2][0],y:this.route[2][1]};}this.needsRedraw=true;}
 setPaused(value){this.paused=!!value;if(this.paused){this.keys.clear();this.vector={x:0,y:0};}this.needsRedraw=true;}
 setReducedMotion(value){this.reducedMotion=!!value;this.needsRedraw=true;}
 setMoveVector(x,y){const n=Math.hypot(x,y)||1;this.vector={x:n>1?x/n:x,y:n>1?y/n:y};if(Math.hypot(x,y)>.05)this.target=null;}
 setTimeScale(value){this.timeScale=clamp(Number(value)||1,1,8);}
 navigateToConsole(){this.target={...this.console,interact:true};return true;}
 command(action){if(this.paused)return false;if(action==='interact'){this.onInteract('console');return true;}return false;}
 pointer(e){if(this.paused)return;const r=this.canvas.getBoundingClientRect();this.canvas.focus({preventScroll:true});const x=(e.clientX-r.left)/r.width,y=(e.clientY-r.top)/r.height;if(Math.hypot(x-this.console.x,y-this.console.y)<.09){this.navigateToConsole();return;}this.target={x:clamp(x,.13,.88),y:clamp(y,.42,.88)};}
 notifyMove(){this.onMove({x:this.player.x,y:this.player.y});}
 tick(now){if(this.destroyed)return;const dt=Math.min(.05,Math.max(0,(now-(this.lastFrame||now))/1000))*this.timeScale;this.lastFrame=now;
  if(!this.paused){this.time+=dt;let dx=this.vector.x,dy=this.vector.y;if(this.keys.has('KeyA')||this.keys.has('ArrowLeft'))dx--;if(this.keys.has('KeyD')||this.keys.has('ArrowRight'))dx++;if(this.keys.has('KeyW')||this.keys.has('ArrowUp'))dy--;if(this.keys.has('KeyS')||this.keys.has('ArrowDown'))dy++;
   if(this.target){dx=this.target.x-this.player.x;dy=this.target.y-this.player.y;if(Math.hypot(dx,dy)<.012){const hit=this.target.interact;this.target=null;if(hit){this.notifyMove();this.onInteract('console');}dx=dy=0;}}
   const n=Math.hypot(dx,dy);if(n>.001){this.player.x=clamp(this.player.x+dx/n*dt*.19,.13,.88);this.player.y=clamp(this.player.y+dy/n*dt*.14,.42,.88);this.needsRedraw=true;if(now-(this.lastMove||0)>700){this.lastMove=now;this.notifyMove();}}
   if(!this.reducedMotion)this.needsRedraw=true;
  }
  if(this.needsRedraw){this.draw();this.needsRedraw=false;}this.frame=requestAnimationFrame(t=>this.tick(t));
 }
 draw(){const c=this.ctx,w=this.canvas.width,h=this.canvas.height,unit=Math.min(w/1280,h/720);c.clearRect(0,0,w,h);
  // A route is a navigation cue; the distinct illustrated architecture stays unobscured.
  c.save();c.strokeStyle='#e9e0b538';c.lineWidth=Math.max(1,unit*1.5);c.setLineDash([3*unit,10*unit]);c.beginPath();this.route.forEach(([x,y],i)=>i?c.lineTo(x*w,y*h):c.moveTo(x*w,y*h));c.stroke();c.setLineDash([]);
  for(let i=0;i<18;i++){const x=((i*.137+this.chapter*.057)%1)*w,y=(.28+((i*.173)%1)*.6)*h;const flick=this.reducedMotion?.65:.35+Math.sin(this.time*.6+i*1.7)*.2;c.fillStyle=`rgba(230,232,188,${flick})`;c.beginPath();c.arc(x+Math.sin(this.time*.2+i)*5*unit,y+Math.cos(this.time*.3+i)*4*unit,Math.max(.8,unit*1.5),0,Math.PI*2);c.fill();}
  const nx=this.console.x*w,ny=this.console.y*h,pulse=this.reducedMotion?0:Math.sin(this.time*1.8)*3*unit;const glow=c.createRadialGradient(nx,ny,2,nx,ny,55*unit);glow.addColorStop(0,'#d9e9b44c');glow.addColorStop(1,'#d9e9b400');c.fillStyle=glow;c.beginPath();c.arc(nx,ny,55*unit,0,Math.PI*2);c.fill();
  c.strokeStyle='#f5deb9';c.lineWidth=Math.max(1.3,unit*1.7);c.beginPath();c.ellipse(nx,ny,23*unit+pulse,11*unit+pulse*.4,0,0,Math.PI*2);c.stroke();c.beginPath();c.moveTo(nx,ny-35*unit);c.lineTo(nx+8*unit,ny-25*unit);c.lineTo(nx,ny-15*unit);c.lineTo(nx-8*unit,ny-25*unit);c.closePath();c.fillStyle='#f8e8bb';c.fill();
  c.font=`${Math.max(11,13*unit)}px Georgia`;c.textAlign='center';c.fillStyle='#fff1d8';c.shadowColor='#081020';c.shadowBlur=8;c.fillText(this.level.npc||'Место встречи',nx,ny-49*unit);c.shadowBlur=0;
  const x=this.player.x*w,y=this.player.y*h;c.fillStyle='#06101c5e';c.beginPath();c.ellipse(x,y,16*unit,6*unit,0,0,Math.PI*2);c.fill();c.strokeStyle='#e5f5eb';c.lineWidth=Math.max(1.2,unit*1.8);c.beginPath();c.arc(x,y-9*unit,5*unit,0,Math.PI*2);c.stroke();c.beginPath();c.moveTo(x,y-4*unit);c.lineTo(x-9*unit,y+1*unit);c.lineTo(x+9*unit,y+1*unit);c.closePath();c.fillStyle='#cfe1d4cc';c.fill();
  if(this.target){c.strokeStyle='#d1edf28c';c.beginPath();c.ellipse(this.target.x*w,this.target.y*h,11*unit,5*unit,0,0,Math.PI*2);c.stroke();}c.restore();
 }
 destroy(){this.destroyed=true;cancelAnimationFrame(this.frame);this.observer.disconnect();window.removeEventListener('keydown',this._down);window.removeEventListener('keyup',this._up);window.removeEventListener('blur',this._blur);this.canvas.removeEventListener('pointerdown',this._pointer);}
}
