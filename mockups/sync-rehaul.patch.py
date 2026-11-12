"""Sync rehaul (IDEAS.md Phase 2 + roll-call 'last time') — the patch behind
mockups/sync-rehaul.html.

    python mockups/sync-rehaul.patch.py TeamDesk.html     # apply to the app, once approved

Every replacement asserts it lands exactly once, so it refuses to half-apply."""
import io, re, sys

def patch(s):
    def rep(old, new, cnt=1):
        nonlocal s
        n = s.count(old)
        assert n == cnt, (old[:90], n)
        s = s.replace(old, new)

    def fn_bounds(name):
        a = s.index("\nfunction " + name + "(") + 1
        m = re.compile(r"\n(?=function |async function |/\*|let |const |document\.)").search(s, a + 10)
        return a, m.start() + 1

    def replace_fn(name, new):
        nonlocal s
        a, b = fn_bounds(name)
        s = s[:a] + new.rstrip("\n") + "\n" + s[b:]

    # ------------------------------------------------------------------ data (v3)
    rep("const DATA_VERSION=2;", "const DATA_VERSION=3;")
    rep('''function normSync(s){return {id:s.id||uid(),date:s.date||todayStr(),team:s.team||"portal",''',
        '''function normSync(s){return {id:s.id||uid(),date:s.date||todayStr(),team:s.team||"portal",
  /* the call as an instrument: when it started and ended, what the team's open tickets
     looked like at the start (dropped at close), and what changed — kept for next time */
  startedAt:+s.startedAt||0,closedAt:+s.closedAt||0,
  baseline:(s.baseline&&typeof s.baseline==="object"&&s.baseline.t)?s.baseline:null,
  recap:(s.recap&&typeof s.recap==="object")?normRecap(s.recap):null,''')
    rep('''function normPromise(p){return {id:p.id||uid(),eta:p.eta||"",givenOn:p.givenOn||todayStr(),note:p.note||""};}''',
        '''function normPromise(p){return {id:p.id||uid(),eta:p.eta||"",givenOn:p.givenOn||todayStr(),note:p.note||"",syncId:p.syncId||""};}
function normRecap(r){const A=x=>Array.isArray(x)?x:[];
  return {status:A(r.status),etas:A(r.etas),hRaised:A(r.hRaised),hCleared:A(r.hCleared),closed:A(r.closed),added:A(r.added)};}''')
    rep('''  raisedOn:h.raisedOn||todayStr(),owner:h.owner||"",resolvedOn:h.resolvedOn||"",resolution:h.resolution||""};}''',
        '''  raisedOn:h.raisedOn||todayStr(),owner:h.owner||"",resolvedOn:h.resolvedOn||"",resolution:h.resolution||"",
  syncId:h.syncId||"",clearedSyncId:h.clearedSyncId||""};}''')
    rep('''  return {counts,closed:optNum(l.closed),added:optNum(l.added)};''',
        '''  /* what the incidents actually were, one line each — the count can stay the same
     while the incidents change — and what became of last call's lines */
  const items=(l.items||[]).filter(x=>x&&String(x.text||"").trim())
    .map(x=>({id:x.id||uid(),text:String(x.text).trim(),from:x.from||""}));
  const followups={};
  if(l.followups&&typeof l.followups==="object"&&!Array.isArray(l.followups))
    Object.entries(l.followups).forEach(([k,v])=>{if(v&&["still","gone","ask"].includes(v.state))followups[k]={state:v.state,answer:String(v.answer||"")};});
  return {counts,closed:optNum(l.closed),added:optNum(l.added),items,followups};''')

    # ------------------------------------------------------------------ sync v2 helpers
    rep("function renderSync(){", SYNC_HELPERS + "\nfunction renderSync(){")
    rep("function syncSelect(kind,id){\n  syncSelectReset();",
        "function syncSelect(kind,id){\n  if(typeof capDraftSave===\"function\")capDraftSave();\n  syncSelectReset();")
    # the old renderSync, rebuilt around the header; keep its queue sections and wiring
    a, b = fn_bounds("renderSync")
    old = s[a:b]
    i = old.index("        ${(()=>{const om=openMentions(s.team);")
    j = old.index("        ${pending.length?")
    mid_sections = old[i:j]
    k = old.index('  wrap.querySelectorAll("[data-agdone]")')
    l = old.index("  const gEpic=syncEpicId?epicById(syncEpicId):null;")
    mid_wiring = old[k:l]
    replace_fn("renderSync", RENDER_SYNC.replace("@@SECTIONS@@", mid_sections).replace("@@WIRING@@", mid_wiring))
    replace_fn("renderCapture", RENDER_CAPTURE)
    replace_fn("closeSync", CLOSE_SYNC)
    replace_fn("nextInQueue", '''function nextInQueue(s,fromId){stepQueue(s,fromId,1);}''')
    # the epic group pane and the start of a call
    rep('''    if(ei&&ei.value)t.promises.push(normPromise({eta:ei.value,givenOn:s.date,note:"given in "+(s.title||"sync")}));''',
        '''    if(ei&&ei.value)t.promises.push(normPromise({eta:ei.value,givenOn:s.date,note:"given in "+(s.title||"sync"),syncId:s.id}));''')
    rep('''  const s=normSync({team,date:todayStr(),title:teamOf(team).name+" sync — "+fmtDate(todayStr())});''',
        '''  const s=normSync({team,date:todayStr(),title:teamOf(team).name+" sync — "+fmtDate(todayStr()),
    startedAt:Date.now(),baseline:syncBaseline(team)});''')
    # the roll-call: incident lines + last time
    rep('''    ${rollLaneHtml(r,"incidents",prev)}''', '''    ${rollLaneHtml(r,"incidents",prev)}
    ${rollLinesHtml(r)}''')
    rep('''    state.rollcalls=state.rollcalls.filter(x=>x.id!==r.id);markDirty();syncSelect(null);};
}''', '''    state.rollcalls=state.rollcalls.filter(x=>x.id!==r.id);markDirty();syncSelect(null);};
  wireRollLines(host,r);
}''')
    # timer ticks with the clock
    rep('''  const g=document.getElementById("ckGreet");if(g)g.textContent=greetText();
  updateSb();},1000);''', '''  const g=document.getElementById("ckGreet");if(g)g.textContent=greetText();
  const stm=document.getElementById("syncTimer");if(stm){const sx=activeSync();if(sx)stm.textContent=syncElapsed(sx);}
  updateSb();},1000);''')

    # ------------------------------------------------------------------ Today: the agenda
    rep('''function cockpitHTML(){''', '''function cockpitHTML(agHtml){''')
    rep('''    <div class="ck-sech"><span class="ck-lbl">Pulse · read from your data file</span></div>''',
        '''    ${agHtml||""}
    <div class="ck-sech"><span class="ck-lbl">Pulse · read from your data file</span></div>''')
    rep('''  const attn=shown.reduce((n,c)=>n+c.n,0);
  det.innerHTML=`<div class="dash cockpit"><div class="ck-in">${cockpitHTML()}<div class="ck-sech"><span class="ck-lbl">Needs attention · ${attn}</span></div>''',
        '''  const attn=shown.reduce((n,c)=>n+c.n,0),AG=agendaItems();
  det.innerHTML=`<div class="dash cockpit"><div class="ck-in">${cockpitHTML(agendaBlockHTML(AG))}<div class="ck-sech"><span class="ck-lbl">Watchlist · ${attn}</span></div>''')
    rep('''  shown.forEach(c=>c.wire());mountCockpit(det);
}''', '''  shown.forEach(c=>c.wire());mountCockpit(det);wireAgenda(det,AG);
}''')
    # cards the agenda now carries
    def cut(start, end):
        nonlocal s
        a = s.index(start); assert s.count(start) == 1, start[:50]
        b = s.index(end, a) + len(end)
        s = s[:a] + s[b:]
    cut('''  /* vendor: approvals awaiting your email sign-off */''', '''view="effort";renderApp();}};}),"warn"));\n''')
    cut('''  /* the answer that walked out of the room''', '''knowledgeTab="mentions";view="knowledge";renderApp();}})),"warn"));\n''')
    cut('''  const dueRisks=state.risks.filter(riskNeedsReview);''', '''"warn"));\n''')
    rep('''  cards.push(dashCard("⚑ Open action points",openActionsAll().map(x=>({''',
        '''  cards.push(dashCard("⚑ Open action points",openActionsAll().filter(x=>!(x.action.due&&daysUntil(x.action.due)<=2)).map(x=>({''')

    # ------------------------------------------------------------------ styles
    rep('''  .dbar{display:block;flex:none}''', '''  .dbar{display:block;flex:none}''' + SYNC_CSS)
    return s


