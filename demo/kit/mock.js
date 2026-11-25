/* Use-case mock kit: the runtime. One page = one case (JSON in #case) walked through typed stages.
   Nothing leaves the browser: a dropped file is never read, only its name is shown. */
(() => {
'use strict';
const C = JSON.parse(document.getElementById('case').textContent);
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
// [[text]] or [[text|key]] -> <mark>; **bold** -> <b>
const rich = s => esc(s).replace(/\[\[(.+?)(?:\|(.+?))?\]\]/g, (_, v, k) => `<mark data-k="${esc(k || v)}">${v}</mark>`)
  .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
const plain = s => String(s ?? '').replace(/\[\[(.+?)(?:\|.+?)?\]\]/g, '$1').replace(/\*\*(.+?)\*\*/g, '$1');
const TONE = {ok: 'OK', check: 'Check', bad: 'Hold', info: 'Info'};
const lastCell = r => r[r.length - 1];  // the status column of a table row
const chip = (tone, label) => `<span class="chip ${tone || ''}">${esc(label ?? TONE[tone] ?? tone)}</span>`;
const wait = ms => new Promise(r => setTimeout(r, ms));
const now = () => new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false});
const ext = n => (n.split('.').pop() || 'txt').toLowerCase().slice(0, 4);
const FAST = /[?&]fast\b/.test(location.search);  // ?fast for quick run-throughs
const T = ms => FAST ? 40 : ms;

const stages = [...C.stages, {type: 'done', title: 'Outcome'}];
let S;
function reset() {
  S = {i: 0, reached: 0, done: new Set(), audit: [], loaded: false, processed: false,
       cur: 0, docs: C.docs.map(() => ({state: '', reason: '', edits: {}})), exc: {}, approved: {}, approvedAt: {}, written: {}, asked: {}, checks: {}, reports: {}};
}
function audit(who, text) { S.audit.push({t: now(), who, text}); renderAudit(); }

/* ---------- shell ---------- */
function shell() {
  const B = C.brand;
  document.body.innerHTML = `
<div class="demo-note"><b>Demo</b> · invented data, pre-written results. Nothing you add is uploaded, read or stored.</div>
<div class="shell">
  <aside class="side">
    <div class="brand"><span class="mk">${esc(B.mark)}</span><div>${esc(B.name)}<small>${esc(B.product)}</small></div></div>
    <h4>Walkthrough</h4><ol class="steps" id="steps"></ol>
    <button class="restart" id="restart">↺ Start over</button>
    <div class="who">Signed in as <b>${esc(C.persona?.name || 'You')}</b><br>${esc(C.persona?.role || '')}</div>
  </aside>
  <section class="main">
    <div class="top"><div><div class="crumb">${esc(C.industry)}<span>${esc(C.area || 'Use case')}</span></div>
      <h1>${esc(C.title)}</h1><p class="tagline">${esc(C.tagline)}</p></div></div>
    <div class="flow">
      <div><b>Starts with</b>${esc(C.flow.start)}</div><div><b>The assistant</b>${esc(C.flow.agent)}</div>
      <div class="p"><b>A person</b>${esc(C.flow.person)}</div><div><b>Ends with</b>${esc(C.flow.end)}</div></div>
    <div class="card" id="stage"></div>
    <details class="activity" id="act"><summary>Audit trail (<span id="actn">0</span> events)</summary><ul class="audit" id="audit"></ul></details>
  </section>
</div>`;
  $('#restart').onclick = () => { reset(); go(0); };
}
function renderSteps() {
  $('#steps').innerHTML = stages.map((s, i) => `<li><button data-i="${i}" class="${i === S.i ? 'on' : ''} ${S.done.has(i) ? 'done' : ''}" ${i > S.reached ? 'disabled' : ''}>
    <span class="n">${S.done.has(i) ? '✓' : i + 1}</span><span class="lbl">${esc(s.title || LABEL[s.type])}</span></button></li>`).join('');
  $$('#steps button').forEach(b => b.onclick = () => go(+b.dataset.i));
}
const auditRows = list => list.map(a => `<li><span class="t">${a.t}</span><span class="${a.who === 'Assistant' ? 'who-a' : 'who-p'}">${esc(a.who)}</span><span>${esc(a.text)}</span></li>`).join('');
function renderAudit() {
  const el = $('#audit'); if (!el) return;
  $('#actn').textContent = S.audit.length;
  el.innerHTML = auditRows(S.audit.slice().reverse());
}
const LABEL = {upload: 'Add documents', process: 'Processing', review: 'Review', exceptions: 'Exceptions', draft: 'Draft',
  approve: 'Approval', write: 'Update system', report: 'Report', ask: 'Ask', feed: 'Monitor', calendar: 'Schedule',
  compare: 'Compare', done: 'Outcome'};

function frame(st, body, {next = true, hint = '', ready = true} = {}) {
  const last = S.i === stages.length - 1;
  $('#stage').innerHTML = `<div class="stage-h"><div><h2>${esc(st.title || LABEL[st.type])}</h2>${st.sub ? `<p>${esc(st.sub)}</p>` : ''}</div>
    ${S.i > 0 ? `<button class="btn sm" id="back">← Back</button>` : ''}</div>
    <div class="stage-b" id="sb">${body}</div>
    ${last ? '' : `<div class="stage-f"><span class="hint" id="hint">${esc(hint)}</span>
      ${next ? `<button class="btn pri" id="next" ${ready ? '' : 'disabled'}>${esc(st.next || 'Continue')} →</button>` : ''}</div>`}`;
  $('#back') && ($('#back').onclick = () => go(S.i - 1));
  $('#next') && ($('#next').onclick = () => { S.done.add(S.i); go(S.i + 1); });
}
const ready = (on, hint) => { const n = $('#next'); if (n) n.disabled = !on; if (hint !== undefined && $('#hint')) $('#hint').textContent = hint; };

