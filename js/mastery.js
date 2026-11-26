// 單元掌握狀態（暫定規則，Phase 5 會改以概念為單位並納入信心與近期表現）。
// 這是學習輔助指標，不是經心理計量驗證的能力分數。
export const CONFIG = { minSample: 5, familiar: 0.8 };
export function unitStatus(questionIds, latest) {
  const done = questionIds.map(id => latest.get(id)).filter(Boolean);
  if (!done.length) return { label: '尚未評估', cls: '' };
  if (done.length < CONFIG.minSample) return { label: `樣本不足（${done.length} 題）`, cls: '' };
  const rate = done.filter(a => a.ok).length / done.length;
  return rate >= CONFIG.familiar ? { label: '基本熟悉', cls: 'ok' } : { label: '待加強', cls: 'warn' };
}