SYNC_HELPERS = r'''/* ===================== SYNC v2 — the call as an instrument =====================
   Syncs are most of the use, so the call gets an instrument of its own: a header that
   says how far through you are, what you've captured, how long you've been on and
   what's next; keys so the hands stay on the keyboard; a "last time" pane so a call
   starts where the previous one ended; and a close sheet that keeps what changed. */
let syncKeyNav=false;   /* a J/K move leaves focus off the note, so the next J/K still works */
/* the open ticket pane's "keep what's typed" — called before ANY move, rather than
   trusting the field's blur event, which doesn't fire in every case */
let capDraftSave=null;
/* the pending tickets in the order the queue shows them — epic groups kept together,
   each ordered by its most urgent ticket. keepId stays listed even if covered, so
   "the one after this" can be found from a ticket just marked covered. */
function queueOrder(s,keepId){
  const q=queueFor(s.team),cov=new Set(s.covered.filter(c=>c.done).map(c=>c.ticketId));
  const listed=q.filter(x=>!cov.has(x.t.id)||x.t.id===keepId),blocks=[],byEpic={};
  listed.forEach(x=>{const e=x.t.epicId?epicById(x.t.epicId):null;
    if(e){(byEpic[e.id]=byEpic[e.id]||{epic:e,items:[]}).items.push(x);}
    else blocks.push({kind:"t",score:x.score,x});});
  Object.values(byEpic).forEach(g=>blocks.push({kind:"e",score:Math.max(...g.items.map(i=>i.score)),epic:g.epic,items:g.items}));
  blocks.sort((a,b)=>b.score-a.score);
  return {blocks,pending:q.filter(x=>!cov.has(x.t.id)),done:q.filter(x=>cov.has(x.t.id)),
    ids:blocks.flatMap(b=>b.kind==="t"?[b.x.t.id]:b.items.map(i=>i.t.id))};
}
function stepQueue(s,fromId,dir){
  const cov=new Set(s.covered.filter(c=>c.done).map(c=>c.ticketId));
  const ids=queueOrder(s,fromId).ids.filter(id=>id===fromId||!cov.has(id));
  const rest=ids.filter(id=>id!==fromId);
  if(!rest.length){syncSelect(null);if(!queueOrder(s).pending.length)toast("All covered ✓");return;}
  const i=ids.indexOf(fromId);
  let j=i<0?(dir>0?0:ids.length-1):(i+dir+ids.length)%ids.length;
  if(ids[j]===fromId)j=(j+dir+ids.length)%ids.length;
  syncSelect("ticket",ids[j]);
}
function syncStep(s,dir,byKey){
  if(capDraftSave)capDraftSave();
  const a=document.activeElement;if(a&&a!==document.body&&a.blur)a.blur();
  syncKeyNav=!!byKey;stepQueue(s,syncFocusId,dir);
}
/* the previous CLOSED call with this team, by date then creation */
function syncKey(x){return (x.date||"")+"|"+String(x.createdAt||0).padStart(15,"0");}
function previousSync(s){
  return state.syncs.filter(x=>x.team===s.team&&x.id!==s.id&&x.closed&&syncKey(x)<syncKey(s))
    .sort((a,b)=>syncKey(a)<syncKey(b)?1:-1)[0]||null;
}
function syncBaseline(team){
  const t={};
  state.tickets.forEach(x=>{if(x.team===team&&isOpen(x)){const lp=latestPromise(x);
    t[x.id]={st:x.myStatus,eta:lp?lp.eta:"",h:openHurdles(x).map(h=>h.id)};}});
  return {at:Date.now(),t};
}
/* What changed on the tickets during the call. With a baseline it also catches what
   was changed on the full ticket page mid-call; without one (a call started before
   this existed) it uses what was captured in the call itself. */
function syncRecap(s){
  const B=s.baseline,R={status:[],etas:[],hRaised:[],hCleared:[],closed:[],added:[]};
  state.tickets.forEach(t=>{
    const b=B&&B.t?B.t[t.id]:null;
    promisesInOrder(t).forEach((p,i,arr)=>{if(p.syncId!==s.id)return;
      const prev=i>0?arr[i-1].eta:"";R.etas.push({id:t.id,eta:p.eta,prev,slip:!!(prev&&p.eta&&p.eta>prev)});});
    t.hurdles.forEach(h=>{const txt=h.text||HURDLE_KINDS[h.kind].label;
      if(h.syncId===s.id||(b&&!h.resolvedOn&&!b.h.includes(h.id)))R.hRaised.push({id:t.id,text:txt});
      if(h.clearedSyncId===s.id||(b&&h.resolvedOn&&b.h.includes(h.id)))R.hCleared.push({id:t.id,text:txt});});
    if(b&&b.st!==t.myStatus){if(t.myStatus==="done")R.closed.push(t.id);else R.status.push({id:t.id,from:b.st,to:t.myStatus});}
    if(B&&!b&&t.team===s.team&&isOpen(t)&&(t.createdAt||0)>=B.at)R.added.push(t.id);});
  return R;
}
function syncCaptured(s){
  let updates=0,etas=0,hRaised=0,hCleared=0;
  state.tickets.forEach(t=>{t.updates.forEach(u=>{if(u.syncId===s.id)updates++;});
    t.promises.forEach(p=>{if(p.syncId===s.id)etas++;});
    t.hurdles.forEach(h=>{if(h.syncId===s.id)hRaised++;if(h.clearedSyncId===s.id)hCleared++;});});
  return {updates,etas,hRaised,hCleared,notes:state.mentions.filter(m=>m.syncId===s.id).length};
}
function durTxt(ms){const m=Math.max(1,Math.round(ms/60000));return m<60?m+" min":Math.floor(m/60)+" h "+p2(m%60);}
function syncElapsed(s){
  if(!s.startedAt||(s.closed&&!s.closedAt))return "—";
  const ms=Math.max(0,(s.closed?s.closedAt:Date.now())-s.startedAt);
  if(ms>6*3600000)return s.closed?durTxt(ms):"since "+new Date(s.startedAt).toTimeString().slice(0,5);
  const t=Math.floor(ms/1000),h=Math.floor(t/3600),m=Math.floor(t%3600/60);
  return (h?h+":"+p2(m):p2(m))+":"+p2(t%60);
}
function lastTimeLine(p){
  const C=syncCaptured(p),R=p.recap,bits=[];
  if(C.updates)bits.push(C.updates+" said");
  const et=R?R.etas.length:C.etas,sl=R?R.etas.filter(x=>x.slip).length:0;
  if(et)bits.push(et+" ETA"+(et===1?"":"s")+(sl?" ("+sl+" slipped)":""));
  if(R&&R.closed.length)bits.push(R.closed.length+" closed");
  const hr=R?R.hRaised.length:C.hRaised;if(hr)bits.push(hr+" hurdle"+(hr===1?"":"s"));
  const oa=p.actions.filter(a=>!a.done).length;if(oa)bits.push(oa+" action"+(oa===1?"":"s")+" open");
  return bits.join(" · ")||"nothing captured on tickets";
}
/* the most recent earlier roll-call of this team that noted what the incidents were */
function lastRollLines(team,cur){
  const k=x=>(x.date||"")+"|"+String(x.createdAt||0).padStart(15,"0");
  return state.rollcalls.filter(r=>r.team===team&&r.incidents.items.length&&(!cur||(r.id!==cur.id&&k(r)<k(cur))))
    .sort((a,b)=>k(a)<k(b)?1:-1)[0]||null;
}
function recapHTML(R){
  if(!R)return "";
  const L=id=>{const t=ticketByRef(id);return t?`<span class="mono">${esc(t.ticketId||"—")}</span> ${esc(clip(t.title||"",56))}`:null;};
  const SL=k=>MY_STATUS[k]?MY_STATUS[k].label:k,rows=[];
  R.closed.forEach(id=>{const l=L(id);if(l)rows.push(["good","Closed",l]);});
  R.status.forEach(x=>{const l=L(x.id);if(l)rows.push(["","Status",l+` <span class="faint">${esc(SL(x.from))} →</span> <b>${esc(SL(x.to))}</b>`]);});
  R.etas.forEach(x=>{const l=L(x.id);if(l)rows.push([x.slip?"bad":"","ETA",l+` → <b>${fmtDate(x.eta)}</b>${x.prev?` <span class="faint">was ${fmtDate(x.prev)}</span>`:""}${x.slip?` <span class="warnchip bad">slipped</span>`:""}`]);});
  R.hRaised.forEach(x=>{const l=L(x.id);if(l)rows.push(["warn","Hurdle",l+` — ${esc(x.text)}`]);});
  R.hCleared.forEach(x=>{const l=L(x.id);if(l)rows.push(["good","Cleared",l+` — ${esc(x.text)}`]);});
  R.added.forEach(id=>{const l=L(id);if(l)rows.push(["","New",l]);});
  if(!rows.length)return `<p class="faint" style="font-size:12px;margin:0">Nothing changed on the tickets.</p>`;
  return `<div class="recap">${rows.map(([c,k,h])=>`<div class="rcp ${c}"><span class="rk">${k}</span><span class="rv">${h}</span></div>`).join("")}</div>`;
}
function capChip(n,label){return `<span class="capc ${n?"on":""}"><b>${n}</b> ${label}${n===1?"":"s"}</span>`;}
function syncHeadHTML(s,O){
  const all=O.pending.length+O.done.length,C=syncCaptured(s),rc=rollcallForSync(s.id);
  const nx=O.ids.find(id=>id!==syncFocusId),nt=nx?ticketByRef(nx):null;
  return `<div class="shead">
    <div class="sh-l">
      <div class="sh-no">${s.closed?`<span class="sh-state">closed</span>`:`<span class="sh-live"><i></i>live</span>`}${teamPill(s.team)}<span>${fmtDate(s.date)}</span></div>
      <div class="sh-title" id="sh-title" title="Click to rename">${esc(s.title||"(untitled sync)")}</div>
      <div class="sh-btns">
        <button class="sm" id="sq-new">＋ Ticket</button>
        <button class="sm" id="sq-ment">＋ Incident note</button>
        <button class="sm" id="sq-agenda" title="Park a point for a later sync">Point to raise</button>
        <button class="sm" id="sq-notes" title="Points, actions, notes (N)">Notes</button>
        <button class="sm" id="sq-keys" title="Keys (?)">Keys</button>
        ${s.closed?`<button class="sm" id="sq-reopen">Reopen</button>`:`<button class="sm go" id="sq-close">Close sync</button>`}</div></div>
    <div class="sh-cov" title="${O.done.length} of ${all} tickets covered">
      <div class="k">Covered</div>
      <div class="sh-dots">${O.done.map(()=>`<i class="on"></i>`).join("")}${O.ids.map(id=>`<i class="${id===syncFocusId?"cur":""}"></i>`).join("")}</div>
      <div class="v">${O.done.length}<small>of ${all} · ${O.pending.length} to go</small></div></div>
    <div class="sh-cap"><div class="k">Captured this call</div><div class="v">
      ${capChip(C.updates,"update")}${capChip(C.etas,"ETA")}${capChip(C.hRaised,"hurdle")}${C.hCleared?capChip(C.hCleared,"cleared"):""}${capChip(s.actions.length,"action")}${capChip(C.notes,"incident note")}
      <span class="capc ${rc&&rc.recorded?"on":""}">roll-call ${rc&&rc.recorded?"✓":"—"}</span></div></div>
    <div class="sh-time"><div class="k">${s.closed?"Took":"On the call"}</div><div class="v" id="syncTimer">${syncElapsed(s)}</div></div>
    <div class="sh-next"><div class="k">Next up <kbd>J</kbd></div>${nt?`<button class="sh-nextbtn" id="sh-next" title="Next ticket (J, or Alt+↓ while typing)"><span class="mono">${esc(nt.ticketId||"—")}</span> ${esc(clip(nt.title||"",30))} ›</button>`
      :`<div class="v" style="font-size:12px;font-family:var(--sans)">${O.pending.length?"—":"All covered ✓"}</div>`}</div>
  </div>`;
}
function etaLedgerHTML(t){
  const ps=promisesInOrder(t).filter(p=>p.eta);
  if(!ps.length)return `<div class="etaled none"><span class="k">ETA</span><span>none given yet — ask for one <kbd>E</kbd></span></div>`;
  const cur=ps[ps.length-1],d=daysUntil(cur.eta),miss=promiseMissed(t),sl=slipCount(t);
  return `<div class="etaled ${miss?"bad":sl?"warn":""}"><span class="k">ETA</span><b>${fmtDate(cur.eta)}</b>
    <span class="ed">${t.myStatus==="done"?"":miss?(-d)+" d past":d===0?"today":d>0?"in "+d+" d":""}</span>
    ${ps.length>1?`<span class="eh">before that ${ps.slice(0,-1).reverse().slice(0,4).map(p=>fmtDate(p.eta)).join(" · ")}</span>`:""}
    ${sl?`<span class="es">${sl}× slipped</span>`:""}</div>`;
}
function capStatusSeg(t){return `<div class="seg" id="cap-seg">${Object.entries(MY_STATUS).map(([k,v])=>
  `<button data-cs="${k}" class="${k===t.myStatus?"on":""}" style="--pen:${MY_PEN[k]}"><i></i>${esc(v.label.split(" /")[0])}</button>`).join("")}</div>`;}
function openSyncKeys(){
  const root=document.getElementById("modalRoot");
  const K=[["J / K","next / previous ticket"],["Alt+↓ / Alt+↑","the same, while typing"],["U","type what they said"],
    ["Ctrl+Enter","mark covered while typing"],["C","mark covered"],["E","new ETA"],["H","add a hurdle"],["A","add an action"],
    ["R","roll-call"],["L","last time"],["N","notes, points & actions"],["Esc","leave a field so the letter keys work"],["?","this sheet"]];
  root.innerHTML=`<div class="modal-bg"><div class="modal" style="width:440px"><h2>Keys in a sync</h2>
    <div class="keysheet">${K.map(([k,d])=>`<div><kbd>${esc(k)}</kbd><span>${esc(d)}</span></div>`).join("")}</div>
    <div class="modal-foot"><button class="primary" id="ks-x">Done</button></div></div></div>`;
  const close=()=>root.innerHTML="";
  root.querySelector("#ks-x").onclick=close;
  root.querySelector(".modal-bg").onclick=e=>{if(e.target.classList.contains("modal-bg"))close();};
}
/* a change that can be taken back: the toast carries an Undo for a few seconds */
function toastUndo(m,undo){
  const t=document.getElementById("toast");t.textContent=m+"  ";
  const b=document.createElement("button");b.className="tundo";b.textContent="Undo";
  b.onclick=()=>{undo();t.className="toast";renderApp();};t.appendChild(b);
  t.className="toast show undo";clearTimeout(toast._t);toast._t=setTimeout(()=>t.className="toast",6000);
}
/* the previous call with this team, read back: what changed, what they said, what they
   read out, what was agreed */
function renderLastTime(host,s){
  const p=previousSync(s);
  if(!p){host.innerHTML=`<div class="capture-head"><div style="flex:1"><h2>Last time</h2></div><button class="sm" id="lt-back">← Queue</button></div>
    <p class="faint">This is the first closed sync for ${esc(teamOf(s.team).name)} — from the next one, this shows what happened in the call before.</p>`;
    host.querySelector("#lt-back").onclick=()=>syncSelect(null);return;}
  const said=[];state.tickets.forEach(t=>t.updates.forEach(u=>{if(u.syncId===p.id)said.push({t,u});}));
  said.sort((a,b)=>a.u.ts-b.u.ts);
  const prc=rollcallForSync(p.id),rc=rollcallForSync(s.id);
  const decs=state.decisions.filter(d=>d.syncId===p.id),ments=state.mentions.filter(m=>m.syncId===p.id);
  const FU={still:"still there",gone:"gone",ask:"asked"};
  host.innerHTML=`
    <div class="capture-head"><div style="flex:1;min-width:0">
        <div class="dh-id"><span class="mono" style="color:var(--accent2)">⟲ LAST TIME</span>${teamPill(p.team)}
          <span class="faint" style="font-weight:400">${fmtDate(p.date)}${p.startedAt&&p.closedAt?" · "+durTxt(p.closedAt-p.startedAt)+" call":""}</span></div>
        <h2>${esc(p.title||"Previous sync")}</h2>
        <div class="faint" style="font-size:12px;margin-top:4px">Where the last ${esc(teamOf(p.team).name)} call left off — so this one can pick it up.</div></div>
      <button class="sm" id="lt-open" title="Open that call's full record">That call ↗</button>
      <button class="sm" id="lt-back">← Queue</button></div>
    ${p.recap?`<div class="sec-title"><h3>What changed on the tickets</h3><div class="ln"></div></div>${recapHTML(p.recap)}`:""}
    <div class="sec-title"><h3>What they said</h3><div class="ln"></div><span class="faint" style="font-size:11px">${said.length}</span></div>
    ${said.length?said.map(x=>`<div class="ltsaid ${isOpen(x.t)&&x.t.team===s.team?"go":""}" data-ltgo="${esc(x.t.id)}">
        <div class="lt-top"><span class="mono">${esc(x.t.ticketId||"—")}</span><span class="lt-tt">${esc(x.t.title||"")}</span>
          ${isOpen(x.t)?"":`<span class="pill ${MY_STATUS[x.t.myStatus].cls}">${MY_STATUS[x.t.myStatus].label}</span>`}</div>
        <div class="lt-tx">${linkify(x.u.text)}</div></div>`).join("")
      :`<p class="faint" style="font-size:12px;margin:0">Nothing was captured on tickets in that call.</p>`}
    ${prc?`<div class="sec-title"><h3>What they read out</h3><div class="ln"></div></div>
      <p style="font-size:12.5px;margin:0 0 8px">${prc.recorded?rollSummaryLine(prc):`<span class="faint">numbers not confirmed in that call</span>`}</p>
      ${prc.incidents.items.length?`<div class="ltinc">${prc.incidents.items.map(it=>{const f=rc&&rc.incidents.followups[it.id];
        return `<div class="li"><span class="dotm"></span><span class="lt">${esc(it.text)}</span>${f?`<span class="warnchip ${f.state==="gone"?"good":f.state==="ask"?"info":""}">${FU[f.state]} today</span>`:""}${f&&f.answer?`<div class="la">↳ ${esc(f.answer)}</div>`:""}</div>`;}).join("")}
        <button class="sm" id="lt-roll" style="margin-top:8px">Follow them up in today's roll-call ›</button></div>`:""}
      ${prc.note?`<div class="rcl-note">They said: “${esc(prc.note)}”</div>`:""}`:""}
    ${p.points.length?`<div class="sec-title"><h3>Points raised</h3><div class="ln"></div></div>
      ${p.points.map(x=>`<div class="point" style="cursor:default"><span class="pby faint" style="border:0">${esc(x.by||"")}</span><div class="ptx">${linkify(x.text||"")}</div></div>`).join("")}`:""}
    ${p.actions.length?`<div class="sec-title"><h3>Action points</h3><div class="ln"></div></div>
      ${p.actions.map(a=>`<div class="ltact ${a.done?"done":""}"><span class="chk ${a.done?"done":""}"></span><span class="at">${esc(a.text||"(untitled)")}</span>
        <span class="faint">${esc(a.owner||"")}${a.due?" · "+fmtDate(a.due):""}</span>${a.resolution?`<div class="la">↳ ${esc(a.resolution)}</div>`:""}</div>`).join("")}`:""}
    ${decs.length?`<div class="sec-title"><h3>Decided</h3><div class="ln"></div></div>
      ${decs.map(d=>`<div class="decrow"><span class="dc-date">${fmtDate(d.date)}</span><div class="dc-t" style="flex:1">${linkify(d.text)}</div><span class="dc-by">${esc(d.by)}</span></div>`).join("")}`:""}
    ${ments.length?`<div class="sec-title"><h3>Incident notes from that call</h3><div class="ln"></div></div>
      ${ments.map(m=>`<div class="ltsaid go" data-ltmn="${esc(m.id)}"><div class="lt-top"><span class="lt-tt">${esc(m.title||"(unnamed incident)")}</span>
        <span class="pill ${MENTION_STATUS[m.status].cls}">${esc(MENTION_STATUS[m.status].label)}</span></div>
        ${m.what?`<div class="lt-tx">${esc(m.what)}</div>`:`<div class="lt-tx faint">no close-out yet</div>`}</div>`).join("")}`:""}`;
  host.querySelector("#lt-back").onclick=()=>syncSelect(null);
  host.querySelector("#lt-open").onclick=()=>openCall("sync",p.id);
  const lr=host.querySelector("#lt-roll");if(lr)lr.onclick=()=>syncSelect("rollcall");
  host.querySelectorAll("[data-ltgo]").forEach(el=>el.onclick=()=>{const t=ticketByRef(el.dataset.ltgo);
    if(t&&isOpen(t)&&t.team===s.team)syncSelect("ticket",t.id);else toast("That one isn't in today's queue — open it from Tickets");});
  host.querySelectorAll("[data-ltmn]").forEach(el=>el.onclick=()=>syncSelect("mention",el.dataset.ltmn));
}
/* ---- roll-call: what the incidents were, and last time's ---- */
function rollLinesHtml(r){
  const L=r.incidents,pl=lastRollLines(r.team,r),P=pl?pl.incidents.items:[];
  return `<div class="rc-lines">
    <div class="rcl-h"><b>What they were</b> <span class="faint">— one line each, only if there's time</span></div>
    ${L.items.map(it=>`<div class="rcl-row"><span class="rcl-dot ${it.from?"carried":""}" title="${it.from?"still there from last time":""}"></span>
      <input data-rcl="${esc(it.id)}" value="${esc(it.text)}" placeholder="what was it?"><button class="ghost sm" data-rcldel="${esc(it.id)}" title="Remove">✕</button></div>`).join("")}
    <div class="rcl-row add"><span class="rcl-dot add"></span><input id="rcl-new" placeholder="add one — e.g. SSO certificate expired on QA, renewed Tuesday  (Enter)"></div>
    ${P.length?`<div class="rcl-h prev"><b>Last time</b> · ${fmtDate(pl.date)} <span class="faint">— the count can stay the same while these change</span></div>
      ${P.map(it=>{const f=L.followups[it.id]||{};return `<div class="rcl-prev ${f.state||""}" data-rcp="${esc(it.id)}">
        <div class="rcl-pt"><span class="rcl-t">${esc(it.text)}</span>
          <span class="rcl-btns"><button class="sm ${f.state==="still"?"on":""}" data-fu="still" title="Still open — carried into this call's list">Still there</button><button class="sm ${f.state==="gone"?"on":""}" data-fu="gone" title="Closed since">Gone</button><button class="sm ${f.state==="ask"?"on":""}" data-fu="ask" title="Ask about it — and keep the answer">Ask</button></span></div>
        ${f.state==="ask"?`<input class="rcl-ans" data-fuans="${esc(it.id)}" value="${esc(f.answer||"")}" placeholder="what did they say about it?">`:""}
      </div>`;}).join("")}
      ${pl.note?`<div class="rcl-note">They said then: “${esc(pl.note)}”</div>`:""}`:""}
  </div>`;
}
function wireRollLines(host,r){
  const ln=r.incidents,pl=lastRollLines(r.team,r);
  /* lines are information, not the numbers — they never mark the roll-call recorded */
  const redraw=()=>{const el=host.querySelector(".rc-lines");if(!el)return;el.outerHTML=rollLinesHtml(r);wireRollLines(host,r);};
  host.querySelectorAll("[data-rcl]").forEach(i=>i.onchange=()=>{const it=ln.items.find(x=>x.id===i.dataset.rcl);if(!it)return;
    it.text=i.value.trim();if(!it.text)ln.items=ln.items.filter(x=>x!==it);touch(r);redraw();});
  host.querySelectorAll("[data-rcldel]").forEach(b=>b.onclick=()=>{const it=ln.items.find(x=>x.id===b.dataset.rcldel);if(!it)return;
    ln.items=ln.items.filter(x=>x!==it);
    if(it.from&&ln.followups[it.from]&&ln.followups[it.from].state==="still")delete ln.followups[it.from];
    touch(r);redraw();});
  const nw=host.querySelector("#rcl-new");
  if(nw)nw.onkeydown=e=>{if(e.key!=="Enter")return;e.preventDefault();const v=nw.value.trim();if(!v)return;
    ln.items.push({id:uid(),text:v,from:""});touch(r);redraw();const n2=host.querySelector("#rcl-new");if(n2)n2.focus();};
  host.querySelectorAll("[data-rcp]").forEach(row=>{const pid=row.dataset.rcp,pit=pl?pl.incidents.items.find(x=>x.id===pid):null;if(!pit)return;
    row.querySelectorAll("[data-fu]").forEach(b=>b.onclick=()=>{const st=b.dataset.fu,cur=ln.followups[pid]||{state:"",answer:""};
      if(cur.state==="still")ln.items=ln.items.filter(x=>x.from!==pid);
      if(cur.state===st){if(cur.answer)ln.followups[pid]={state:"ask",answer:cur.answer};else delete ln.followups[pid];
        if(st==="ask"&&!cur.answer)delete ln.followups[pid];}
      else{ln.followups[pid]={state:st,answer:cur.answer||""};
        if(st==="still")ln.items.push({id:uid(),text:pit.text,from:pid});}
      touch(r);redraw();if(st==="ask"){const a=host.querySelector(`[data-fuans="${pid}"]`);if(a)a.focus();}});
    const an=row.querySelector("[data-fuans]");
    if(an)an.onchange=()=>{ln.followups[pid]={state:"ask",answer:an.value.trim()};touch(r);};});
}
/* ---- Today's agenda: one ordered list for the day ---- */
function whenTxt(d){return d==null?"":d<0?(-d)+" d late":d===0?"today":d===1?"tomorrow":DAYS[new Date(addDays(d)+"T00:00:00").getDay()];}
function agendaItems(){
  const out=[];
  state.settings.teams.forEach(tm=>{
    const live=state.syncs.find(x=>!x.closed&&x.team===tm.id),nx=nextSyncFor(tm.id);
    if(!live&&!(nx&&nx.inDays===0))return;
    const q=queueFor(tm.id).length,ag=agendaFor(tm.id).length,mn=openMentions(tm.id).length,pl=lastRollLines(tm.id,null);
    out.push({k:"sync",ord:0,pen:"var(--pen-4)",when:live?"live":"today",text:(live?"Resume the ":"")+tm.name+" sync",
      sub:[q+" ticket"+(q===1?"":"s")+" to ask about",ag?ag+" point"+(ag===1?"":"s")+" to raise":"",
        mn?mn+" incident note"+(mn===1?"":"s")+" to chase":"",pl?pl.incidents.items.length+" incident"+(pl.incidents.items.length===1?"":"s")+" from last time":""].filter(Boolean).join(" · "),
      btn:live?"Resume":"Start",go:()=>live?openCall("sync",live.id):startSync(tm.id)});});
  openActionsAll().forEach(x=>{const a=x.action;if(!a.due)return;const d=daysUntil(a.due);if(d>2)return;
    const mine=!a.owner||/^me$/i.test(a.owner.trim());
    out.push({k:"act",ord:d<0?1:2,d,mine,pen:"var(--pen-5)",when:whenTxt(d),late:d<0,text:a.text||"(untitled action)",
      sub:(a.owner||"unassigned")+" · from "+(x.owner.title||"a call"),btn:"✓ Done",doneMsg:"Action point done",
      done:()=>{a.done=true;touch(x.owner);},undo:()=>{a.done=false;touch(x.owner);},go:()=>openCall(x.kind,x.owner.id)});});
  state.tickets.filter(isOpen).forEach(t=>{const lp=latestPromise(t);if(!lp||!lp.eta)return;const d=daysUntil(lp.eta);if(d<-7||d>1)return;
    let added=null;
    out.push({k:"eta",ord:d<0?1:3,d,pen:d<0?"var(--bad)":"var(--pen-2)",when:whenTxt(d),late:d<0,text:ticketLabel(t),
      sub:(d<0?"ETA passed":"they promised it "+(d===0?"today":"tomorrow"))+" · "+teamOf(t.team).name+(slipCount(t)?" · "+slipCount(t)+"× slipped":""),
      btn:"Ask next sync",doneMsg:"Parked for the next "+teamOf(t.team).name+" sync",
      done:()=>{added=normAgenda({team:t.team,ticketId:t.id,text:"ETA "+fmtDate(lp.eta)+" — where is "+(t.ticketId||t.title)+"?"});state.agenda.push(added);markDirty();},
      undo:()=>{state.agenda=state.agenda.filter(z=>z!==added);markDirty();},go:()=>gotoTicket(t.id)});});
  pendingApprovals().forEach(a=>{const t=a.ticketId?ticketByRef(a.ticketId):null;const d=daysUntil(a.requestedOn);
    out.push({k:"appr",ord:3,d:0,pen:"var(--watch)",when:d<0?(-d)+" d waiting":"waiting",text:(a.title||(t?ticketLabel(t):"(untitled)")),
      sub:APPROVAL_KINDS[a.kind].label+" · "+teamOf(a.team).name+" · your sign-off",btn:"Open",
      go:()=>{effortTeam=a.team;effortTab="approvals";view="effort";renderApp();}});});
  state.risks.filter(riskNeedsReview).forEach(r=>{const d=daysUntil(r.reviewOn);let prev="";
    out.push({k:"risk",ord:d<0?1:2,d,pen:"var(--watch)",when:whenTxt(d),late:d<0,text:r.title||"(untitled risk)",
      sub:"risk review · "+RISK_SEV[r.severity].label+(r.owner?" · "+r.owner:""),btn:"Reviewed",doneMsg:"Next review in "+RISK_REVIEW_DAYS+" days",
      done:()=>{prev=r.reviewOn;r.reviewOn=addDays(RISK_REVIEW_DAYS);touch(r);},undo:()=>{r.reviewOn=prev;touch(r);},
      go:()=>{activeRiskId=r.id;view="risks";renderApp();}});});
  state.settings.teams.flatMap(tm=>openMentions(tm.id)).forEach(m=>{const age=mentionAge(m);
    out.push({k:"note",ord:age>=MENTION_CHASE_DAYS?1:4,d:-age,pen:"var(--watch)",when:age+" d",late:age>=MENTION_CHASE_DAYS,
      text:m.title||"(unnamed incident)",sub:"incident note · "+teamOf(m.team).name+" · no close-out yet",btn:"Open",
      go:()=>{activeMentionId=m.id;knowledgeTab="mentions";view="knowledge";renderApp();}});});
  return out.sort((a,b)=>a.ord-b.ord||(a.d||0)-(b.d||0)||(b.mine?1:0)-(a.mine?1:0));
}
function agendaBlockHTML(items){
  return `<div class="ck-sech"><span class="ck-lbl">Agenda · ${items.length}</span></div>
  <div class="ck-unit ag-unit">${items.length?`<div class="agenda">${items.map((it,i)=>`<div class="ag-row" data-ag="${i}" style="--pen:${it.pen}"><i></i>
      <span class="ag-when ${it.late?"bad":""}">${esc(it.when)}</span>
      <span class="ag-main"><span class="ag-t">${esc(it.text)}</span>${it.sub?`<span class="ag-s">${esc(it.sub)}</span>`:""}</span>
      ${it.btn?`<button class="sm ${it.k==="sync"?"go":""}" data-agb="${i}">${esc(it.btn)}</button>`:""}</div>`).join("")}</div>`
    :`<div class="ck-empty">Nothing on today — no sync, and no actions, ETAs or reviews falling due.</div>`}</div>`;
}
function wireAgenda(host,items){
  host.querySelectorAll("[data-ag]").forEach(r=>r.onclick=e=>{if(e.target.closest("[data-agb]"))return;items[+r.dataset.ag].go();});
  host.querySelectorAll("[data-agb]").forEach(b=>b.onclick=e=>{e.stopPropagation();const it=items[+b.dataset.agb];
    if(it.done){it.done();renderApp();toastUndo(it.doneMsg||"Done",it.undo);}else it.go();});
}
/* ---- keys during a call ---- */
document.addEventListener("keydown",e=>{
  if(view!=="sync"||activeMeetingId||screenLocked||pendingEncrypted)return;
  const s=activeSync();if(!s)return;
  if(document.getElementById("modalRoot").firstElementChild)return;
  const tg=e.target,typing=/^(INPUT|TEXTAREA|SELECT)$/.test(tg.tagName)||tg.isContentEditable;
  if(e.altKey&&!e.ctrlKey&&(e.key==="ArrowDown"||e.key==="ArrowUp")){e.preventDefault();syncStep(s,e.key==="ArrowDown"?1:-1,false);return;}
  if(typing){if(e.key==="Escape"&&!e.defaultPrevented)tg.blur();return;}
  if(e.ctrlKey||e.metaKey||e.altKey)return;
  const click=sel=>{const b=document.querySelector(sel);if(b)b.click();};
  const focus=sel=>{const el=document.querySelector(sel);if(el)el.focus();};
  const map={j:()=>syncStep(s,1,true),k:()=>syncStep(s,-1,true),
    c:()=>{const b=document.querySelector("#cap-save");if(!b)return;if(b.dataset.covered==="1")toast("Already covered");else b.click();},
    u:()=>focus("#cap-said"),e:()=>focus("#cap-eta"),h:()=>click("#cap-hurdle"),a:()=>click("#cap-action"),
    r:()=>syncSelect("rollcall"),n:()=>syncSelect(null),
    l:()=>{if(previousSync(s))syncSelect("lasttime");else toast("No earlier sync with this team yet");},"?":()=>openSyncKeys()};
  const fn=map[e.key==="?"?"?":e.key.toLowerCase()];
  if(fn){e.preventDefault();fn();}
});
'''