function go(i) {
  S.i = Math.max(0, Math.min(i, stages.length - 1));
  S.reached = Math.max(S.reached, S.i);
  renderSteps();
  const st = stages[S.i];
  $('#act').style.display = '';
  (K[st.type] || K.unknown)(st);
  renderAudit();
  window.scrollTo({top: 0, behavior: 'smooth'});
}

/* ---------- documents ---------- */
function docView(d) {
  let inner;
  if (d.kind === 'sheet' && d.rows) {
    const [h, ...r] = d.rows;
    inner = `<div class="db" style="white-space:normal"><table><tr>${h.map(x => `<th>${rich(x)}</th>`).join('')}</tr>${r.map(row => `<tr>${row.map(x => `<td>${rich(x)}</td>`).join('')}</tr>`).join('')}</table>${d.body ? `<p style="white-space:pre-wrap;margin:10px 0 0">${rich(d.body)}</p>` : ''}</div>`;
  } else if (d.kind === 'call') {
    inner = `<div class="db">${String(d.body).split('\n').map(l => { const m = l.match(/^([^:]{1,24}):\s?(.*)$/); return m ? `<b>${esc(m[1])}:</b> ${rich(m[2])}` : rich(l); }).join('\n')}</div>`;
  } else {
    inner = `<div class="db">${rich(d.body)}</div>`;
  }
  const meta = d.kind === 'email' ? `<div class="meta"><b>From</b> ${esc(d.from || '')} &nbsp; <b>To</b> ${esc(d.to || '')}<br><b>Subject</b> ${esc(d.subject || d.name)}</div>` : '';
  return `<div class="doc ${esc(d.kind)}"><div class="dh"><span>${esc(d.name)}</span><span>${esc(d.meta || '')}</span></div>${meta}${inner}</div>`;
}
const lowField = f => String(f[1]).startsWith('?') || (f[3] != null && f[3] < 0.8);
function docTone(d) {
  if (d.tone) return d.tone;
  if ((d.table?.r || []).some(r => lastCell(r) === 'bad') || (d.flags || []).some(f => Array.isArray(f) && f[0] === 'bad')) return 'bad';
  if ((d.fields || []).some(lowField) || (d.table?.r || []).some(r => lastCell(r) === 'check') || (d.flags || []).length) return 'check';
  return 'ok';
}
function fieldsTable(d, di) {
  return `<div class="tw"><table class="t"><tr><th>Field</th><th>Value</th><th>Confidence</th><th>Found in</th></tr>${d.fields.map((f, i) => {
    const low = lowField(f), v = String(f[1]).replace(/^\?/, ''), c = f[3] ?? (low ? 0.45 : 0.97);
    const col = c >= 0.9 ? 'var(--ok)' : c >= 0.75 ? 'var(--check)' : 'var(--bad)';
    const ed = S.docs[di].edits[i];
    const val = low && !S.docs[di].state ? `<input class="fx" data-f="${i}" value="${esc(ed ?? '')}" placeholder="${esc(v)}">` : esc(ed ?? v);
    return `<tr class="pick" data-k="${esc(f[0])}" data-v="${esc(v)}"><td>${esc(f[0])}</td><td>${val}</td><td><span class="conf"><i style="width:${Math.round(c * 100)}%;background:${col}"></i></span>${low ? chip('check', 'Check') : ''}</td><td class="src">${esc(f[2] || '')}</td></tr>`;
  }).join('')}</table></div>`;
}
function statusTable(t, filters) {
  const tones = [...new Set(t.r.map(lastCell))];
  const f = filters && tones.length > 1 ? `<div class="filters"><button class="on" data-f="">All (${t.r.length})</button>${tones.map(x => `<button data-f="${x}">${TONE[x] || x} (${t.r.filter(r => lastCell(r) === x).length})</button>`).join('')}</div>` : '';
  const extra = !t.h || !t.r.length || t.h.length < t.r[0].length;
  return `${f}<div class="tw"><table class="t">${t.h ? `<tr>${t.h.map(x => `<th>${esc(x)}</th>`).join('')}${extra ? '<th>Status</th>' : ''}</tr>` : ''}${t.r.map(r => {
    const s = lastCell(r);
    return `<tr data-s="${esc(s)}">${r.slice(0, -1).map(x => `<td>${rich(x)}</td>`).join('')}<td>${chip(s)}</td></tr>`;
  }).join('')}</table></div>`;
}
function wireFilters(root) {
  $$('.filters button', root).forEach(b => b.onclick = () => {
    $$('.filters button', root).forEach(x => x.classList.toggle('on', x === b));
    $$('tr[data-s]', root).forEach(tr => tr.style.display = !b.dataset.f || tr.dataset.s === b.dataset.f ? '' : 'none');
  });
}
const flagList = fl => `<ul class="flags">${fl.map(f => Array.isArray(f) ? `<li class="${esc(f[0])}">${rich(f[1])}</li>` : `<li>${rich(f)}</li>`).join('')}</ul>`;
function draftBox(dr, id) {
  const texts = [dr.text, ...(dr.alt || [])];
  return `<div class="draft" data-alt="0" id="${id}"><div class="dh"><span>${esc(dr.label || 'Draft')}${dr.to ? ' · to ' + esc(dr.to) : ''}</span>
    <span class="row">${texts.length > 1 ? `<button class="btn sm" data-regen>↻ Another version</button>` : ''}<span>Editable</span></span></div>
    ${dr.subject ? `<div style="padding:8px 14px 0;font-size:13px"><b>Subject:</b> ${esc(dr.subject)}</div>` : ''}
    <div class="ed" contenteditable="true">${rich(texts[0])}</div></div>`;
}
function wireDraft(root, dr) {
  const texts = [dr.text, ...(dr.alt || [])];
  $$('[data-regen]', root).forEach(b => b.onclick = async () => {
    const box = b.closest('.draft'), ed = $('.ed', box);
    let k = (+box.dataset.alt + 1) % texts.length; box.dataset.alt = k;
    ed.style.opacity = .35; await wait(T(500)); ed.innerHTML = rich(texts[k]); ed.style.opacity = 1;
    audit('Assistant', `Rewrote the draft (version ${k + 1} of ${texts.length})`);
  });
}

