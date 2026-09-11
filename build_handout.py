#!/usr/bin/env python3
"""Build HANDOUT.html (and a print-clean PDF source) from HANDOUT.md."""
import re, io, base64, markdown

md = open('HANDOUT.md').read()
html_body = markdown.markdown(md, extensions=['tables', 'fenced_code', 'sane_lists'])

# embed the display face so the doc survives with no network
try:
    from fontTools.ttLib import TTFont
    f = TTFont('/Users/maanav/Documents/site2026/assets/RozhaOne-Regular.ttf')
    f.flavor = 'woff2'
    buf = io.BytesIO(); f.save(buf)
    ROZHA, FMT = base64.b64encode(buf.getvalue()).decode(), 'woff2'
except Exception:
    ROZHA = base64.b64encode(open('/Users/maanav/Documents/site2026/assets/RozhaOne-Regular.ttf','rb').read()).decode()
    FMT = 'truetype'

# ---- slugs + anchors on every heading, collected for the contents rail ----
toc = []
def slugify(t):
    s = re.sub(r'<[^>]+>', '', t)
    s = re.sub(r'[^\w\s-]', '', s).strip().lower()
    return re.sub(r'[\s_]+', '-', s)

def anchor(m):
    lvl, attrs, text = m.group(1), m.group(2), m.group(3)
    sid = slugify(text)
    if lvl in ('1','2'):
        toc.append((lvl, sid, re.sub(r'<[^>]+>', '', text)))
    return (f'<h{lvl} id="{sid}"{attrs}>{text}'
            f'<a class="anchor" href="#{sid}" aria-label="Link to this section">#</a></h{lvl}>')

html_body = re.sub(r'<h([1-3])([^>]*)>(.*?)</h\1>', anchor, html_body, flags=re.S)

# ---- checklists become real checkboxes ----
cb_i = [0]
def checkbox(m):
    cb_i[0] += 1
    return (f'<li class="task"><input type="checkbox" id="t{cb_i[0]}" data-k="t{cb_i[0]}">'
            f'<label for="t{cb_i[0]}">')
html_body = re.sub(r'<li>\[ \] ', checkbox, html_body)
# close the label we opened
parts, out, depth = html_body.split('<li class="task">'), [], 0
if len(parts) > 1:
    rebuilt = parts[0]
    for p in parts[1:]:
        end = p.find('</li>')
        rebuilt += '<li class="task">' + p[:end] + '</label></li>' + p[end+5:]
    html_body = rebuilt

toc_html = '\n'.join(
    f'<a class="toc-l{lvl}" href="#{sid}">{txt}</a>' for lvl, sid, txt in toc)