RENDER_SYNC = r'''function renderSync(){
  const wrap=document.getElementById("syncwrap");
  if(!wrap){renderApp();return;}   /* not on the sync screen yet — draw the whole view */
  wrap.classList.remove("v2");capDraftSave=null;
  if(activeMeetingId){renderMeetingDetail(wrap);return;}
  const s=activeSync();
  if(!s){renderSyncPicker(wrap);return;}
  /* a call opened before the timer and the baseline existed starts both now */
  if(!s.closed&&!s.startedAt)s.startedAt=Date.now();
  if(!s.closed&&!s.baseline)s.baseline=syncBaseline(s.team);
  const O=queueOrder(s),pending=O.pending,done=O.done;
  const coveredIds=new Set(done.map(x=>x.t.id));
  const carried=carriedActions(s.team,s.id);
  const focus=syncFocusId?ticketByRef(syncFocusId):null;
  const prev=previousSync(s),rc=rollcallForSync(s.id);
  const pl=lastRollLines(s.team,rc||{id:"",date:s.date,createdAt:Date.now()});
  const asks=rc?Object.values(rc.incidents.followups).filter(f=>f.state==="ask"&&!f.answer).length:0;
  wrap.classList.add("v2");
  wrap.innerHTML=`${syncHeadHTML(s,O)}
    <div class="sbody">
    <div class="queue"><div class="queue-list" id="qlist">
        ${prev?`<div class="qrow lasttime ${syncPane==="lasttime"?"active":""}" data-qlast="1">
          <div class="qtop"><span class="ltbadge">⟲ last time</span><span style="margin-left:auto"></span><span class="qid">${fmtDate(prev.date)}</span></div>
          <div class="qtitle" style="white-space:normal">${esc(lastTimeLine(prev))}</div></div>`:""}
        <div class="qrow rollcall ${syncPane==="rollcall"?"active":""}" data-qroll="1">
          <div class="qtop"><span class="rcbadge">📊 roll-call</span><span style="margin-left:auto"></span>
            ${rc&&rc.recorded?`<span class="qtick">✓</span>`:`<span class="warnchip">not recorded</span>`}</div>
          <div class="qtitle">${rc&&rc.recorded?rollTotal(rc.demands)+" demands · "+rollTotal(rc.incidents)+" incidents":"Their numbers by status"}</div>
          <div class="qwhy"><span class="warnchip info">${(()=>{const p=lastRollcall(s.team,rc?rc.id:null);
              return p?"last call: "+rollTotal(p.demands)+" demands · "+rollTotal(p.incidents)+" incidents":"first one for this team";})()}</span>
            ${pl?`<span class="warnchip ${asks?"bad":""}">${pl.incidents.items.length} incident${pl.incidents.items.length===1?"":"s"} noted ${fmtDate(pl.date)}${asks?" · "+asks+" to ask":""}</span>`:""}</div>
        </div>
@@SECTIONS@@        ${pending.length?`<div class="qsec">Tickets (${pending.length})</div>`+O.blocks.map(b=>{
            if(b.kind==="t")return qrowHtml(b.x,false);
            return `<div class="qepic">
                <div class="qe-head" data-qepic="${esc(b.epic.id)}" title="Open all ${b.items.length} together">
                  <span class="qe-name">◆ ${esc(b.epic.name)}</span><span class="qe-n">${b.items.length}</span><span class="qe-go">open together →</span></div>
                <div class="qe-items">${b.items.map(x=>qrowHtml(x,false)).join("")}</div></div>`;}).join("")
          :`<div class="qsec">Tickets</div><p class="faint" style="font-size:12px;padding:6px 13px">${done.length?"All covered ✓":"No open tickets for this team."}</p>`}
        ${done.length?`<div class="qsec">Covered (${done.length})</div>`+done.map(x=>qrowHtml(x,true)).join(""):""}
    </div></div>
    <div class="capture" id="capture"></div></div>`;

  const on=(sel,fn)=>{const el=wrap.querySelector(sel);if(el)el.onclick=fn;};
  on("#sq-new",()=>openQuickAdd(s.team));
  on("#sq-ment",()=>syncSelect("mention",newMention(s.team,s.id).id));
  on("#sq-agenda",()=>openAgendaModal(s.team));
  on("#sq-notes",()=>syncSelect(null));
  on("#sq-keys",openSyncKeys);
  on("#sq-close",()=>closeSync(s));
  on("#sq-reopen",()=>{s.closed=false;s.closedAt=0;touch(s);renderSync();toast("Reopened");});
  on("#sh-next",()=>{syncKeyNav=false;stepQueue(s,syncFocusId,1);});
  on("#sh-title",e=>editInline(e.currentTarget,s.title,v=>{s.title=v;touch(s);renderSync();}));
  on("[data-qlast]",()=>syncSelect("lasttime"));
  on("[data-qroll]",()=>syncSelect("rollcall"));
  wrap.querySelectorAll("[data-qment]").forEach(r=>r.onclick=()=>syncSelect("mention",r.dataset.qment));
@@WIRING@@
  const gEpic=syncEpicId?epicById(syncEpicId):null;
  const cap=document.getElementById("capture");
  if(syncPane==="rollcall")renderRollcallCapture(cap,s);
  else if(syncPane==="lasttime")renderLastTime(cap,s);
  else if(syncPane==="mention")renderMentionCapture(cap,s,mentionById(syncMentionId));
  else if(gEpic)renderEpicCapture(cap,s,gEpic);
  else if(focus)renderCapture(cap,s,focus);
  else renderSyncNotes(cap,s);
  syncKeyNav=false;
  const cur=wrap.querySelector(".qrow.active");if(cur&&cur.scrollIntoView)cur.scrollIntoView({block:"nearest"});
}
'''

