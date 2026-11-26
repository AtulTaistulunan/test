import * as store from './store.js';
import * as repo from './repo.js';
import { unitStatus } from './mastery.js';

const $ = (s, r = document) => r.querySelector(s);
const E = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const NAV = [['dash', '學習總覽'], ['notes', '知識筆記'], ['tree', '知識探索'], ['practice', '章節練習'], ['compose', '自訂組卷', 'Phase 4'], ['mock', '模擬測驗', 'Phase 4'],
  ['recall', '主動回憶'], ['wrong', '錯題與收藏'], ['scholar', '學者索引', 'Phase 2'], ['cram', '考前重點']];
const NAMES = Object.fromEntries(NAV.map(n => [n[0], n[1]]));
const CONF = { hi: '非常確定', mid: '不太確定', lo: '猜測作答' };
let route = { view: 'dash', unit: null };
let quiz = { unit: null, i: 0, sel: null, conf: null, done: false };
let filter = '';
const main = $('#main'), aside = $('#aside'), nav = $('#nav');

// ---------- 路由：只用 #名稱，單元代碼是穩定的 ----------
function parse() {
  const h = location.hash.replace(/^#/, '');
  const m = /^(notes|practice)-(.+)$/.exec(h);
  if (m) return { view: m[1], unit: m[2] };
  return { view: NAMES[h] ? h : 'dash', unit: null };
}
const href = (v, u) => '#' + v + (u ? '-' + u : '');

// ---------- 共用 ----------
function statusOf(u, unitData) {
  // 沒載入題目清單時，以作答紀錄中的單元欄位估算
  const latest = store.latestByQuestion();
  const ids = unitData ? unitData.questions.map(q => q.id) : [...latest.values()].filter(a => a.u === u.id).map(a => a.q);
  return unitStatus(ids, latest);
}
function pill(st) { return `<span class="pill ${st.cls}">${st.label}</span>`; }
function ask(msg) { return new Promise(res => { const d = $('#dlg'); $('#dlgmsg').textContent = msg; d.showModal(); $('#dlgyes').onclick = () => { d.close(); res(true); }; $('#dlgno').onclick = () => { d.close(); res(false); }; }); }
function setAside(html) { document.body.classList.toggle('noaside', !html); aside.innerHTML = html || ''; }
function crumb(parts) { $('#crumb').textContent = parts.filter(Boolean).join(' ／ '); document.title = parts[parts.length - 1] + '｜教檢研習室'; }

function renderNav() {
  const idx = repo.getIndex();
  let h = NAV.map(n => `<a class="item" href="${href(n[0])}"${route.view === n[0] && !route.unit ? ' aria-current="page"' : (route.view === n[0] ? ' aria-current="page"' : '')}>${n[1]}${n[2] ? `<span class="later">${n[2]}</span>` : ''}</a>`).join('');
  const target = route.view === 'practice' ? 'practice' : 'notes';
  h += '<h6>單元目錄</h6>';
  for (const s of repo.tree()) {
    const openS = route.unit && repo.unitMeta(route.unit)?.subject === s.id;
    h += `<details${openS || filter ? ' open' : ''}><summary>${E(s.name)}</summary>`;
    for (const g of s.groups) {
      const us = g.units.filter(u => (!filter || u.title.includes(filter) || g.name.includes(filter)) && (target === 'notes' || u.questions));
      if (!us.length) continue;
      const openG = us.some(u => u.id === route.unit);
      h += `<details${openG || filter ? ' open' : ''}><summary>${E(g.name)}</summary>` + us.map(u => `<a class="u" href="${href(target, u.id)}"${u.id === route.unit ? ' aria-current="page"' : ''}>${E(u.title)}</a>`).join('') + '</details>';
    }
    h += '</details>';
  }
  nav.innerHTML = h;
}

// ---------- 各頁面 ----------
function viewDash() {
  const idx = repo.getIndex(), latest = store.latestByQuestion();
  const n = latest.size, ok = [...latest.values()].filter(a => a.ok).length, wrong = n - ok, last = store.getLast();
  crumb(['學習總覽']); setAside('');
  const recent = []; for (const a of [...store.attempts()].reverse()) { if (a.u && !recent.includes(a.u)) recent.push(a.u); if (recent.length >= 4) break; }
  main.innerHTML = `<div class="wide"><h1>學習總覽</h1>
  <p class="meta">數字都來自這台裝置上的實際作答紀錄${store.persistent ? '' : '；這個瀏覽器無法儲存紀錄，關閉後會消失'}。</p>
  <div class="grid">
    <div class="card stat"><b>${idx.totals.questions}</b><span>題庫總數（AI 生成練習題）</span></div>
    <div class="card stat"><b>${n}</b><span>已作答題數</span></div>
    <div class="card stat"><b>${Math.round(n / idx.totals.questions * 100)}%</b><span>題庫完成率</span></div>
    <div class="card stat"><b>${n ? Math.round(ok / n * 100) + '%' : '—'}</b><span>作答正確率${n && n < 10 ? '（樣本少）' : ''}</span></div>
    <div class="card stat"><b>${wrong}</b><span>待訂正錯題</span></div>
  </div>
  ${n ? '' : '<p class="empty" style="margin-top:16px">還沒有作答紀錄。從「章節練習」選一個單元開始，這裡就會出現你的進度。</p>'}
  <h2>繼續學習</h2>
  ${last && repo.unitMeta(last.unit) ? `<div class="card"><b>${E(repo.unitMeta(last.unit).title)}</b><div class="meta" style="margin:4px 0 0">上次停在${last.view === 'practice' ? '練習第 ' + (last.i + 1) + ' 題' : '知識筆記'}</div><div class="actions"><a class="primary" href="${href(last.view, last.unit)}">繼續</a></div></div>` : '<p class="empty">尚無上次學習的位置。</p>'}
  ${recent.length ? '<h2>最近練習的單元</h2><div class="ulist">' + recent.map(id => { const u = repo.unitMeta(id); return u ? `<a class="urow" href="${href('notes', id)}"><b>${E(u.title)}</b>${pill(statusOf(u))}<span class="n">${u.questions} 題</span></a>` : ''; }).join('') + '</div>' : ''}
  <h2>學習模式</h2><div class="actions"><a class="ghost" href="#notes">知識筆記</a><a class="ghost" href="#practice">章節練習</a><a class="ghost" href="#recall">主動回憶</a><a class="ghost" href="#wrong">錯題與收藏</a><a class="ghost" href="#cram">考前重點</a></div>
  <h2>紀錄管理</h2><div class="actions"><button class="ghost" id="clear"${n ? '' : ' disabled'}>清除全部作答紀錄</button></div></div>`;
  const c = $('#clear'); if (c) c.onclick = async () => { if (await ask(`確定清除 ${store.attempts().length} 筆作答紀錄？這個動作無法復原，收藏不受影響。`)) { store.clearAttempts(); render(); } };
}
function unitList(view, title, lead, pred) {
  crumb([title]); setAside('');
  let h = `<div class="wrap"><h1>${title}</h1><p class="meta">${lead}</p>`;
  for (const s of repo.tree()) for (const g of s.groups) {
    const us = g.units.filter(u => pred(u) && (!filter || u.title.includes(filter) || g.name.includes(filter)));
    if (!us.length) continue;
    h += `<h3>${E(g.name)}<span class="pill" style="margin-left:8px">${E(s.name)}</span></h3><div class="ulist">` + us.map(u => `<a class="urow" href="${href(view, u.id)}"><b>${E(u.title)}</b>${u.questions ? pill(statusOf(u)) : ''}<span class="n">${view === 'recall' ? u.recall + ' 則' : (u.questions ? u.questions + ' 題' : '')}</span></a>`).join('') + '</div>';
  }
  main.innerHTML = h + '</div>';
}
async function viewNotes(uid) {
  const u = repo.unitMeta(uid), d = await repo.loadUnit(uid), s = repo.getIndex().subjects.find(x => x.id === u.subject);
  crumb(['知識筆記', u.group, u.title]); store.setLast({ view: 'notes', unit: uid, i: 0 });
  main.innerHTML = `<div class="${d.notesHtml.includes('kgrid') || d.notesHtml.includes('<table') ? 'wide' : 'wrap'}"><h1>${E(u.title)}</h1>
  <div class="meta"><span>${E(s.name)}</span><span>${E(u.group)}</span>${u.questions ? pill(statusOf(u, d)) : ''}</div>
  ${u.questions ? `<div class="tabs"><a href="${href('notes', uid)}" aria-current="page">知識筆記</a><a href="${href('practice', uid)}">練習 ${u.questions} 題</a></div>` : ''}
  <section class="notes" id="s-notes">${d.notesHtml || '<p class="empty">尚未整理。原筆記沒有這個主題的內容，可先練習題目，解析中有關鍵字與口訣。</p>'}</section>
  ${d.recall.length ? `<h2 id="s-recall">情境回憶考點</h2><p class="meta">先自己說出考點，再按「顯示考點」。這 ${d.recall.length} 則只有情境與考點，沒有選項。</p><div class="recall">${d.recall.map(recallCard).join('')}</div>` : ''}
  ${u.questions ? `<h2 id="s-q">對應練習題</h2><p>這個單元有 ${u.questions} 題練習題。</p><div class="actions"><a class="primary" href="${href('practice', uid)}">開始練習</a></div>` : ''}</div>`;
  setAside(`<h6>本頁目錄</h6><p><a href="#s-notes" data-jump="s-notes">知識筆記</a>${d.recall.length ? '<br><a href="#s-recall" data-jump="s-recall">情境回憶考點</a>' : ''}${u.questions ? '<br><a href="#s-q" data-jump="s-q">對應練習題</a>' : ''}</p>${u.questions ? '<h6>掌握程度</h6><p>' + pill(statusOf(u, d)) + '</p><p style="color:var(--text2)">暫定規則：作答未滿 5 題不判定。</p>' : ''}<h6>資料來源</h6><p style="color:var(--text2)">尚未整理。內容整理自 AI 生成的筆記與題庫，標「補充」者為另外補上。</p>`);
}
function recallCard(r) { return `<div class="rc"><span class="rid">${E(r.id)}${r.flagged ? '<span class="flag">易錯</span>' : ''}</span><div>${r.situation}</div><button class="ghost" data-reveal>顯示考點</button><div class="ansr" hidden>${r.concept}${r.tip ? `<div class="diag"><mark>${r.tip}</mark></div>` : ''}</div></div>`; }
async function viewRecall() {
  const us = repo.getIndex().units.filter(u => u.recall); crumb(['主動回憶']); setAside('');
  const ds = await Promise.all(us.map(u => repo.loadUnit(u.id)));
  main.innerHTML = `<div class="wrap"><h1>主動回憶</h1><p class="meta">先看情境，自己回想考點，再揭示。共 ${ds.reduce((n, d) => n + d.recall.length, 0)} 則；間隔複習排程不在開發範圍內。</p>` +
    ds.map((d, i) => `<h3>${E(us[i].title)}</h3><div class="recall">${d.recall.map(recallCard).join('')}</div>`).join('') + '</div>';
}
async function viewPractice(uid) {
  const u = repo.unitMeta(uid), d = await repo.loadUnit(uid), qs = d.questions;
  if (!qs.length) { location.hash = href('notes', uid); return; }
  if (quiz.unit !== uid) { const l = store.getLast(); quiz = { unit: uid, i: l && l.unit === uid && l.view === 'practice' ? Math.min(l.i, qs.length - 1) : 0, sel: null, conf: null, done: false }; }
  const q = qs[quiz.i], prev = store.lastOf(q.id), browse = store.prefs().browse, shown = quiz.done || browse;
  crumb(['章節練習', u.group, u.title]); store.setLast({ view: 'practice', unit: uid, i: quiz.i });
  let h = `<div class="wrap"><div class="tabs"><a href="${href('notes', uid)}">知識筆記</a><a href="${href('practice', uid)}" aria-current="page">練習 ${qs.length} 題</a></div>
  <div class="qhead"><span>${E(u.title)}｜第 ${quiz.i + 1} / ${qs.length} 題</span><div class="bar"><i style="width:${(quiz.i + 1) / qs.length * 100}%"></i></div><span class="pill">${q.id}・練習題（AI 生成）</span>${q.neg ? '<span class="pill neg">否定題</span>' : ''}</div>
  <p class="stem">${q.stem}</p><div role="radiogroup" aria-label="選項">`;
  for (const k of Object.keys(q.opts)) {
    let cls = '', mark = '';
    if (shown) { if (k === q.ans) { cls = ' right'; mark = '✓ 題庫答案' + (quiz.sel === k ? '・你的選擇' : ''); } else if (k === quiz.sel && quiz.done) { cls = ' wrong'; mark = '✗ 你的選擇'; } }
    h += `<button class="opt${cls}" role="radio" aria-checked="${quiz.sel === k}" data-k="${k}"${quiz.done ? ' disabled' : ''}><span class="k">${k}</span><span>${q.opts[k]}</span>${mark ? `<span class="mark">${mark}</span>` : ''}</button>`;
  }
  h += '</div>';
  if (!quiz.done && !browse) h += `<div class="conf"><span>作答信心（可不填）</span>${Object.entries(CONF).map(([c, t]) => `<button data-c="${c}" aria-pressed="${quiz.conf === c}">${t}</button>`).join('')}</div>
    <div class="actions"><button class="primary" id="confirm"${quiz.sel ? '' : ' disabled'}>確認答案</button><button class="ghost" id="bm" aria-pressed="${store.isBookmarked(q.id)}">${store.isBookmarked(q.id) ? '★ 已收藏' : '☆ 收藏'}</button></div>${prev ? `<p class="diag">上次作答：${prev.ok ? '答對' : '答錯'}</p>` : ''}`;
  if (shown) {
    const ok = quiz.sel === q.ans, c = quiz.conf;
    const d2 = !quiz.done ? '' : ok ? (c === 'hi' ? '答對且有把握。' : c ? '答對但信心不高：這個概念可能還不穩定。' : '') : (c === 'hi' ? '很確定卻答錯：可能有迷思概念，建議回頭看筆記。這只是單次作答的提示。' : c ? '答錯且信心不高：可能是知識不足。' : '');
    h += `<div class="expl"><h3>${quiz.done ? (ok ? '✓ 答對了' : '✗ 答錯了') + '　' : ''}題庫答案：${q.ans}</h3>${q.expl.map(([l, t]) => `<p><span class="el">${E(l)}</span>${t}</p>`).join('')}${d2 ? `<div class="diag">${d2}</div>` : ''}<div class="diag">逐選項解析：尚未整理</div></div>
    <div class="actions"><a class="ghost" href="${href('notes', uid)}">回到知識筆記</a><button class="ghost" id="bm" aria-pressed="${store.isBookmarked(q.id)}">${store.isBookmarked(q.id) ? '★ 已收藏' : '☆ 收藏'}</button>${quiz.i > 0 ? '<button class="ghost" id="prevq">上一題</button>' : ''}${quiz.i < qs.length - 1 ? '<button class="primary" id="nextq">下一題</button>' : '<a class="primary" href="#dash">完成，回學習總覽</a>'}</div>`;
  }
  const idxHtml = `<div class="qidx">${qs.map((x, i) => { const l = store.lastOf(x.id); return `<button data-i="${i}"${i === quiz.i ? ' aria-current="true"' : ''} class="${l ? (l.ok ? 'r' : 'w') : ''}" aria-label="第 ${i + 1} 題${l ? (l.ok ? '，已答對' : '，已答錯') : '，未作答'}">${i + 1}${l ? (l.ok ? '✓' : '✗') : ''}</button>`; }).join('')}</div>`;
  h += `<div class="inline-idx"><h3>題號</h3>${idxHtml}</div></div>`;
  main.innerHTML = h;
  setAside(`<h6>題號</h6>${idxHtml}<h6 style="margin-top:18px">瀏覽模式</h6><p><label><input type="checkbox" id="browse"${browse ? ' checked' : ''}> 直接顯示答案與解析</label><br><span style="color:var(--text2)">開啟時不記錄作答。</span></p><h6>快捷鍵</h6><p>A B C D 選擇<br>Enter 確認<br>← → 換題</p>`);
}
function confirmAns(d) { const q = d.questions[quiz.i]; if (!quiz.sel || quiz.done || store.prefs().browse) return; quiz.done = true; store.addAttempt({ q: q.id, u: quiz.unit, sel: quiz.sel, ok: quiz.sel === q.ans, conf: quiz.conf }); render(); }
function moveQ(n, len) { const i = quiz.i + n; if (i < 0 || i >= len) return; quiz = { unit: quiz.unit, i, sel: null, conf: null, done: false }; render(); main.scrollTop = 0; }
async function viewWrong() {
  crumb(['錯題與收藏']); setAside('');
  const latest = store.latestByQuestion(), wrong = [...latest.values()].filter(a => !a.ok), bms = store.bookmarks();
  const need = new Set([...wrong.map(a => a.u), ...bms.map(id => (store.attempts().find(a => a.q === id) || {}).u)].filter(Boolean));
  const data = new Map(); for (const u of need) for (const q of (await repo.loadUnit(u)).questions) data.set(q.id, { q, u });
  const strip = s => s.replace(/<[^>]+>/g, '');
  const row = (id, extra) => { const x = data.get(id); if (!x) return `<div class="wq"><b>${E(id)}</b><small>${extra}</small></div>`; return `<div class="wq"><b>${E(id)}</b>　${E(strip(x.q.stem).slice(0, 70))}…<small>${extra}｜<a href="${href('practice', x.u)}" data-goto="${id}">重新練習</a>｜<a href="${href('notes', x.u)}">知識筆記</a></small></div>`; };
  main.innerHTML = `<div class="wrap"><h1>錯題與收藏</h1><p class="meta">錯因分類與訂正內容排在 Phase 4。答對後歷史錯誤次數仍會保留。</p>
  <h2>待訂正錯題（${wrong.length}）</h2>${wrong.length ? '<div class="card">' + wrong.map(a => row(a.q, `你選 ${a.sel}，題庫答案 ${data.get(a.q)?.q.ans ?? '—'}${a.conf ? '｜信心：' + CONF[a.conf] : ''}｜累計答錯 ${store.wrongCount(a.q)} 次`)).join('') + '</div>' : '<p class="empty">目前沒有錯題。最近一次作答答錯的題目會出現在這裡。</p>'}
  <h2>收藏（${bms.length}）</h2>${bms.length ? '<div class="card">' + bms.map(id => row(id, '已收藏')).join('') + '</div>' : '<p class="empty">還沒有收藏的題目。在練習時按「收藏」即可加入。</p>'}</div>`;
}
function viewTree() {
  crumb(['知識探索']); setAside('');
  let h = '<div class="wide"><h1>知識探索</h1><p class="meta">目前提供階層式知識樹；比較矩陣、心智圖與時間軸排在 Phase 3。</p><div class="actions" style="margin:0 0 12px"><button class="ghost" id="exp">全部展開</button><button class="ghost" id="col">全部收合</button></div><div class="card" id="treebox">';
  for (const s of repo.tree()) {
    const tot = s.groups.reduce((n, g) => n + g.units.reduce((m, u) => m + u.questions, 0), 0);
    h += `<details open><summary style="cursor:pointer;min-height:44px;display:flex;align-items:center;font-size:18px"><b>${E(s.name)}</b><span class="pill" style="margin-left:auto">${tot} 題</span></summary>`;
    for (const g of s.groups) {
      const us = g.units.filter(u => !filter || u.title.includes(filter) || g.name.includes(filter)); if (!us.length) continue;
      h += `<details${filter ? ' open' : ''} style="margin-left:16px"><summary style="cursor:pointer;min-height:44px;display:flex;align-items:center"><b>${E(g.name)}</b><span class="pill" style="margin-left:auto">${us.reduce((m, u) => m + u.questions, 0)} 題</span></summary><div class="ulist" style="margin:4px 0 10px 16px">` +
        us.map(u => `<a class="urow" href="${href('notes', u.id)}"><b>${E(u.title)}</b>${u.questions ? pill(statusOf(u)) : ''}<span class="n">${u.questions ? u.questions + ' 題' : '—'}</span></a>`).join('') + '</div></details>';
    }
    h += '</details>';
  }
  main.innerHTML = h + '</div></div>';
  $('#exp').onclick = () => main.querySelectorAll('details').forEach(d => d.open = true);
  $('#col').onclick = () => main.querySelectorAll('#treebox details details').forEach(d => d.open = false);
}
function later(v) { crumb([NAMES[v]]); setAside(''); main.innerHTML = `<div class="wrap"><h1>${NAMES[v]}</h1><p class="empty">這個功能排在 ${NAV.find(n => n[0] === v)[2]}，尚未開放。</p></div>`; }

async function render() {
  renderNav();
  try {
    const { view, unit } = route;
    if (unit && !repo.unitMeta(unit)) { main.innerHTML = '<div class="wrap"><h1>找不到這個單元</h1><p class="empty">連結可能已經過期。請從左側單元目錄重新選擇。</p></div>'; setAside(''); return; }
    if (view === 'dash') viewDash();
    else if (view === 'notes') unit ? await viewNotes(unit) : unitList('notes', '知識筆記', '選一個單元閱讀概念整理。', u => u.kind === 'unit');
    else if (view === 'practice') unit ? await viewPractice(unit) : unitList('practice', '章節練習', '選一個單元，一次作答一題；確認後才公布答案。', u => u.questions > 0);
    else if (view === 'cram') unitList('notes', '考前重點', '口訣、易混淆對照與其他總整理。', u => u.kind !== 'unit');
    else if (view === 'recall') await viewRecall();
    else if (view === 'wrong') await viewWrong();
    else if (view === 'tree') viewTree();
    else later(view);
  } catch (e) { main.innerHTML = `<div class="wrap"><h1>載入失敗</h1><p class="empty">${E(e.message)}。請確認網路後重新整理。</p></div>`; setAside(''); }
}

// ---------- 事件 ----------
document.addEventListener('click', async e => {
  const t = e.target; let x;
  if (t.id === 'menu' || t.id === 'scrim') { const mob = matchMedia('(max-width:760px)').matches; document.body.classList.toggle(mob ? 'navopen' : 'navclosed'); $('#menu').setAttribute('aria-expanded', mob ? document.body.classList.contains('navopen') : !document.body.classList.contains('navclosed')); return; }
  if (x = t.closest('[data-jump]')) { e.preventDefault(); document.getElementById(x.dataset.jump)?.scrollIntoView(); return; }
  if (x = t.closest('[data-reveal]')) { x.hidden = true; x.nextElementSibling.hidden = false; return; }
  if (x = t.closest('[data-goto]')) { e.preventDefault(); const u = x.getAttribute('href').replace('#practice-', ''); const d = await repo.loadUnit(u); quiz = { unit: u, i: Math.max(0, d.questions.findIndex(q => q.id === x.dataset.goto)), sel: null, conf: null, done: false }; if (location.hash === href('practice', u)) render(); else location.hash = href('practice', u); return; }
  if (route.view !== 'practice' || !route.unit) return;
  const d = await repo.loadUnit(route.unit);
  if (x = t.closest('.opt')) { if (!quiz.done) { quiz.sel = x.dataset.k; render(); } }
  else if (x = t.closest('[data-c]')) { quiz.conf = quiz.conf === x.dataset.c ? null : x.dataset.c; render(); }
  else if (t.id === 'confirm') confirmAns(d);
  else if (t.id === 'nextq') moveQ(1, d.questions.length);
  else if (t.id === 'prevq') moveQ(-1, d.questions.length);
  else if (t.id === 'bm') { store.toggleBookmark(d.questions[quiz.i].id); render(); }
  else if (x = t.closest('.qidx button')) { quiz = { unit: quiz.unit, i: +x.dataset.i, sel: null, conf: null, done: false }; render(); }
});
document.addEventListener('change', e => { if (e.target.id === 'browse') { store.setPref('browse', e.target.checked); quiz.sel = null; quiz.done = false; render(); } });
document.addEventListener('keydown', async e => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); $('#search').focus(); return; }
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  const tg = e.target.tagName; if (['INPUT', 'SELECT', 'TEXTAREA'].includes(tg) || $('#dlg').open || route.view !== 'practice' || !route.unit) return;
  const d = await repo.loadUnit(route.unit), k = e.key.toUpperCase();
  if (!quiz.done && k.length === 1 && 'ABCD'.includes(k)) { quiz.sel = k; render(); }
  else if (e.key === 'Enter' && !quiz.done && quiz.sel && tg !== 'BUTTON' && tg !== 'A') { e.preventDefault(); confirmAns(d); }
  else if (e.key === 'ArrowRight') moveQ(1, d.questions.length);
  else if (e.key === 'ArrowLeft') moveQ(-1, d.questions.length);
});
$('#search').addEventListener('input', function () { filter = this.value.trim(); if (!['notes', 'practice', 'tree', 'cram'].includes(route.view) || route.unit) { location.hash = '#notes'; } else render(); });
function applyPrefs() { const p = store.prefs(); document.documentElement.dataset.mode = p.mode; document.documentElement.style.setProperty('--fs', p.fs); $('#mode').value = p.mode; $('#fsz').value = p.fs; }
$('#mode').onchange = function () { store.setPref('mode', this.value); applyPrefs(); };
$('#fsz').onchange = function () { store.setPref('fs', this.value); applyPrefs(); };
window.addEventListener('hashchange', () => { route = parse(); document.body.classList.remove('navopen'); render().then(() => { main.scrollTop = 0; main.focus({ preventScroll: true }); }); });

applyPrefs();
repo.loadIndex().then(() => { route = parse(); render(); }).catch(() => { main.innerHTML = '<div class="wrap"><h1>載入失敗</h1><p class="empty">無法讀取題庫索引。請確認網路後重新整理。</p></div>'; });