/* ---------- stage components ---------- */
const K = {};

K.upload = st => {
  const inbox = st.mode === 'inbox';
  const files = C.docs.map((d, i) => `<div class="file" data-i="${i}"><span class="ic ${ext(d.name)}">${ext(d.kind === 'email' ? 'x.eml' : d.name).toUpperCase()}</span>
    <div style="min-width:0"><b>${esc(d.kind === 'email' ? (d.subject || d.name) : d.name)}</b><small>${esc(d.kind === 'email' ? 'from ' + (d.from || '') : d.meta || '')}</small></div>
    <span class="fin"></span><i class="bar"></i></div>`).join('');
  const body = inbox
    ? `<div class="drop" id="drop"><div style="font-size:26px">📥</div><div class="big">${esc(st.source || 'Connected inbox')}</div><small>${esc(st.hint || 'New messages are picked up as they arrive.')}</small>
       <div class="row" style="justify-content:center;margin-top:12px"><button class="btn pri" id="sample">${esc(st.cta || 'Check for new messages')}</button></div></div>
       <div class="files" id="files" style="display:none">${files}</div>`
    : `<div class="drop" id="drop"><div style="font-size:26px">⤒</div><div class="big">${esc(st.drop || 'Drop files here')}</div><small>${esc(st.hint || 'PDF, scans, spreadsheets or emails')}</small>
       <div class="row" style="justify-content:center;margin-top:12px"><button class="btn pri" id="sample">${esc(st.cta || 'Use the sample files')}</button></div></div>
       <div class="own" id="own" style="display:none"></div>
       <div class="files" id="files" style="display:none">${files}</div>`;
  frame(st, body, {ready: S.loaded, hint: S.loaded ? `${C.docs.length} ready` : 'Add the sample files to continue'});
  if (S.loaded) { $('#files').style.display = ''; $$('.file').forEach(f => { $('.bar', f).style.width = '100%'; $('.fin', f).innerHTML = chip('ok', 'Received'); }); return; }
  const drop = $('#drop');
  const load = async (own) => {
    $('#sample').disabled = true; $('#files').style.display = '';
    if (own) { const o = $('#own'); o.style.display = ''; o.textContent = `You dropped “${own}”. In this demo your file is not opened, read or uploaded. The sample files below stand in for it.`; }
    for (const f of $$('.file')) { await wait(T(260)); $('.bar', f).style.width = '100%'; await wait(T(380)); $('.fin', f).innerHTML = chip('ok', inbox ? 'New' : 'Received'); }
    S.loaded = true; audit('You', inbox ? `${C.docs.length} new messages picked up from ${st.source || 'the inbox'}` : `Added ${C.docs.length} files`);
    ready(true, `${C.docs.length} ready`);
  };
  $('#sample').onclick = () => load();
  if (!inbox) {
    ['dragenter', 'dragover'].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.add('over'); }));
    ['dragleave', 'drop'].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.remove('over'); }));
    drop.addEventListener('drop', ev => { const f = ev.dataTransfer?.files?.[0]; if (!S.loaded && !$('#sample').disabled) load(f ? f.name : 'your file'); });
  }
};

