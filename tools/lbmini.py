# 런치보드 오른쪽: 개인별 청구액 요약 + 자세히 보기(현황판) — 공개용 패치
LBMINI_JS = r'''function lbMiniHTML() {
  var URL_BOARD = "https://hver-lunchboard.pages.dev/";
  var more = '<a class="lbmMore" href="' + URL_BOARD + '" target="_blank" rel="noopener">자세히 보기 ↗</a>';
  if (!LBD || !LBD.months) return '<div class="lbm"><div class="lbmHead"><b>이번 달 개인별 청구액</b>' + more + '</div><div class="lbmEmpty">현황판 데이터가 없습니다.</div></div>';
  var now = new Date(Date.now() + 9 * 3600 * 1000), cur = now.getUTCFullYear() + "-" + String(now.getUTCMonth() + 1).padStart(2, "0");
  var yms = Object.keys(LBD.months).sort(), ym = LBD.months[cur] ? cur : yms[yms.length - 1];
  var days = (LBD.months[ym] || {}).days || {}, tot = {}, cnt = {};
  Object.keys(days).forEach(function (k) { var e = days[k].entries || {}; Object.keys(e).forEach(function (id) { var v = (+e[id].lunch || 0) + (+e[id].drink || 0); if (v) { tot[id] = (tot[id] || 0) + v; cnt[id] = (cnt[id] || 0) + 1; } }); });
  var mem = (LBD.members || []).filter(function (m) { return m.active !== false || tot[m.id]; });
  var groups = [], gmap = {};
  mem.forEach(function (m) { if (!m.team && !tot[m.id]) return; var t = m.team || "기타"; if (!gmap[t]) { gmap[t] = []; groups.push(t); } gmap[t].push(m); });
  var all = 0, max = 1; mem.forEach(function (m) { all += tot[m.id] || 0; if ((tot[m.id] || 0) > max) max = tot[m.id]; });
  var sv = LBD.savedAt ? new Date(new Date(LBD.savedAt).getTime() + 9 * 3600 * 1000) : null;
  var svTxt = sv ? (sv.getUTCMonth() + 1) + "/" + sv.getUTCDate() + " " + String(sv.getUTCHours()).padStart(2, "0") + ":" + String(sv.getUTCMinutes()).padStart(2, "0") + " 기준" : "";
  var rows = groups.map(function (g) {
    var gs = 0; gmap[g].forEach(function (m) { gs += tot[m.id] || 0; });
    return '<div class="lbmTeam"><span>' + esc(g) + '</span><span class="num">' + gs.toLocaleString("ko-KR") + '원</span></div>' + gmap[g].map(function (m) {
      var v = tot[m.id] || 0;
      return '<div class="lbmRow"><span class="nm">' + esc(m.name) + '</span><span class="bar"><i style="width:' + Math.round(v / max * 100) + '%"></i></span><span class="v num">' + (v ? v.toLocaleString("ko-KR") + '원' : '<em>—</em>') + '</span><span class="d num">' + (cnt[m.id] ? cnt[m.id] + '일' : '') + '</span></div>';
    }).join("");
  }).join("");
  return '<div class="lbm"><div class="lbmHead"><div><b>' + (+ym.slice(5)) + '월 개인별 청구액</b><small>' + esc(svTxt) + '</small></div>' + more + '</div>' +
    '<div class="lbmTotal"><span>이번 달 합계</span><b class="num">' + all.toLocaleString("ko-KR") + '<small>원</small></b></div>' + rows +
    '<p class="lbmNote">청구액 = 점심 + 음료. 일별 내역·잔액은 「자세히 보기」에서 볼 수 있어요.</p></div>';
}
'''
LBMINI_CSS = ('.lbm{border:1px solid #dfe3dc;border-radius:14px;background:#fff;padding:16px 18px;margin-bottom:16px}'
 '.lbmHead{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:10px}'
 '.lbmHead b{font-size:16px;display:block}.lbmHead small{font-size:12px;color:#6b7570}'
 '.lbmMore{flex:none;background:#c7801c;color:#fff;text-decoration:none;font-weight:700;font-size:13px;padding:8px 14px;border-radius:999px}'
 '.lbmTotal{display:flex;justify-content:space-between;align-items:baseline;background:#F2F4F1;border-radius:10px;padding:10px 12px;margin-bottom:6px}'
 '.lbmTotal b{font-size:22px}.lbmTotal small{font-size:12px;margin-left:2px;color:#6b7570}'
 '.lbmTeam{display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:#6b7570;padding:12px 2px 4px;border-bottom:1px solid #e4e9e3}'
 '.lbmRow{display:grid;grid-template-columns:64px 1fr 92px 34px;gap:8px;align-items:center;padding:7px 2px;border-bottom:1px solid #f0f2ef;font-size:14px}'
 '.lbmRow .nm{font-weight:600}.lbmRow .bar{height:8px;background:#eef1ed;border-radius:4px;overflow:hidden}.lbmRow .bar i{display:block;height:100%;background:#c7801c;border-radius:4px}'
 '.lbmRow .v{text-align:right;font-weight:700}.lbmRow .v em{color:#aab2ad;font-style:normal;font-weight:400}.lbmRow .d{text-align:right;font-size:12px;color:#6b7570}'
 '.lbmNote{font-size:12px;color:#6b7570;margin:10px 0 0}.lbmEmpty{color:#6b7570;padding:20px 0;text-align:center}')
PATCHES = [
  ('if(p.id==="lunchboard") h += lunchFrameHTML();', 'if(p.id==="lunchboard") h += lbMiniHTML();'),
  ('function lunchFrameHTML() {', LBMINI_JS + 'function lunchFrameHTML() {'),
  ('.lbx{border-radius:14px;', LBMINI_CSS + '.lbx{border-radius:14px;'),
]
def apply(s):
    for a,b in PATCHES:
        if b.split('(')[0] in s and a not in s: continue
        assert s.count(a)==1, a[:60]
        s=s.replace(a,b)
    return s