RENDER_CAPTURE = r'''function renderCapture(host,s,t){
  const cov=s.covered.find(c=>c.ticketId===t.id),isCov=!!(cov&&cov.done);
  const lastUp=t.updates.length?t.updates.slice().sort((a,b)=>b.ts-a.ts)[0]:null;
  const oh=openHurdles(t),ep=t.epicId?epicById(t.epicId):null;
  host.innerHTML=`
    <div class="capture-head">
      <div style="flex:1;min-width:0">
        <div class="dh-id"><span style="color:${teamColor(t.team)}">${esc(t.ticketId||"—")}</span>${teamPill(t.team)}
          ${ep?`<span class="faint" style="font-weight:400">◆ ${esc(ep.code||ep.name)}</span>`:""}
          ${isCov?`<span class="warnchip good">✓ covered</span>`:""}</div>
        <h2>${esc(t.title||"(untitled)")}</h2>
        <div class="faint" style="font-size:12px;margin-top:4px">${t.assignees.length?esc(t.assignees.map(personName).join(", "))+" · ":""}${esc(t.priority)} · last heard ${lastUp?fmtTs(lastUp.ts):"never"}</div>
      </div>
      <button class="sm" id="cap-open" title="Open the full ticket">Full ticket ↗</button>
    </div>
    ${etaLedgerHTML(t)}
    ${lastUp?`<div class="lastsaid"><div class="ls-h">Last time they said · ${fmtTs(lastUp.ts)}</div>${linkify(lastUp.text)}</div>`:""}
    ${oh.length?`<div class="caph">${oh.map(h=>`<div class="caph-row">
        <span class="kindtag">${esc(HURDLE_KINDS[h.kind].label)}</span>
        <span class="caph-t">${esc(h.text||"(no detail)")}<span class="faint"> · ${h.owner?esc(h.owner)+" · ":""}${Math.max(0,-daysUntil(h.raisedOn))} d open</span></span>
        <input data-hres="${esc(h.id)}" placeholder="cleared how? (optional)">
        <button class="sm" data-hclr="${esc(h.id)}">✓ Cleared</button></div>`).join("")}</div>`:""}
    ${statusDisagrees(t)?`<div class="disagree">⚠ They have this as “${esc(t.theirStatus)}”, you have it as <b>${MY_STATUS[t.myStatus].label}</b>.</div>`:""}
    <div id="cap-gates"></div>
    <div class="field"><label>What did they say? <span class="faint" style="text-transform:none;letter-spacing:0">— kept as you move between tickets · <kbd>U</kbd></span></label>
      <textarea id="cap-said" style="min-height:96px" placeholder="Type as they talk.  Ctrl+Enter marks it covered · Alt+↓ next ticket · Esc then ? for all keys">${esc(cov&&cov.draft||"")}</textarea></div>
    <div class="capgrid">
      <div class="field"><label>My status</label>${capStatusSeg(t)}</div>
      <div class="field"><label>Their status</label><input id="cap-their" value="${esc(t.theirStatus)}" list="dl-their2" placeholder="In Progress"><datalist id="dl-their2">${theirStatusOptions()}</datalist></div>
      <div class="field"><label>New ETA <kbd>E</kbd></label><input type="date" id="cap-eta"></div>
    </div>
    <div class="row cap-tools">
      <button id="cap-hurdle">🚧 Hurdle <kbd>H</kbd></button>
      <button id="cap-action">⚑ Action <kbd>A</kbd></button>
      <button id="cap-poc">👤 POC</button>
      <button id="cap-dec">🧭 Decision</button></div>
    <div class="capx" id="cap-hform" hidden>
      <select id="cap-hk">${Object.entries(HURDLE_KINDS).map(([k,v])=>`<option value="${k}">${esc(v.label)}</option>`).join("")}</select>
      <input id="cap-ht" placeholder="What's in the way?">
      <input id="cap-ho" placeholder="who's blocking" style="flex:0 0 150px">
      <button class="primary sm" id="cap-hadd">Add hurdle</button></div>
    <div class="capx" id="cap-aform" hidden>
      <input id="cap-at" placeholder="What needs doing?">
      <input id="cap-ao" value="Me" placeholder="owner" style="flex:0 0 120px">
      <input type="date" id="cap-ad" style="flex:0 0 150px">
      <button class="primary sm" id="cap-aadd">Add action</button></div>
    <div class="row cap-go">
      <button class="${isCov?"":"go"}" id="cap-save" data-covered="${isCov?1:0}" style="flex:1">${isCov?"↩ Reopen — mark not covered":"✓ Mark covered"}</button>
      <button id="cap-prev" title="Previous ticket (K)" style="flex:0 0 auto">‹ Prev</button>
      <button id="cap-next" title="Next ticket (J)" style="flex:0 0 auto">Skip ›</button>
    </div>
    <p class="faint" style="font-size:11.5px;margin-top:12px">Marking covered writes your note and any new ETA to the ticket, then moves to the next one. Moving between tickets never marks anything covered.</p>`;

  const q=x=>host.querySelector(x);
  renderGateStrip(q("#cap-gates"),t,()=>{draftSave();renderSync();});
  const said=q("#cap-said");
  if(!syncKeyNav)said.focus();
  capDraftSave=()=>draftSave();
  function draftSave(){
    let c=s.covered.find(x=>x.ticketId===t.id);
    if(!c){if(!said.value)return;c={ticketId:t.id,draft:"",done:false};s.covered.push(c);}
    if(c.draft!==said.value){c.draft=said.value;touch(s);}
  }
  said.onblur=draftSave;
  q("#cap-open").onclick=()=>{draftSave();gotoTicket(t.id);};
  host.querySelectorAll("[data-cs]").forEach(b=>b.onclick=()=>{if(b.dataset.cs===t.myStatus)return;draftSave();
    setStatus(t,b.dataset.cs);touch(t);renderSync();});
  q("#cap-their").onchange=e=>{t.theirStatus=e.target.value.trim();touch(t);};
  q("#cap-dec").onclick=()=>{draftSave();openDecisionModal({ticketId:t.id,syncId:s.id});};
  q("#cap-poc").onclick=()=>{draftSave();openContactModal(t);};
  /* hurdles and actions are added here, in the call — no detour to the full ticket */
  const toggle=(id,first)=>{const f=q(id),other=q(id==="#cap-hform"?"#cap-aform":"#cap-hform");other.hidden=true;
    f.hidden=!f.hidden;if(!f.hidden)q(first).focus();};
  q("#cap-hurdle").onclick=()=>toggle("#cap-hform","#cap-ht");
  q("#cap-action").onclick=()=>toggle("#cap-aform","#cap-at");
  const addH=()=>{const tx=q("#cap-ht").value.trim();if(!tx){toast("What's in the way?",true);return;}draftSave();
    t.hurdles.push(normHurdle({text:tx,kind:q("#cap-hk").value,owner:q("#cap-ho").value.trim(),syncId:s.id}));
    const was=t.myStatus;if(was!=="done"&&was!=="blocked")setStatus(t,"blocked");
    touch(t);renderSync();toast("Hurdle added"+(was!=="done"&&was!=="blocked"?" — status → Blocked":""));};
  q("#cap-hadd").onclick=addH;
  ["#cap-ht","#cap-ho"].forEach(id=>q(id).onkeydown=e=>{if(e.key==="Enter"){e.preventDefault();addH();}});
  const addA=()=>{const tx=q("#cap-at").value.trim();if(!tx){toast("What's the action?",true);return;}draftSave();
    const text=t.ticketId&&!tx.includes(t.ticketId)?t.ticketId+" — "+tx:tx;
    s.actions.push(normAction({text,owner:q("#cap-ao").value.trim(),due:q("#cap-ad").value,fromSyncId:s.id}));
    touch(s);renderSync();toast("Action added — it carries into later syncs until done");};
  q("#cap-aadd").onclick=addA;
  ["#cap-at","#cap-ao"].forEach(id=>q(id).onkeydown=e=>{if(e.key==="Enter"){e.preventDefault();addA();}});
  host.querySelectorAll("[data-hclr]").forEach(b=>b.onclick=()=>{draftSave();
    const h=t.hurdles.find(x=>x.id===b.dataset.hclr);if(!h)return;
    const how=host.querySelector(`[data-hres="${h.id}"]`);
    h.resolvedOn=todayStr();h.clearedSyncId=s.id;if(how&&how.value.trim())h.resolution=how.value.trim();
    let msg="Hurdle cleared";
    if(t.myStatus==="blocked"&&!openHurdles(t).length){setStatus(t,"progress");msg+=" — status → In progress";}
    touch(t);renderSync();toast(msg);});
  q("#cap-prev").onclick=()=>{draftSave();stepQueue(s,t.id,-1);};
  q("#cap-next").onclick=()=>{draftSave();stepQueue(s,t.id,1);};
  const save=()=>{
    const txt=said.value.trim();
    if(txt)t.updates.push(normUpdate({text:txt,syncId:s.id}));
    const eta=q("#cap-eta").value;
    if(eta)t.promises.push(normPromise({eta,givenOn:s.date,note:"given in "+(s.title||"sync"),syncId:s.id}));
    let c=s.covered.find(x=>x.ticketId===t.id);
    if(!c){c={ticketId:t.id,draft:"",done:true};s.covered.push(c);}
    c.done=true;c.draft="";said.value="";
    touch(t);touch(s);
    toast("Captured on "+(t.ticketId||"ticket")+(eta?" · ETA "+fmtDate(eta):""));
    stepQueue(s,t.id,1);
  };
  q("#cap-save").onclick=()=>{
    const c=s.covered.find(x=>x.ticketId===t.id);
    if(c&&c.done){c.done=false;touch(s);toast("Reopened — back in the queue");renderSync();}
    else save();
  };
  said.onkeydown=e=>{if(e.key==="Enter"&&e.ctrlKey){e.preventDefault();
    const c=s.covered.find(x=>x.ticketId===t.id);if(c&&c.done)return;save();}};
}
'''