K.process = st => {
  const steps = st.steps || [['Reading each document', 'Text, tables and scans'], ['Pulling out the details', 'Against your field list'], ['Checking against your rules', 'Prices, terms, records'], ['Preparing drafts for review', 'Nothing is sent or saved']];
  const counters = st.counters || [['Documents', C.docs.length], ['Items checked', C.docs.reduce((a, d) => a + (d.fields || []).length + (d.table?.r || []).length, 0)], ['Need a person', C.docs.filter(d => docTone(d) !== 'ok').length]];
  const body = `<div class="counters">${counters.map((c, i) => `<div class="kpi"><b data-c="${i}">0</b><small>${esc(c[0])}</small></div>`).join('')}</div>
    <div class="progress"><i id="pb"></i></div>
    <div class="pipe">${steps.map((s, i) => `<div class="pstep" data-i="${i}"><span class="dot"></span><div><b>${esc(s[0])}</b><small>${esc(s[1] || '')}</small></div></div>`).join('')}</div>
    <div class="console" id="con"></div>`;
  frame(st, body, {ready: S.processed, hint: S.processed ? 'Finished. Everything is waiting for review.' : 'Working…'});
  const con = $('#con'), line = (t, c = '') => { con.insertAdjacentHTML('beforeend', `<div><span class="t">${now()}</span> <span class="${c}">${esc(t)}</span></div>`); con.scrollTop = 1e6; };
  const setCounters = () => counters.forEach((c, i) => $(`[data-c="${i}"]`).textContent = c[1]);
  if (S.processed) { $('#pb').style.width = '100%'; $$('.pstep').forEach(p => { p.className = 'pstep fin'; $('.dot', p).textContent = '✓'; }); setCounters(); (S.log || []).forEach(l => line(l[0], l[1])); return; }
  const idx = S.i; S.log = [];
  const L = (t, c) => { S.log.push([t, c]); if (S.i === idx) line(t, c); };
  (async () => {
    const perDoc = C.docs.map(d => {
      const low = (d.fields || []).filter(lowField).length, n = (d.fields || []).length + (d.table?.r || []).length, tone = docTone(d);
      return [`${d.name}: ${n} items, ${low ? low + ' uncertain, ' : ''}${(d.flags || []).length} flagged`, tone === 'ok' ? 'g' : 'y'];
    });
    const extra = st.log || [];
    for (let i = 0; i < steps.length; i++) {
      if (S.i !== idx) return;
      const p = $(`.pstep[data-i="${i}"]`); p.className = 'pstep run';
      L(`▸ ${steps[i][0]}`);
      const chunk = i === 0 ? C.docs.map(d => [`  opened ${d.name}`, '']) : i === 1 ? perDoc.map(x => ['  ' + x[0], x[1]]) : [];
      for (const c of chunk) { await wait(T(320)); L(c[0], c[1]); }
      for (const e of extra.filter(e => (e[2] ?? steps.length - 1) === i)) { await wait(T(300)); L('  ' + e[0], e[1] || ''); }
      await wait(T(650));
      if (S.i !== idx) return;
      p.className = 'pstep fin'; $('.dot', p).textContent = '✓';
      $('#pb').style.width = Math.round((i + 1) / steps.length * 100) + '%';
      counters.forEach((c, j) => { const v = $(`[data-c="${j}"]`); if (v) v.textContent = typeof c[1] === 'number' ? Math.round(c[1] * (i + 1) / steps.length) : (i === steps.length - 1 ? c[1] : '…'); });
    }
    L('✓ Done. Nothing has been sent or saved; everything waits for a person.', 'g');
    S.processed = true; audit('Assistant', st.auditText || `Prepared a first pass on ${C.docs.length} items`);
    if (S.i === idx) { setCounters(); ready(true, 'Finished. Everything is waiting for review.'); }
  })();
};

K.review = st => {
  const decided = () => S.docs.filter(d => d.state).length;
  const q = C.docs.map((d, i) => {
    const s = S.docs[i].state, tone = s === 'yes' ? 'ok' : s === 'no' ? 'bad' : docTone(d);
    const lab = s === 'yes' ? (st.doneLabel || 'Approved') : s === 'no' ? 'Sent back' : {ok: 'Ready', check: 'Check', bad: 'Hold'}[tone];
    return `<button class="qi ${i === S.cur ? 'on' : ''}" data-i="${i}">${chip(tone, lab)}<b>${esc(d.label || d.subject || d.name)}</b><small>${esc(d.sub || d.meta || '')}</small></button>`;
  }).join('');
  const d = C.docs[S.cur], ds = S.docs[S.cur];
  let res = '';
  if (d.fields) res += `<div class="sec-t">Extracted</div>${fieldsTable(d, S.cur)}`;
  if (d.table) res += `<div class="sec-t">${esc(d.table.title || 'Checks')}</div>${statusTable(d.table)}`;
  if (d.flags?.length) res += `<div class="sec-t">For a person to look at</div>${flagList(d.flags)}`;
  if (d.draft) res += `<div class="sec-t">${esc(d.draft.label || 'Draft')}</div>${draftBox(d.draft, 'dr' + S.cur)}`;
  if (d.notes) res += `<div class="sec-t">Notes</div><p style="margin:0;font-size:13px">${rich(d.notes)}</p>`;
  const reasons = st.reasons || ['Needs more information', 'Wrong match', 'I will handle it myself'];
  const act = ds.state
    ? `<div class="decided ${ds.state === 'yes' ? 'ok' : 'bad'}">${ds.state === 'yes' ? '✓ ' + esc(st.doneLabel || 'Approved') : '↩ Sent back: ' + esc(ds.reason)} <button class="btn sm" id="undo" style="margin-left:8px">Undo</button></div>`
    : `<div class="decide"><button class="btn ok" id="yes">${esc(d.yes || st.yes || 'Approve')}</button><button class="btn warn" id="no">${esc(st.no || 'Send back')}</button>
       <span class="hint" style="color:var(--muted);font-size:12.5px">${esc(st.rule || 'Nothing moves until you decide.')}</span></div>
       <div class="reason" id="reasons">${reasons.map(r => `<button>${esc(r)}</button>`).join('')}</div>`;
  const left = st.hideDoc ? '' : `<div><div class="sec-t">Source</div>${docView(d)}</div>`;
  const body = `<div class="review"><div class="queue">${q}</div><div class="rv"><div class="${st.hideDoc ? '' : 'split'}">${left}<div>${res}${act}</div></div></div></div>`;
  frame(st, body, {hint: `${decided()} of ${C.docs.length} decided`});
  $('#sb').style.padding = 0;
  $$('.qi').forEach(b => b.onclick = () => { S.cur = +b.dataset.i; K.review(st); });
  wireDraft($('#sb'), d.draft || {});
  $$('tr.pick').forEach(tr => tr.onclick = () => {
    $$('tr.pick').forEach(x => x.classList.remove('hl')); tr.classList.add('hl');
    $$('mark').forEach(m => m.classList.toggle('hot', m.dataset.k === tr.dataset.k || m.textContent === tr.dataset.v));
    const m = $('mark.hot'); m && m.scrollIntoView({block: 'nearest', behavior: 'smooth'});
  });
  $$('mark').forEach(m => m.onclick = () => { const tr = $$('tr.pick').find(t => t.dataset.k === m.dataset.k || t.dataset.v === m.textContent); tr && tr.click(); });
  $$('input.fx').forEach(inp => inp.oninput = () => { ds.edits[inp.dataset.f] = inp.value; });
  const after = () => { const nx = S.docs.findIndex(x => !x.state); if (nx >= 0) S.cur = nx; K.review(st); };
  $('#yes') && ($('#yes').onclick = () => {
    const missing = $$('input.fx').filter(i => !i.value.trim());
    if (missing.length && !st.allowBlank) { missing.forEach(i => i.style.outline = '2px solid var(--bad)'); $('#hint').textContent = 'Fill or confirm the highlighted field first, or send it back.'; missing[0].focus(); return; }
    ds.state = 'yes'; audit('You', `${d.yes || st.yes || 'Approved'}: ${d.label || d.subject || d.name}`); after();
  });
  $('#no') && ($('#no').onclick = () => $('#reasons').classList.add('show'));
  $$('#reasons button').forEach(b => b.onclick = () => { ds.state = 'no'; ds.reason = b.textContent; audit('You', `Sent back (${b.textContent}): ${d.label || d.subject || d.name}`); after(); });
  $('#undo') && ($('#undo').onclick = () => { ds.state = ''; audit('You', `Reopened: ${d.label || d.subject || d.name}`); K.review(st); });
};