CSS = r"""
@font-face{font-family:"Rozha One";font-style:normal;font-weight:400;font-display:block;
 src:url(data:font/__FMT__;base64,__ROZHA__) format("__FMT__")}
:root{
 --ink:#0e1220;--ink-soft:#2f3854;--ink-dim:#6b7089;
 --paper:#ece2cc;--paper-2:#e4d9c0;--rule:#c9bb9c;--rule-up:#b3a487;
 --peacock:#1a4f4b;--madder:#8f3b2e;--turmeric:#8a5a12;
 --rail:20rem;
}
*{box-sizing:border-box}
html{background:var(--paper);-webkit-print-color-adjust:exact;print-color-adjust:exact;scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);
 font-family:"Newsreader",Georgia,"Times New Roman",serif;font-size:11.6pt;line-height:1.58}
.sheet{max-width:52rem;margin:0 auto;padding:3.4rem 3rem 6rem}

/* contents rail */
.rail{position:fixed;top:0;left:0;width:var(--rail);height:100vh;overflow-y:auto;
 padding:2.2rem 1.3rem 3rem 1.6rem;background:var(--paper-2);border-right:1px solid var(--rule);
 font-size:9.4pt;line-height:1.35;z-index:50}
.rail .rail-title{font-family:"JetBrains Mono",monospace;font-size:7.6pt;letter-spacing:.18em;
 text-transform:uppercase;color:var(--turmeric);font-weight:600;margin-bottom:1rem;display:block}
.rail a{display:block;color:var(--ink-soft);text-decoration:none;border:0;padding:.3rem .5rem;
 border-radius:4px;border-left:2px solid transparent}
.rail a:hover{background:rgba(14,18,32,.05);color:var(--ink)}
.rail a.toc-l1{font-family:"Rozha One",Georgia,serif;font-size:11.4pt;color:var(--ink);
 margin-top:1rem;padding-top:.55rem;border-top:1px solid var(--rule)}
.rail a.toc-l1:first-of-type{margin-top:0;border-top:0;padding-top:0}
.rail a.toc-l2{padding-left:.75rem}
.rail a.active{color:var(--madder);border-left-color:var(--madder);background:rgba(143,59,46,.07)}
@media(min-width:1180px){.sheet{margin-left:calc(var(--rail) + 3rem);margin-right:3rem;max-width:52rem}}
@media(max-width:1179px){.rail{display:none}}

h1,h2,h3,h4{font-family:"Rozha One",Georgia,serif;font-weight:400;line-height:1.12;letter-spacing:-.004em;
 position:relative;scroll-margin-top:1.5rem}
h1{font-size:30pt;margin:0 0 .35rem;padding-bottom:.7rem;border-bottom:2px solid var(--madder)}
h1+p{font-size:12.4pt;color:var(--ink-soft);margin-top:.9rem}
h2{font-size:19pt;margin:2.6rem 0 .9rem;padding-top:1.1rem;border-top:1px solid var(--rule)}
h3{font-size:14pt;margin:1.9rem 0 .55rem;color:var(--peacock)}
h4{font-size:11.8pt;margin:1.3rem 0 .4rem;color:var(--ink-soft)}
.anchor{position:absolute;left:-1.35rem;top:.12em;opacity:0;color:var(--rule-up);border:0;
 font-family:"JetBrains Mono",monospace;font-size:.55em;text-decoration:none;transition:opacity .15s}
h1:hover .anchor,h2:hover .anchor,h3:hover .anchor{opacity:1}
.anchor:hover{color:var(--madder)}

hr{border:0;height:1px;background:var(--rule-up);margin:2.6rem 0}
p{margin:.62rem 0}
a{color:var(--peacock);text-decoration:none;border-bottom:1px solid rgba(26,79,75,.32)}
a:hover{color:var(--madder);border-bottom-color:rgba(143,59,46,.5)}
strong{font-weight:600;color:var(--ink)}
code{font-family:"JetBrains Mono",ui-monospace,"SF Mono",Menlo,monospace;font-size:.86em;
 background:rgba(14,18,32,.055);border:1px solid rgba(14,18,32,.1);border-radius:3px;padding:.06em .34em}

/* code blocks with a copy button */
.codewrap{position:relative;margin:1rem 0}
pre{background:#12172a;color:#ece2cc;border-radius:7px;padding:.95rem 1.1rem;margin:0;
 font-size:9.7pt;line-height:1.62;page-break-inside:avoid;white-space:pre-wrap;word-break:break-word}
pre code{background:none;border:0;padding:0;color:inherit;font-size:inherit}
.copy{position:absolute;top:.5rem;right:.5rem;font-family:"JetBrains Mono",monospace;font-size:7.6pt;
 letter-spacing:.1em;text-transform:uppercase;color:#b5ac97;background:rgba(236,226,204,.08);
 border:1px solid rgba(236,226,204,.22);border-radius:4px;padding:.3rem .55rem;cursor:pointer;
 opacity:0;transition:opacity .15s,background .15s,color .15s}
.codewrap:hover .copy{opacity:1}
.copy:hover{background:rgba(217,164,65,.2);color:#ece2cc;border-color:rgba(217,164,65,.5)}
.copy.done{opacity:1;background:rgba(63,143,135,.25);border-color:rgba(63,143,135,.6);color:#cfe6e2}

table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:10.3pt;page-break-inside:avoid}
th{text-align:left;font-family:"JetBrains Mono",monospace;font-size:8pt;letter-spacing:.1em;
 text-transform:uppercase;color:var(--turmeric);font-weight:600;border-bottom:1.5px solid var(--rule-up);
 padding:.4rem .7rem .4rem 0;vertical-align:bottom}
td{border-bottom:1px solid var(--rule);padding:.52rem .7rem .52rem 0;vertical-align:top;color:var(--ink-soft)}
td strong{color:var(--ink)}
td:last-child,th:last-child{padding-right:0}
tbody tr:hover td{background:rgba(14,18,32,.028)}

blockquote{margin:1.1rem 0;padding:.75rem 0 .75rem 1.05rem;border-left:3px solid var(--madder);
 color:var(--ink-soft);page-break-inside:avoid}
blockquote p{margin:.3rem 0}
ul,ol{padding-left:1.25rem;margin:.62rem 0}
li{margin:.3rem 0}

/* tickable checklists */
li.task{list-style:none;margin-left:-1.25rem;display:flex;gap:.6rem;align-items:flex-start;
 padding:.28rem .5rem;border-radius:5px;transition:background .15s}
li.task:hover{background:rgba(14,18,32,.04)}
li.task input{appearance:none;-webkit-appearance:none;flex:0 0 auto;width:1.02em;height:1.02em;
 margin-top:.28em;border:1.5px solid var(--rule-up);border-radius:3.5px;background:transparent;
 cursor:pointer;position:relative;transition:background .15s,border-color .15s}
li.task input:hover{border-color:var(--peacock)}
li.task input:checked{background:var(--peacock);border-color:var(--peacock)}
li.task input:checked::after{content:"";position:absolute;left:.3em;top:.09em;width:.24em;height:.5em;
 border:solid #ece2cc;border-width:0 2px 2px 0;transform:rotate(43deg)}
li.task label{cursor:pointer;flex:1}
li.task input:checked+label{color:var(--ink-dim);text-decoration:line-through;
 text-decoration-color:var(--rule-up)}

.resetwrap{margin:1.2rem 0 0}
.reset{font-family:"JetBrains Mono",monospace;font-size:8pt;letter-spacing:.12em;text-transform:uppercase;
 color:var(--ink-dim);background:transparent;border:1px solid var(--rule);border-radius:5px;
 padding:.42rem .8rem;cursor:pointer}
.reset:hover{border-color:var(--madder);color:var(--madder)}

.totop{position:fixed;bottom:1.6rem;right:1.6rem;width:2.5rem;height:2.5rem;border-radius:50%;
 background:var(--paper-2);border:1px solid var(--rule-up);color:var(--ink-soft);cursor:pointer;
 font-size:1rem;line-height:1;opacity:0;pointer-events:none;transition:opacity .2s;z-index:60}
.totop.show{opacity:1;pointer-events:auto}
.totop:hover{border-color:var(--madder);color:var(--madder)}

h2,h3{page-break-after:avoid}
@page{margin:16mm 14mm}
@media print{
 .rail,.copy,.totop,.anchor,.resetwrap{display:none!important}
 .sheet{margin:0;max-width:none;padding:0;font-size:10.4pt}
 li.task input{-webkit-print-color-adjust:exact;print-color-adjust:exact}
 a{color:var(--ink);border:0}
}
"""
CSS = CSS.replace('__ROZHA__', ROZHA).replace('__FMT__', FMT)