CLOSE_SYNC = r'''function closeSync(s){
  const O=queueOrder(s),missed=O.pending;
  const open=s.actions.filter(a=>!a.done).length;
  /* notes typed but never marked covered still go to their ticket — discussed, just
     not closed out, so nothing typed is lost */
  const drafts=s.covered.filter(c=>!c.done&&c.draft&&c.draft.trim());
  /* an untouched roll-call is last week's numbers wearing this week's date — it goes,
     unless it holds incident lines, which are kept (still out of the trend) */
  const rc=rollcallForSync(s.id),rcLines=rc&&(rc.incidents.items.length||Object.keys(rc.incidents.followups).length);
  const asks=rc?Object.values(rc.incidents.followups).filter(f=>f.state==="ask"&&!f.answer).length:0;
  const nOm=openMentions(s.team).length,R=syncRecap(s);
  const root=document.getElementById("modalRoot");
  const pl=n=>n===1?"":"s";
  root.innerHTML=`<div class="modal-bg"><div class="modal" style="width:580px">
    <h2>Close ${esc(s.title||"this sync")}</h2>
    <p class="faint" style="font-size:12px;margin-top:-8px">${syncElapsed(s)} on the call · ${O.done.length} of ${O.done.length+missed.length} tickets covered</p>
    <div class="sec-title"><h3>What changed in this call</h3><div class="ln"></div></div>
    ${recapHTML(R)}
    <div class="sec-title" style="margin-top:16px"><h3>Carries to the next call</h3><div class="ln"></div></div>
    <ul class="closelist">
      ${missed.length?`<li><b>${missed.length}</b> ticket${pl(missed.length)} not covered — top of the queue next time${missed.length<=6?`: <span class="mono">${missed.map(x=>esc(x.t.ticketId||clip(x.t.title,20))).join(", ")}</span>`:""}</li>`:""}
      ${open?`<li><b>${open}</b> action point${pl(open)} still open — they carry over</li>`:""}
      ${nOm?`<li><b>${nOm}</b> incident note${pl(nOm)} with no close-out — asked about again</li>`:""}
      ${asks?`<li><b>${asks}</b> incident${pl(asks)} you meant to ask about, with no answer noted</li>`:""}
      ${drafts.length?`<li><b>${drafts.length}</b> half-typed note${pl(drafts.length)} — saved to ${drafts.length===1?"its ticket":"their tickets"}</li>`:""}
      ${rc&&!rc.recorded?`<li>The roll-call numbers weren't confirmed — ${rcLines?"they stay out of the trend; the incident lines are kept":"the draft is discarded"}</li>`:""}
      ${!missed.length&&!open&&!nOm&&!asks&&!drafts.length&&!(rc&&!rc.recorded)?`<li>Nothing — a clean close.</li>`:""}
    </ul>
    <p class="faint" style="font-size:11.5px">The next ${esc(teamOf(s.team).name)} sync opens with this as <b>Last time</b>.</p>
    <div class="modal-foot"><button class="ghost" id="cs-x">Keep going</button><button class="go" id="cs-ok">Close sync</button></div></div></div>`;
  root.querySelector("#cs-x").onclick=()=>root.innerHTML="";
  root.querySelector("#cs-ok").onclick=()=>{root.innerHTML="";
    if(rc&&!rc.recorded&&!rcLines)state.rollcalls=state.rollcalls.filter(x=>x.id!==rc.id);
    drafts.forEach(c=>{const t=ticketByRef(c.ticketId);
      if(t){t.updates.push(normUpdate({text:c.draft.trim(),syncId:s.id}));c.draft="";touch(t);}});
    const R2=syncRecap(s);
    /* reopened and closed again: what the first close saw from the baseline stays */
    if(!s.baseline&&s.recap){R2.status=s.recap.status;R2.closed=s.recap.closed;R2.added=s.recap.added;}
    s.recap=R2;s.baseline=null;s.closed=true;s.closedAt=Date.now();
    touch(s);activeSyncId=null;syncSelectReset();renderSync();
    toast("Sync closed — the next one opens with what changed");};
}
'''