K.exceptions = st => {
  const items = st.items, E = (S.exc[S.i] = S.exc[S.i] || {});
  const n = () => items.filter((_, i) => E[i] != null).length;
  const body = items.map((x, i) => `<div class="exc"><h3>${chip(x.tone || 'check')} ${esc(x.title)}</h3><p>${rich(x.detail)}</p>
    ${x.rec != null ? `<p style="font-size:12.5px">Assistant suggests: <b>${esc(x.options[x.rec])}</b>${x.why ? ' · ' + esc(x.why) : ''}</p>` : ''}
    <div class="opts" data-i="${i}">${x.options.map((o, j) => `<button data-j="${j}" class="${E[i] === j ? 'sel' : ''}">${esc(o)}</button>`).join('')}</div></div>`).join('');
  frame(st, body, {ready: n() === items.length, hint: `${n()} of ${items.length} resolved by you`});
  $$('.opts').forEach(o => $$('button', o).forEach(b => b.onclick = () => {
    const i = +o.dataset.i, j = +b.dataset.j; E[i] = j;
    $$('button', o).forEach(x => x.classList.toggle('sel', x === b));
    audit('You', `${items[i].title}: ${items[i].options[j]}`);
    ready(n() === items.length, `${n()} of ${items.length} resolved by you`);
  }));
};

K.compare = st => {
  frame(st, `${st.intro ? `<p style="margin-top:0">${rich(st.intro)}</p>` : ''}${st.kpis ? kpis(st.kpis) : ''}${statusTable(st.table, true)}${st.flags ? `<div class="sec-t">For a person to look at</div>${flagList(st.flags)}` : ''}`);
  wireFilters($('#sb'));
};

K.draft = st => {
  const ctx = st.context ? `<div class="sec-t">${esc(st.contextLabel || 'Based on')}</div>${flagList(st.context.map(c => ['info', c]))}` : '';
  frame(st, `${ctx}<div class="sec-t">${esc(st.label || 'Draft')}</div>${draftBox(st, 'dr')}<p style="font-size:12.5px;color:var(--muted)">${esc(st.note || 'Edit anything. Nothing is sent from this screen.')}</p>`);
  wireDraft($('#sb'), st);
};