JS = r"""
(function(){
  // copy buttons on every code block
  document.querySelectorAll('pre').forEach(function(pre){
    var w = document.createElement('div'); w.className = 'codewrap';
    pre.parentNode.insertBefore(w, pre); w.appendChild(pre);
    var b = document.createElement('button');
    b.className = 'copy'; b.type = 'button'; b.textContent = 'copy';
    b.addEventListener('click', function(){
      navigator.clipboard.writeText(pre.innerText).then(function(){
        b.textContent = 'copied'; b.classList.add('done');
        setTimeout(function(){ b.textContent = 'copy'; b.classList.remove('done'); }, 1400);
      });
    });
    w.appendChild(b);
  });

  // checklists remember what you ticked
  var KEY = 'hermes-handout-v1';
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch(e){}
  var boxes = document.querySelectorAll('input[data-k]');
  boxes.forEach(function(b){
    if (saved[b.dataset.k]) b.checked = true;
    b.addEventListener('change', function(){
      saved[b.dataset.k] = b.checked;
      try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch(e){}
    });
  });
  if (boxes.length){
    var last = boxes[boxes.length-1].closest('ul');
    if (last){
      var wrap = document.createElement('div'); wrap.className = 'resetwrap';
      var r = document.createElement('button');
      r.className = 'reset'; r.type = 'button'; r.textContent = 'reset all checkboxes';
      r.addEventListener('click', function(){
        boxes.forEach(function(b){ b.checked = false; });
        try { localStorage.removeItem(KEY); } catch(e){}
        saved = {};
      });
      wrap.appendChild(r); last.parentNode.insertBefore(wrap, last.nextSibling);
    }
  }

  // highlight the section you are reading in the rail
  var links = [].slice.call(document.querySelectorAll('.rail a'));
  var targets = links.map(function(a){ return document.getElementById(a.getAttribute('href').slice(1)); });
  function sync(){
    var y = window.scrollY + 120, best = 0;
    targets.forEach(function(t, i){ if (t && t.offsetTop <= y) best = i; });
    links.forEach(function(a, i){ a.classList.toggle('active', i === best); });
    top.classList.toggle('show', window.scrollY > 700);
  }
  var top = document.querySelector('.totop');
  top.addEventListener('click', function(){ window.scrollTo({top:0, behavior:'smooth'}); });
  window.addEventListener('scroll', sync, {passive:true});
  sync();
})();
"""

doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hermes workshop handout</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body>
<nav class="rail"><span class="rail-title">Contents</span>
{toc_html}
</nav>
<main class="sheet">
{html_body}
</main>
<button class="totop" type="button" aria-label="Back to top">&#8593;</button>
<script>{JS}</script>
</body></html>"""

open('HANDOUT.html', 'w').write(doc)
print('HANDOUT.html', round(len(doc)/1024), 'KB |', len(toc), 'toc entries |', cb_i[0], 'checkboxes')