SYNC_CSS = r'''
  /* ---------------- sync v2: the call as an instrument ---------------- */
  .syncwrap.v2{flex-direction:column}
  .sbody{display:flex;flex:1;min-height:0}
  .shead{display:flex;flex-wrap:wrap;align-items:stretch;border-bottom:1px solid var(--rule);background:var(--paper);position:relative;z-index:2}
  .shead>div{padding:9px 16px 10px;border-right:1px solid var(--rule);min-width:0;display:flex;flex-direction:column;justify-content:center;gap:5px}
  .shead .k{font-family:var(--label);font-size:8.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--ink-3);font-weight:600;white-space:nowrap;display:flex;align-items:center;gap:6px}
  .shead .v{font-family:var(--mono);font-size:15px;color:var(--ink);font-variant-numeric:tabular-nums;white-space:nowrap}
  .shead .v small{font-size:10px;color:var(--ink-3);margin-left:6px}
  .sh-l{flex:1 1 420px}
  .sh-btns{display:flex;flex-wrap:wrap;gap:5px;margin-top:1px}
  :root[data-theme="bench"] .sh-btns button{padding:2px 9px;font-size:11px}
  .sh-no{display:flex;align-items:center;gap:8px;font-family:var(--mono);font-size:10.5px;color:var(--ink-3)}
  .sh-live{display:inline-flex;align-items:center;gap:6px;color:var(--bad);font-weight:600;text-transform:uppercase;letter-spacing:.16em;font-size:9px;font-family:var(--label)}
  .sh-live i{width:7px;height:7px;border-radius:50%;background:var(--bad);animation:shpulse 1.8s ease-in-out infinite}
  @keyframes shpulse{0%,100%{box-shadow:0 0 0 0 color-mix(in srgb,var(--bad) 50%,transparent)}60%{box-shadow:0 0 0 6px transparent}}
  .sh-state{color:var(--ink-3);text-transform:uppercase;letter-spacing:.16em;font-size:9px;font-family:var(--label)}
  .sh-title{font-size:16px;font-weight:600;color:var(--ink);letter-spacing:-.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:text}
  .sh-cov{flex:0 1 220px}
  .sh-dots{display:flex;flex-wrap:wrap;gap:3px;max-width:210px}
  .sh-dots i{width:8px;height:8px;border-radius:50%;border:1px solid var(--ink-4);box-sizing:border-box;transition:background .3s,border-color .3s}
  .sh-dots i.on{background:var(--good);border-color:var(--good)}
  .sh-dots i.cur{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 35%,transparent)}
  .sh-cap{flex:0 1 270px}
  .sh-cap .v{font-family:var(--sans);font-size:11.5px;white-space:normal;display:flex;flex-wrap:wrap;gap:3px 11px}
  .capc{color:var(--ink-4)} .capc b{font-family:var(--mono);font-weight:600}
  .capc.on{color:var(--ink-2)} .capc.on b{color:var(--ink)}
  .sh-time .v{font-size:20px;letter-spacing:-.02em}
  .sh-next{flex:0 1 220px;border-right:0!important}
  :root[data-theme="bench"] .sh-nextbtn{text-align:left;font-size:11.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:230px;padding:4px 9px}
  kbd{font-family:var(--mono);font-size:9px;border:1px solid var(--rule-strong);border-bottom-width:2px;border-radius:3px;padding:0 4px;color:var(--ink-3);background:var(--paper);letter-spacing:0;text-transform:none;font-weight:500;line-height:1.5}
  button kbd{margin-left:4px}
  .qrow.lasttime{border-left-color:var(--accent2)}
  .ltbadge{font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent2);font-weight:600}
  /* capture */
  .etaled{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 12px;margin:12px 0 0;padding:7px 11px;border:1px solid var(--rule);border-left:2px solid var(--pen-2);border-radius:3px;font-size:12px;color:var(--ink-2)}
  .etaled .k{font-family:var(--label);font-size:8.5px;letter-spacing:.18em;font-weight:600;color:var(--ink-3)}
  .etaled b{font-family:var(--mono);font-size:13.5px;color:var(--ink)}
  .etaled .ed{font-family:var(--mono);font-size:11px}
  .etaled .eh{font-family:var(--mono);font-size:10.5px;color:var(--ink-3)}
  .etaled .es{font-size:10.5px;color:var(--watch);font-weight:600}
  .etaled.warn{border-left-color:var(--watch)} .etaled.bad{border-left-color:var(--bad)} .etaled.bad .ed{color:var(--bad)}
  .etaled.none{border-left-color:var(--ink-4);color:var(--ink-3)}
  .caph{margin:0 0 14px;border:1px solid color-mix(in srgb,var(--watch) 35%,var(--rule));border-radius:3px}
  .caph-row{display:flex;flex-wrap:wrap;align-items:center;gap:8px;padding:7px 10px;border-top:1px dotted var(--rule-strong);font-size:12.5px}
  .caph-row:first-child{border-top:0}
  .caph-t{flex:1 1 220px;min-width:0}
  .caph-row input{flex:0 1 190px;font-size:12px;padding:3px 8px}
  .capgrid{display:grid;grid-template-columns:auto minmax(140px,1fr) 170px;gap:12px;align-items:end}
  .capgrid .seg{height:30px}
  .cap-tools{margin:2px 0 10px;gap:6px}
  .capx{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:0 0 12px;padding:9px 10px;border:1px dashed var(--rule-strong);border-radius:3px;background:var(--paper-2)}
  .capx[hidden]{display:none}
  .capx input,.capx select{font-size:12.5px;padding:5px 8px;flex:1 1 200px}
  .capx select{flex:0 0 170px}
  .cap-go{margin-top:6px}
  @media (max-width:1180px){.capgrid{grid-template-columns:1fr 1fr}.capgrid .field:first-child{grid-column:1/-1}}
  /* last time */
  .recap{border:1px solid var(--rule);border-radius:3px}
  .rcp{display:grid;grid-template-columns:62px 1fr;gap:10px;padding:6px 10px;border-top:1px dotted var(--rule-strong);font-size:12.5px;align-items:baseline}
  .rcp:first-child{border-top:0}
  .rcp .rk{font-family:var(--label);font-size:8.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3);font-weight:600}
  .rcp.good .rk{color:var(--good)} .rcp.bad .rk{color:var(--bad)} .rcp.warn .rk{color:var(--watch)}
  .rcp .mono{font-family:var(--mono);font-size:11px;color:var(--accent)}
  .ltsaid{padding:8px 4px;border-top:1px dotted var(--rule-strong)}
  .ltsaid.go{cursor:pointer} .ltsaid.go:hover{background:var(--paper-2)}
  .lt-top{display:flex;align-items:baseline;gap:9px}
  .lt-top .mono{font-family:var(--mono);font-size:11px;color:var(--accent);flex:none}
  .lt-tt{font-size:12.5px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;min-width:0}
  .lt-tx{font-size:12.5px;color:var(--ink-2);margin-top:3px;line-height:1.5;white-space:pre-wrap}
  .ltinc .li{display:flex;flex-wrap:wrap;align-items:center;gap:8px;padding:5px 0;font-size:12.5px}
  .ltinc .dotm{width:6px;height:6px;border-radius:50%;background:var(--watch);flex:none}
  .ltinc .lt{flex:1;min-width:0}
  .la{flex-basis:100%;font-size:12px;color:var(--ink-2);padding-left:14px}
  .ltact{display:flex;flex-wrap:wrap;align-items:center;gap:9px;padding:6px 4px;border-top:1px dotted var(--rule-strong);font-size:12.5px}
  .ltact .at{flex:1;min-width:0} .ltact.done .at{color:var(--ink-3);text-decoration:line-through}
  .ltact .chk{width:12px;height:12px;border-radius:50%;border:1px solid var(--ink-3);flex:none}
  .ltact .chk.done{background:var(--good);border-color:var(--good)}
  /* roll-call: what the incidents were */
  .rc-lines{margin-top:12px;padding-top:12px;border-top:1px solid var(--rule)}
  .rcl-h{font-size:12px;color:var(--ink-2);margin:0 0 6px}
  .rcl-h b{font-family:var(--label);font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:var(--ink);font-weight:600}
  .rcl-h.prev{margin-top:14px}
  .rcl-row{display:flex;align-items:center;gap:8px;padding:2px 0}
  .rcl-row input{flex:1;font-size:12.5px;padding:4px 8px}
  .rcl-row.add input{border-style:dashed}
  .rcl-dot{width:7px;height:7px;border-radius:50%;background:var(--watch);flex:none}
  .rcl-dot.carried{background:transparent;border:1.5px solid var(--watch)}
  .rcl-dot.add{background:transparent;border:1px dashed var(--ink-4)}
  .rcl-prev{padding:6px 8px;border:1px solid var(--rule);border-left:2px solid var(--ink-4);border-radius:3px;margin-bottom:5px}
  .rcl-prev.still{border-left-color:var(--watch)} .rcl-prev.gone{border-left-color:var(--good)} .rcl-prev.gone .rcl-t{color:var(--ink-3);text-decoration:line-through}
  .rcl-prev.ask{border-left-color:var(--accent)}
  .rcl-pt{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
  .rcl-t{flex:1 1 220px;font-size:12.5px;color:var(--ink)}
  .rcl-btns{display:flex;gap:4px}
  :root[data-theme="bench"] .rcl-btns button{padding:2px 8px;font-size:11px}
  :root[data-theme="bench"] .rcl-btns button.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
  .rcl-ans{width:100%;margin-top:6px;font-size:12.5px;padding:4px 8px}
  .rcl-note{font-size:12px;color:var(--ink-2);margin-top:8px;font-style:italic}
  /* close sheet, keys sheet */
  .closelist{margin:0 0 10px;padding-left:18px;font-size:12.5px;line-height:1.7;color:var(--ink-2)}
  .closelist b{font-family:var(--mono);color:var(--ink)}
  .keysheet{display:grid;gap:6px;margin:4px 0 6px}
  .keysheet div{display:grid;grid-template-columns:120px 1fr;gap:10px;align-items:center;font-size:12.5px}
  .keysheet kbd{font-size:10.5px;padding:1px 6px;justify-self:start}
  /* toast with Undo */
  .toast.undo{pointer-events:auto}
  .tundo{margin-left:10px;background:transparent!important;color:inherit!important;border:1px solid currentColor!important;padding:2px 9px!important;font-size:11px!important}
  /* Today: the agenda */
  .ag-unit{padding:4px 15px}
  .ag-row{display:grid;grid-template-columns:10px 84px minmax(0,1fr) auto;gap:12px;align-items:center;padding:9px 0;border-top:1px dotted var(--rule-strong);cursor:pointer}
  .ag-row:first-child{border-top:0}
  .ag-row:hover .ag-t{color:var(--pen)}
  .ag-row>i{width:8px;height:8px;border-radius:50%;background:var(--pen)}
  .ag-when{font-family:var(--mono);font-size:11px;color:var(--ink-3);white-space:nowrap}
  .ag-when.bad{color:var(--bad)}
  .ag-main{display:flex;flex-direction:column;min-width:0}
  .ag-t{font-size:13px;color:var(--ink);font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transition:color .2s}
  .ag-s{font-size:11px;color:var(--ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'''


if __name__ == "__main__":
    P = sys.argv[1]
    s = io.open(P, encoding="utf-8").read()
    s = patch(s)
    io.open(P, "w", encoding="utf-8", newline="").write(s)
    print("applied to", P, len(s))