K.approve = st => {
  const ck = st.checks || [];
  const key = S.i;
  S.checks[key] = S.checks[key] || ck.map(() => false);
  const sum = st.summary ? `<div class="tw" style="margin-bottom:12px"><table class="t">${st.summary.map(r => `<tr><td style="width:38%;color:var(--muted)">${esc(r[0])}</td><td>${rich(r[1])}</td></tr>`).join('')}</table></div>` : '';
  const dec = S.approved[key] === 'yes' ? `<div class="decided ok">✓ ${esc(st.doneLabel || 'Approved')} by ${esc(C.persona?.name || 'you')} at ${esc(S.approvedAt[key])}</div>`
    : S.approved[key] === 'no' ? `<div class="decided bad">↩ Held. ${esc(st.heldText || 'Nothing was sent or saved.')}</div>` : '';
  const body = `<div class="gate"><h3>${esc(st.question || 'Ready to go ahead?')}</h3><p style="margin:0 0 10px;font-size:13px;color:var(--muted)">${esc(st.explain || 'This is the step a person always owns. The assistant cannot do it.')}</p>
    ${sum}${ck.length ? `<ul class="checklist">${ck.map((c, i) => `<li><input type="checkbox" id="ck${i}" ${S.checks[key][i] ? 'checked' : ''}><label for="ck${i}">${rich(c)}</label></li>`).join('')}</ul>` : ''}
    ${dec || `<div class="row"><button class="btn ok" id="ap" ${S.checks[key].every(Boolean) ? '' : 'disabled'}>${esc(st.yes || 'Approve')}</button><button class="btn warn" id="hold">${esc(st.no || 'Hold')}</button></div>`}</div>`;
  frame(st, body, {ready: !!S.approved[key], hint: dec ? '' : 'Tick each check, then decide.'});
  $$('.checklist input').forEach((c, i) => c.onchange = () => { S.checks[key][i] = c.checked; $('#ap') && ($('#ap').disabled = !S.checks[key].every(Boolean)); });
  $('#ap') && ($('#ap').onclick = () => { S.approved[key] = 'yes'; S.approvedAt[key] = now(); audit('You', st.auditText || `${st.yes || 'Approved'}`); K.approve(st); });
  $('#hold') && ($('#hold').onclick = () => { S.approved[key] = 'no'; audit('You', `Held: ${st.question || 'approval'}`); K.approve(st); });
};

// Decisions made earlier in the walkthrough that later stages must respect.
const heldBefore = () => Object.entries(S.approved).some(([k, v]) => v === 'no' && +k < S.i);
const sentBack = () => S.docs.filter(d => d.state === 'no').length;
const allSentBack = () => S.docs.length > 0 && sentBack() === S.docs.length;
function caveat() {
  if (heldBefore()) return `<ul class="flags" style="margin-bottom:12px"><li class="bad">You held this at the approval step, so nothing here was sent, saved or shared.</li></ul>`;
  if (allSentBack()) return `<ul class="flags" style="margin-bottom:12px"><li class="bad">You sent back every item, so nothing here was written or sent. Each one goes back to its owner.</li></ul>`;
  const n = sentBack();
  return n ? `<ul class="flags" style="margin-bottom:12px"><li>${n} item${n > 1 ? 's' : ''} you sent back ${n > 1 ? 'are' : 'is'} left out and go${n > 1 ? '' : 'es'} back to the owner. (In this demo the pre-written records and figures below don't change.)</li></ul>` : '';
}

K.write = st => {
  const recs = st.records || [];
  if (heldBefore() || allSentBack()) {
    frame(st, caveat() + `<div class="sys"><div class="sh"><span>${esc(st.system || 'Your system')}</span><span>${esc(st.env || 'test copy')}</span></div><div class="sb">${recs.map(r => `<div class="rec in"><div class="row" style="justify-content:space-between"><b>${esc(r.title)}</b>${chip('bad', 'Not written')}</div></div>`).join('')}</div></div>`, {hint: 'Nothing was written.'});
    return;
  }
  const body = `${caveat()}<div class="sys"><div class="sh"><span>${esc(st.system || 'Your system')}</span><span>${esc(st.env || 'test copy')}</span></div><div class="sb" id="recs">
    ${recs.map((r, i) => `<div class="rec" data-i="${i}"><div class="row" style="justify-content:space-between"><b>${esc(r.title)}</b>${chip(r.tone || 'ok', r.status || 'Saved')}</div>
      ${r.kv ? `<div class="kv">${r.kv.map(x => `<span>${esc(x[0])}: <b>${esc(x[1])}</b></span>`).join('')}</div>` : ''}${r.note ? `<div style="font-size:12.5px;margin-top:4px;color:var(--muted)">${rich(r.note)}</div>` : ''}</div>`).join('')}
    </div></div>${S.written[S.i] ? '' : `<div class="row" style="margin-top:12px"><button class="btn pri" id="w">${esc(st.cta || 'Write to ' + (st.system || 'the system'))}</button><span style="font-size:12.5px;color:var(--muted)">${esc(st.note || 'Only what a person approved is written.')}</span></div>`}`;
  frame(st, body, {ready: !!S.written[S.i], hint: S.written[S.i] ? 'Saved.' : ''});
  if (S.written[S.i]) { $$('.rec').forEach(r => r.classList.add('in')); return; }
  $('#w').onclick = async () => {
    $('#w').disabled = true; const idx = S.i;
    for (const r of $$('.rec')) { await wait(T(450)); if (S.i !== idx) return; r.classList.add('in'); }
    S.written[idx] = true; audit('Assistant', (st.auditText || `Wrote ${recs.length} record(s) to ${st.system || 'the system'} after approval`) + (sentBack() ? ` (${sentBack()} sent back, left out)` : ''));
    ready(true, 'Saved.'); $('#w').remove();
  };
};

