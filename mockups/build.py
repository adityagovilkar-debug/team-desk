"""Builds the two mockup pages from the CURRENT TeamDesk.html:

    sync-rehaul.html   the app with mockups/sync-rehaul.patch.py applied
    sync-current.html  the app as it is today, for comparison

Both boot into invented data (mockdata.js), keep their browser storage under their own
names (tdmockup.*), and never write to a file — so opening them can't touch real data.

    python mockups/build.py
"""
import io, os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
src = io.open(os.path.join(ROOT, "TeamDesk.html"), encoding="utf-8").read()
spec = importlib.util.spec_from_file_location("sync_patch", os.path.join(HERE, "sync-rehaul.patch.py"))
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)

PANEL_CSS = """<style>
  .mockpanel{position:fixed;right:14px;bottom:34px;z-index:300;width:330px;max-height:62vh;overflow:auto;background:var(--paper);
    border:1px solid var(--rule-strong);border-radius:4px;box-shadow:0 6px 24px rgba(0,0,0,.18);font-size:12px;line-height:1.5;color:var(--ink-2)}
  .mockpanel h4{margin:0;padding:9px 12px;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--rule);font-size:11px;
    letter-spacing:.14em;text-transform:uppercase;color:var(--ink)}
  .mockpanel h4 span{font-weight:400;letter-spacing:0;text-transform:none;color:var(--ink-3)}
  .mockpanel h4 button{margin-left:auto;padding:1px 8px}
  .mockpanel ol{margin:8px 0;padding:0 14px 0 30px}.mockpanel li{margin-bottom:6px}
  .mockpanel p{margin:6px 12px 10px}.mockpanel b{color:var(--ink)}
  .mockpanel.min ol,.mockpanel.min p{display:none}
</style>"""

NOTES_REHAUL = PANEL_CSS + """<div class="mockpanel" id="mockpanel"><h4>Mockup · sync rehaul <span>invented data · nothing saved</span><button id="mpx">–</button></h4>
<ol>
<li><b>The header</b> is the call at a glance: tickets covered as dots, what you've captured, time on the call, and <b>Next up</b>.</li>
<li><b>Keys</b> — <kbd>J</kbd>/<kbd>K</kbd> next/previous, <kbd>Ctrl+Enter</kbd> covered, <kbd>E</kbd> ETA, <kbd>H</kbd> hurdle, <kbd>A</kbd> action, <kbd>L</kbd> last time, <kbd>?</kbd> all. While typing: <kbd>Alt+↓</kbd>/<kbd>Alt+↑</kbd>.</li>
<li><b>⟲ Last time</b> (top of the queue): what changed and what they said in the previous Portal call, its actions and decisions.</li>
<li><b>Roll-call → Incidents</b>: note what the incidents were, one line each; last call's lines sit below with <b>Still there · Gone · Ask</b> (Ask keeps their answer).</li>
<li><b>On a ticket</b>: the ETA history, clear a hurdle in place, add a hurdle or an action without leaving the call, status as a segment.</li>
<li><b>Close sync</b>: a sheet with what changed and what carries over — it becomes the next call's <b>Last time</b>.</li>
<li><b>Today</b> (top of the rail): an <b>Agenda</b> under the greeting — today's sync and what's waiting in it, actions and ETAs due, approvals, reviews. Ticking one offers Undo.</li>
</ol>
<p>Compare with <a href="sync-current.html">the current sync screen</a>. Reload to start over.</p></div>
<script>(function(){var p=document.getElementById("mockpanel");document.getElementById("mpx").onclick=function(){p.classList.toggle("min");this.textContent=p.classList.contains("min")?"+":"–";};})();</script>"""

NOTES_CURRENT = PANEL_CSS + """<div class="mockpanel" id="mockpanel"><h4>Current sync screen <span>for comparison</span><button id="mpx">–</button></h4>
<p>This is Team Desk as it is today, on the same invented data. The proposal is <a href="sync-rehaul.html">the sync rehaul</a>.</p></div>
<script>(function(){var p=document.getElementById("mockpanel");document.getElementById("mpx").onclick=function(){p.classList.toggle("min");this.textContent=p.classList.contains("min")?"+":"–";};})();</script>"""

BOOT = """async function mockBoot(){await initStore();state=migrate(window.MOCK());dirty=false;
  const live=state.syncs.find(x=>!x.closed&&x.team==="portal");if(live){view="sync";activeSyncId=live.id;}
  renderApp();}
window.MOCKUP=true;mockBoot();
"""

def rep(s, old, new):
    assert s.count(old) == 1, (old[:60], s.count(old))
    return s.replace(old, new)

def sandbox(html, notes, title):
    n = html.count('"teamdesk')
    assert n >= 10, n
    html = html.replace('"teamdesk', '"tdmockup')          # every storage key, the IndexedDB name, the tab channel
    html = rep(html, 'function writeFile(opts){',
               'function writeFile(opts){if(window.MOCKUP){toast("Mockup — nothing is written to a file");return Promise.resolve(false);}')
    html = rep(html, 'window.addEventListener("beforeunload",e=>{', 'window.addEventListener("beforeunload",e=>{if(window.MOCKUP)return;')
    html = rep(html, '\nboot();\n', '\n' + BOOT)
    html = rep(html, '<div id="modalRoot"></div>', '<div id="modalRoot"></div>\n<script src="mockdata.js"></script>')
    a = html.index("<title>"); b = html.index("</title>", a)
    html = html[:a] + "<title>" + title + html[b:]
    html = rep(html, "</body>", notes + "\n</body>")
    return html

io.open(os.path.join(HERE, "sync-current.html"), "w", encoding="utf-8", newline="").write(
    sandbox(src, NOTES_CURRENT, "Team Desk · current sync (mockup)"))
io.open(os.path.join(HERE, "sync-rehaul.html"), "w", encoding="utf-8", newline="").write(
    sandbox(P.patch(src), NOTES_REHAUL, "Team Desk · sync rehaul (mockup)"))
print("built sync-current.html and sync-rehaul.html")
