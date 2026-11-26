// 資料讀取：單元索引一次載入，各單元內容用到才載入。
let index = null; const cache = new Map();
export async function loadIndex() { if (!index) index = await (await fetch('data/index.json')).json(); return index; }
export const getIndex = () => index;
export const unitMeta = id => index.units.find(u => u.id === id);
export async function loadUnit(id) {
  if (!cache.has(id)) cache.set(id, fetch(`data/units/${id}.json`).then(r => { if (!r.ok) throw new Error('找不到單元 ' + id); return r.json(); }));
  return cache.get(id);
}
export function tree() { // 考科 → 群組 → 單元
  return index.subjects.map(s => { const groups = []; for (const u of index.units.filter(u => u.subject === s.id)) { let g = groups.find(g => g.name === u.group); if (!g) groups.push(g = { name: u.group, units: [] }); g.units.push(u); } return { ...s, groups }; });
}