function kpis(list) { return `<div class="kpis">${list.map(k => `<div class="kpi ${esc(k[2] || '')}"><b>${esc(k[0])}</b><small>${esc(k[1])}</small></div>`).join('')}</div>`; }
function chart(c) {
  const W = 640, bh = 22, gap = 8, lw = 170, max = Math.max(...c.values.map(Math.abs), 1), H = c.values.length * (bh + gap) + 10;
  const bars = c.values.map((v, i) => {
    const w = Math.max(2, Math.abs(v) / max * (W - lw - 70)), y = i * (bh + gap) + 4, col = (c.tones && c.tones[i]) ? `var(--${c.tones[i]})` : 'var(--accent)';
    return `<text x="${lw - 8}" y="${y + bh / 2 + 4}" text-anchor="end">${esc(c.labels[i])}</text><rect x="${lw}" y="${y}" width="${w}" height="${bh}" rx="3" fill="${col}" opacity=".85"></rect><text x="${lw + w + 6}" y="${y + bh / 2 + 4}">${esc((c.prefix || '') + v.toLocaleString(undefined, {maximumFractionDigits: Math.abs(v) >= 100 ? 0 : 1}) + (c.unit || ''))}</text>`;
  }).join('');
  return `${c.title ? `<p style="font-size:12.5px;color:var(--muted);margin:6px 0 2px">${esc(c.title)}</p>` : ''}<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(c.title || 'chart')}">${bars}</svg>`;
}
function reportHTML(st) {
  const secs = (st.sections || []).map(s => `<h3>${esc(s.h)}</h3>${s.p ? (Array.isArray(s.p) ? s.p : [s.p]).map(p => `<p>${rich(p)}</p>`).join('') : ''}
    ${s.list ? `<ul>${s.list.map(x => `<li>${rich(x)}</li>`).join('')}</ul>` : ''}${s.kpis ? kpis(s.kpis) : ''}${s.table ? statusOrPlain(s.table) : ''}${s.chart ? chart(s.chart) : ''}`).join('');
  return `<div class="paper" id="paper"><div class="rh"><div><h2>${esc(st.doc || st.title)}</h2><small>${esc(st.subtitle || '')}</small></div><div style="text-align:right"><b>${esc(C.brand.name)}</b><br><small>Prepared ${new Date().toLocaleDateString([], {day: 'numeric', month: 'short', year: 'numeric'})}</small></div></div>
    ${st.kpis ? kpis(st.kpis) : ''}${secs}${st.sources ? `<h3>Sources</h3><ol class="cites">${st.sources.map(s => `<li>${esc(s)}</li>`).join('')}</ol>` : ''}
    <div class="foot">${esc(st.foot || 'Draft prepared by the assistant from the documents above. A person reviewed and approved it before use.')} · Demo with invented data.</div></div>`;
}
function statusOrPlain(t) {
  const hasStatus = t.r.length && ['ok', 'check', 'bad', 'info'].includes(lastCell(t.r[0]));
  if (hasStatus) return statusTable(t);
  return `<div class="tw"><table class="t">${t.h ? `<tr>${t.h.map(x => `<th>${esc(x)}</th>`).join('')}</tr>` : ''}${t.r.map(r => `<tr>${r.map(x => `<td>${rich(x)}</td>`).join('')}</tr>`).join('')}</table></div>`;
}
const PRINT_CSS = `body{font:14px/1.5 system-ui,Arial,sans-serif;color:#1b2230;margin:30px}.paper{max-width:820px;margin:auto}.rh{display:flex;justify-content:space-between;border-bottom:2px solid #1b2230;margin-bottom:14px}h2{margin:0}h3{font-size:13px;text-transform:uppercase;margin:18px 0 6px}table{width:100%;border-collapse:collapse;font-size:13px}td,th{border-bottom:1px solid #dde1e8;padding:5px 7px;text-align:left}.kpis{display:flex;gap:8px;flex-wrap:wrap}.kpi{border:1px solid #dde1e8;border-radius:8px;padding:8px 10px;min-width:130px}.kpi b{display:block;font-size:20px}.chip{font-size:11px;font-weight:600;border-radius:10px;padding:1px 7px;background:#eee}.chip.ok{background:#e3f4ea}.chip.check{background:#fdf1dc}.chip.bad{background:#fbe4e7}.foot,small,.cites{color:#5d6678;font-size:12px}svg text{font-size:11px;fill:#5d6678}rect{fill:#2f5bea}mark{background:none;font-weight:600}`;

K.report = st => {
  const idx = S.i;
  const tools = `<div class="rep-tools"><span class="row">${chip('info', st.format || 'Report')}${S.reports[idx] ? chip('check', 'Draft · needs sign-off') : ''}</span>
    <span class="row"><button class="btn sm" id="regen">↻ Regenerate</button><button class="btn sm" id="print">Print / PDF</button><button class="btn sm" id="dl">Download</button></span></div>`;
  const gen = `<div class="gen"><div class="spinner"></div><div id="gs">Gathering figures…</div></div>`;
  frame(st, S.reports[idx] ? tools + caveat() + reportHTML(st) : gen, {ready: !!S.reports[idx], hint: S.reports[idx] ? 'Read it, edit the source items if needed, then continue.' : 'Generating…'});
  const wire = () => {
    $('#print').onclick = () => window.print();
    $('#dl').onclick = () => {
      const html = `<!doctype html><html><head><meta charset="utf-8"><title>${esc(st.doc || st.title)}</title><style>${PRINT_CSS}</style></head><body>${$('#paper').outerHTML}</body></html>`;
      const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([html], {type: 'text/html'}));
      a.download = (st.file || (st.doc || st.title).toLowerCase().replace(/[^a-z0-9]+/g, '-')) + '.html'; a.click();
      audit('You', `Downloaded “${st.doc || st.title}”`);
    };
    $('#regen').onclick = () => { S.reports[idx] = false; K.report(st); };
  };
  if (S.reports[idx]) return wire();
  (async () => {
    for (const m of st.genSteps || ['Gathering figures…', 'Writing the sections…', 'Linking every point to its source…', 'Formatting…']) {
      if (S.i !== idx) return; $('#gs') && ($('#gs').textContent = m); await wait(T(700));
    }
    if (S.i !== idx) return;
    S.reports[idx] = true; audit('Assistant', `Generated “${st.doc || st.title}” (draft)`); K.report(st);
  })();
};

