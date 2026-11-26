// 本機儲存：作答紀錄、收藏、偏好。Phase 6 會在這一層接上雲端同步。
const KEY = 'tes-v1';
const blank = () => ({ v: 1, attempts: [], bookmarks: [], prefs: { mode: 'light', fs: '17px', browse: false }, last: null });
let S = blank(); export let persistent = true;
try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(blank(), JSON.parse(raw)); } catch (e) { persistent = false; }
function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { persistent = false; } }
export const prefs = () => S.prefs;
export function setPref(k, v) { S.prefs[k] = v; save(); }
export function addAttempt(a) { S.attempts.push(Object.assign({ t: Date.now() }, a)); save(); }
export const attempts = () => S.attempts;
export function lastOf(qid) { for (let i = S.attempts.length - 1; i >= 0; i--) if (S.attempts[i].q === qid) return S.attempts[i]; return null; }
export function latestByQuestion() { const m = new Map(); for (const a of S.attempts) m.set(a.q, a); return m; }
export function wrongCount(qid) { return S.attempts.filter(a => a.q === qid && !a.ok).length; }
export const isBookmarked = q => S.bookmarks.includes(q);
export function toggleBookmark(q) { const i = S.bookmarks.indexOf(q); if (i >= 0) S.bookmarks.splice(i, 1); else S.bookmarks.push(q); save(); }
export const bookmarks = () => S.bookmarks;
export function setLast(l) { S.last = l; save(); }
export const getLast = () => S.last;
export function clearAttempts() { S.attempts = []; S.last = null; save(); }