K.ask = st => {
  const A = (S.asked[S.i] = S.asked[S.i] || new Set());
  const shown = st.qa.filter((_, i) => A.has(i));
  const body = `${st.intro ? `<p style="margin-top:0;color:var(--muted)">${esc(st.intro)}</p>` : ''}<div class="chat" id="chat">
    ${shown.length ? '' : `<div class="msg a">${esc(st.hello || 'Ask a question. Every answer links to where it came from.')}</div>`}
    ${st.qa.map((x, i) => A.has(i) ? `<div class="msg u">${esc(x.q)}</div><div class="msg a">${rich(x.a)}${x.cites ? `<div class="cites">${x.cites.map((c, j) => `<sup class="c">[${j + 1}]</sup> ${esc(c)}`).join(' &nbsp; ')}</div>` : ''}</div>` : '').join('')}
    </div><div class="sugg">${st.qa.map((x, i) => `<button data-i="${i}" ${A.has(i) ? 'disabled' : ''}>${esc(x.q)}</button>`).join('')}</div>`;
  frame(st, body, {hint: `${A.size} of ${st.qa.length} asked`});
  $$('.sugg button').forEach(b => b.onclick = async () => {
    const i = +b.dataset.i, x = st.qa[i], idx = S.i; $$('.sugg button').forEach(z => z.disabled = true);
    const chat = $('#chat'); chat.insertAdjacentHTML('beforeend', `<div class="msg u">${esc(x.q)}</div><div class="msg a" id="typing">…</div>`);
    audit('You', `Asked: ${x.q}`);
    await wait(T(700)); if (S.i !== idx) return;
    const t = $('#typing'), words = plain(x.a).split(' ');
    for (let k = 1; k <= words.length; k += 3) { if (S.i !== idx) return; t.textContent = words.slice(0, k).join(' '); await wait(T(45)); }
    A.add(i); audit('Assistant', `Answered with ${(x.cites || []).length} source(s)`); K.ask(st);
  });
};

K.feed = st => {
  const body = `${st.intro ? `<p style="margin-top:0;color:var(--muted)">${esc(st.intro)}</p>` : ''}${st.kpis ? kpis(st.kpis) : ''}<div class="feed">${st.items.map(x => `<div class="fi"><span class="when">${esc(x.when)}</span>
    <div><b>${esc(x.title)}</b><p>${rich(x.text)}</p>${x.src ? `<p class="cites">Source: ${esc(x.src)}</p>` : ''}</div>${x.tag ? chip(x.tag[0], x.tag[1]) : ''}</div>`).join('')}</div>`;
  frame(st, body);
};

K.calendar = st => {
  const body = `${st.intro ? `<p style="margin-top:0;color:var(--muted)">${esc(st.intro)}</p>` : ''}${st.kpis ? kpis(st.kpis) : ''}<div class="cal">${st.days.map(d => `<div class="day"><h5>${esc(d.d)}</h5>${d.ev.map(e => `<div class="ev ${esc(e[1] || '')}">${rich(e[0])}</div>`).join('')}</div>`).join('')}</div>`;
  frame(st, body);
};

K.done = st => {
  const yes = S.docs.filter(d => d.state === 'yes').length, no = S.docs.filter(d => d.state === 'no').length;
  const people = S.audit.filter(a => a.who !== 'Assistant').length, bot = S.audit.length - people;
  const next = C.next || ['Approved items move on in your own systems.', 'Items sent back return to the person who owns them, with the reason.', 'Every step above is kept as an audit trail.'];
  const body = `<div class="done-box"><div class="big">✓</div><h2 style="margin:6px 0">${esc(Object.values(S.approved).includes('no') || allSentBack() ? 'Held: nothing was sent or saved' : C.outcome || 'Walkthrough complete')}</h2>
    <p style="color:var(--muted);margin:0">The assistant did the reading and preparing. ${esc(C.persona?.name || 'A person')} made every decision.</p></div>
    ${kpis([[C.docs.length, 'Items in this batch'], [yes, 'Approved by a person', 'ok'], [no, 'Sent back', no ? 'bad' : ''], [bot, 'Assistant steps'], [people, 'Human decisions', 'ok']])}
    <div class="split"><div><div class="sec-t">In a real setup</div><ul style="margin:0;padding-left:18px">${next.map(x => `<li>${rich(x)}</li>`).join('')}</ul></div>
    <div><div class="sec-t">Audit trail</div><ul class="audit">${auditRows(S.audit) || '<li>No events yet.</li>'}</ul></div></div>
    <div class="row" style="justify-content:center;margin-top:18px"><button class="btn pri" id="again">↺ Run it again</button></div>`;
  frame(st, body, {next: false});
  $('#act').style.display = 'none';
  S.done.add(S.i); renderSteps();
  $('#again').onclick = () => { reset(); go(0); };
};
K.unknown = st => frame(st, `<p>Unknown stage type “${esc(st.type)}”.</p>`);

reset(); shell(); go(0);
})();
