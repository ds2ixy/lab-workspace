# 런치보드(공개용): 개인별 청구액 목록 + 선택한 사람의 청구 내역(영수증) + 자세히 보기(현황판)
import re
LBMINI_JS = r'''/*LBM>*/var LBM = { sel: null, ym: null };
function lbmData() {
  if (!LBD || !LBD.months) return null;
  var now = new Date(Date.now() + 9 * 3600 * 1000), cur = now.getUTCFullYear() + "-" + String(now.getUTCMonth() + 1).padStart(2, "0");
  var yms = Object.keys(LBD.months).sort();
  if (!LBM.ym || !LBD.months[LBM.ym]) LBM.ym = LBD.months[cur] ? cur : yms[yms.length - 1];
  var ym = LBM.ym, days = (LBD.months[ym] || {}).days || {}, P = {};
  Object.keys(days).sort().forEach(function (k) {
    var d = days[k], e = d.entries || {};
    Object.keys(e).forEach(function (id) {
      var l = +e[id].lunch || 0, r = +e[id].drink || 0; if (!l && !r) return;
      var p = P[id] || (P[id] = { lunch: 0, drink: 0, days: [] });
      p.lunch += l; p.drink += r; p.days.push({ k: k, l: l, r: r, place: d.place || "", cafe: d.cafe || "", note: d.note || "" });
    });
  });
  var mem = (LBD.members || []).filter(function (m) { return P[m.id] || (m.active !== false && m.team); });
  var groups = [], G = {};
  mem.forEach(function (m) { var t = m.team || "기타"; if (!G[t]) { G[t] = []; groups.push(t); } G[t].push(m); });
  return { ym: ym, yms: yms, P: P, mem: mem, groups: groups, G: G };
}
function lbmWon(n) { return (+n || 0).toLocaleString("ko-KR"); }
function lbmSlip(D, m) {
  var p = D.P[m.id], WD = ["일", "월", "화", "수", "목", "금", "토"], mo = +D.ym.slice(5);
  var head = '<div class="lbmSlip"><h3>중식비 청구 내역</h3><div class="meta">' + D.ym.slice(0, 4) + '년 ' + mo + '월 · ' + esc(m.name) + (m.team ? ' · ' + esc(m.team) : '') + '</div><hr>';
  if (!p) return head + '<div class="lbmNone">이번 달 청구 내역이 없습니다.</div></div>';
  var rows = p.days.map(function (d) {
    var a = d.k.split("-").map(Number), w = WD[new Date(a[0], a[1] - 1, a[2]).getDay()];
    var pl = [d.place ? "식사 " + d.place : "", d.cafe ? "음료 " + d.cafe : "", d.note].filter(Boolean).join(" · ");
    return '<tr><td class="l"><b>' + a[1] + '/' + a[2] + ' (' + w + ')</b>' + (pl ? '<span>' + esc(pl) + '</span>' : '') + '</td><td>' + lbmWon(d.l) + '</td><td class="dr">' + lbmWon(d.r) + '</td><td class="t">' + lbmWon(d.l + d.r) + '</td></tr>';
  }).join("");
  return head + '<table><thead><tr><th class="l">날짜 · 장소</th><th>점심</th><th>음료</th><th>계</th></tr></thead><tbody>' + rows + '</tbody></table><hr>' +
    '<div class="sub"><span>점심 ' + lbmWon(p.lunch) + ' · 음료 ' + lbmWon(p.drink) + '</span><span>' + p.days.length + '일</span></div>' +
    '<div class="grand"><span>청구 합계</span><b class="num">' + lbmWon(p.lunch + p.drink) + '<small>원</small></b></div></div>';
}
function lbmLive() {
  if (window.__lbmLive) return; window.__lbmLive = 1;
  try {
    fetch("https://hver-lunchboard.pages.dev/data.json?t=" + Date.now(), { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
      if (!d || !d.months || !d.members) return;
      if (LBD && LBD.savedAt && d.savedAt && new Date(d.savedAt) < new Date(LBD.savedAt)) return;
      LBD = d; LBM.live = 1;
      var el = document.querySelector(".lbm"); if (!el) return; var w = document.createElement("div"); w.innerHTML = lbMiniHTML(); el.replaceWith(w.firstChild);
    }).catch(function () {});
  } catch (e) {}
}
function lbMiniHTML() {
  lbmLive();
  if (!window.__lbmOn) { window.__lbmOn = 1; document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-lbm]"); if (!b) return;
    var v = b.getAttribute("data-lbm");
    if (v === "prev" || v === "next") { var D0 = lbmData(), i = D0.yms.indexOf(D0.ym) + (v === "prev" ? -1 : 1); if (i < 0 || i >= D0.yms.length) return; LBM.ym = D0.yms[i]; }
    else LBM.sel = v;
    var el = document.querySelector(".lbm"); if (!el) return; var w = document.createElement("div"); w.innerHTML = lbMiniHTML(); el.replaceWith(w.firstChild);
  }); }
  var URL_BOARD = "https://hver-lunchboard.pages.dev/";
  var more = '<a class="lbmMore" href="' + URL_BOARD + '" target="_blank" rel="noopener">자세히 보기 ↗</a>';
  var D = lbmData();
  if (!D) return '<div class="lbm"><div class="lbmTop"><b>개인별 청구액</b>' + more + '</div><div class="lbmNone">현황판 데이터가 없습니다.</div></div>';
  var all = 0, lunch = 0, drink = 0, n = 0, max = 1;
  D.mem.forEach(function (m) { var p = D.P[m.id]; if (!p) return; n++; lunch += p.lunch; drink += p.drink; if (p.lunch + p.drink > max) max = p.lunch + p.drink; });
  all = lunch + drink;
  if (!LBM.sel || !D.mem.some(function (m) { return m.id === LBM.sel; })) { var f = D.mem.filter(function (m) { return D.P[m.id]; })[0] || D.mem[0]; LBM.sel = f ? f.id : null; }
  var sv = LBD.savedAt ? new Date(new Date(LBD.savedAt).getTime() + 9 * 3600 * 1000) : null;
  var svTxt = sv ? (sv.getUTCMonth() + 1) + "/" + sv.getUTCDate() + " " + String(sv.getUTCHours()).padStart(2, "0") + ":" + String(sv.getUTCMinutes()).padStart(2, "0") + " 기준" : "";
  var i = D.yms.indexOf(D.ym), mo = +D.ym.slice(5);
  var top = '<div class="lbmTop"><div class="lbmMon"><button data-lbm="prev" aria-label="이전 달"' + (i <= 0 ? ' disabled' : '') + '>‹</button><b>' + D.ym.slice(0, 4) + '년 ' + mo + '월</b><button data-lbm="next" aria-label="다음 달"' + (i >= D.yms.length - 1 ? ' disabled' : '') + '>›</button><small>' + esc(svTxt) + (LBM.live ? ' · <span class="lbmLiveTag">● 실시간</span>' : '') + '</small></div>' + more + '</div>';
  var tiles = '<div class="lbmTiles"><div class="tl main"><span>이번 달 청구 합계</span><b class="num">' + lbmWon(all) + '<small>원</small></b></div>' +
    '<div class="tl"><span>점심</span><b class="num">' + lbmWon(lunch) + '<small>원</small></b></div>' +
    '<div class="tl dr"><span>음료</span><b class="num">' + lbmWon(drink) + '<small>원</small></b></div>' +
    '<div class="tl"><span>청구 인원</span><b class="num">' + n + '<small>명</small></b></div></div>';
  var list = D.groups.map(function (g) {
    var gs = 0; D.G[g].forEach(function (m) { var p = D.P[m.id]; if (p) gs += p.lunch + p.drink; });
    return '<div class="lbmGrp"><div class="gh"><span>' + esc(g) + ' <em>' + D.G[g].length + '명</em></span><b class="num">' + lbmWon(gs) + '원</b></div>' + D.G[g].map(function (m) {
      var p = D.P[m.id], v = p ? p.lunch + p.drink : 0;
      return '<button class="lbmP' + (m.id === LBM.sel ? ' on' : '') + '" data-lbm="' + esc(m.id) + '"><span class="nm">' + esc(m.name) + '</span><span class="bar"><i style="width:' + Math.round(v / max * 100) + '%"></i></span><span class="v num">' + (v ? lbmWon(v) + '원' : '—') + '</span><span class="d num">' + (p ? p.days.length + '일' : '') + '</span></button>';
    }).join("") + '</div>';
  }).join("");
  var sel = D.mem.filter(function (m) { return m.id === LBM.sel; })[0];
  return '<div class="lbm">' + top + tiles + '<div class="lbmBody"><div class="lbmList"><div class="lbmCap">개인별 청구액 <small>이름을 누르면 청구 내역이 보여요</small></div>' + list + '</div>' +
    '<div class="lbmSide">' + (sel ? lbmSlip(D, sel) : '') + '</div></div>' +
    '<p class="lbmNote">청구액 = 점심 + 음료 · 입금·잔액과 일별 전체 내역은 「자세히 보기」에서 볼 수 있어요.</p></div>';
}
/*<LBM*/
'''
LBMINI_CSS = ('/*LBM>*/'
 '.lbm{--a:#c7801c;--dr:#9A5A16;--ln:#e4e9e3;--mu:#6b7570;border:1px solid #dfe3dc;border-radius:16px;background:#fff;padding:18px 20px 16px;margin-bottom:16px}'
 '.lbmTop{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:14px}'
 '.lbmMon{display:flex;align-items:center;gap:6px;flex-wrap:wrap}.lbmMon b{font-size:18px;min-width:104px;text-align:center}'
 '.lbmMon button{width:30px;height:30px;border-radius:50%;border:1px solid var(--ln);background:#fff;font-size:16px;line-height:1;cursor:pointer}.lbmMon button:disabled{opacity:.35;cursor:default}'
 '.lbmMon small{font-size:12px;color:var(--mu);margin-left:6px}'
 '.lbmMore{flex:none;background:var(--a);color:#fff;text-decoration:none;font-weight:700;font-size:13px;padding:9px 16px;border-radius:999px}.lbmMore:hover{filter:brightness(.95)}'
 '.lbmTiles{display:grid;grid-template-columns:1.4fr 1fr 1fr .8fr;gap:10px;margin-bottom:18px}'
 '.lbmTiles .tl{background:#F5F6F3;border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:2px;min-width:0}'
 '.lbmTiles .tl span{font-size:12px;color:var(--mu);font-weight:600}.lbmTiles .tl b{font-size:20px;white-space:nowrap}.lbmTiles .tl small{font-size:12px;color:var(--mu);margin-left:2px;font-weight:500}'
 '.lbmTiles .tl.main{background:#FBF1E3}.lbmTiles .tl.main b{font-size:26px;color:#8a5410}.lbmTiles .tl.dr b{color:var(--dr)}'
 '.lbmBody{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(300px,1fr);gap:18px;align-items:start}'
 '.lbmCap{font-weight:700;font-size:15px;margin-bottom:4px}.lbmCap small{font-weight:500;font-size:12px;color:var(--mu);margin-left:6px}'
 '.lbmGrp{margin-top:8px}.lbmGrp .gh{display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:var(--mu);padding:8px 4px 6px;border-bottom:1px solid var(--ln)}.lbmGrp .gh em{font-style:normal;font-weight:500}'
 '.lbmP{width:100%;display:grid;grid-template-columns:62px minmax(40px,1fr) 88px 32px;gap:8px;align-items:center;padding:8px 6px;border:0;border-bottom:1px solid #f0f2ef;background:none;font:inherit;font-size:14px;text-align:left;cursor:pointer;border-radius:8px}'
 '.lbmP:hover{background:#faf6ef}.lbmP.on{background:#FBF1E3;box-shadow:inset 3px 0 0 var(--a)}'
 '.lbmP .nm{font-weight:600}.lbmP .bar{height:8px;background:#eef1ed;border-radius:4px;overflow:hidden}.lbmP .bar i{display:block;height:100%;background:var(--a);border-radius:4px}'
 '.lbmP .v{text-align:right;font-weight:700}.lbmP .d{text-align:right;font-size:12px;color:var(--mu)}'
 '.lbmSide{position:sticky;top:12px}'
 '.lbmSlip{background:#fff;border:1px solid var(--ln);border-radius:6px;padding:18px 16px 24px;box-shadow:0 6px 18px rgba(30,40,30,.07);'
 '-webkit-mask:radial-gradient(circle 5px at 50% 100%,transparent 98%,#000) 0 0/14px 100% repeat-x;mask:radial-gradient(circle 5px at 50% 100%,transparent 98%,#000) 0 0/14px 100% repeat-x}'
 '.lbmSlip h3{margin:0;text-align:center;font-size:18px}.lbmSlip .meta{text-align:center;font-size:12px;color:var(--mu);margin-top:3px}'
 '.lbmSlip hr{border:0;border-top:1px dashed #d6dcd5;margin:12px 0}'
 '.lbmSlip table{width:100%;border-collapse:collapse;font-size:13px;font-variant-numeric:tabular-nums}'
 '.lbmSlip th{background:#EEF1EC;color:var(--mu);font-weight:600;font-size:11px;padding:6px;text-align:right}.lbmSlip th.l,.lbmSlip td.l{text-align:left}'
 '.lbmSlip td{padding:7px 6px;text-align:right;vertical-align:top;border-bottom:1px solid #f3f5f2}.lbmSlip td.l span{display:block;font-size:11px;color:var(--mu);margin-top:1px}'
 '.lbmSlip td.dr{color:var(--dr)}.lbmSlip td.t{font-weight:700}'
 '.lbmSlip .sub{display:flex;justify-content:space-between;font-size:12px;color:var(--mu)}'
 '.lbmSlip .grand{display:flex;justify-content:space-between;align-items:baseline;margin-top:8px;font-weight:700}.lbmSlip .grand b{font-size:24px}.lbmSlip .grand small{font-size:13px;margin-left:2px}'
 '.lbmLiveTag{color:#2f8f5b;font-weight:700}'
 '.lbmNone{color:var(--mu);padding:24px 0;text-align:center}.lbmNote{font-size:12px;color:var(--mu);margin:14px 0 0}'
 '@media (max-width:900px){.lbmBody{grid-template-columns:minmax(0,1fr)}.lbmSide{position:static}.lbmTiles{grid-template-columns:1fr 1fr}}'
 '/*<LBM*/')
KICK_A = """'<span class="sumK" style="color:'+c+'">'+esc(S.kicker||p.group)+'</span>'+"""
KICK_B = """(p.id==="lunchboard"?'':'<span class="sumK" style="color:'+c+'">'+esc(S.kicker||p.group)+'</span>')+"""
def apply(s):
    # 이전에 넣은 패치(표시가 있든 없든) 제거 후 다시 넣기
    s = re.sub(r'/\*LBM>\*/.*?/\*<LBM\*/\n?', '', s, flags=re.S)
    s = re.sub(r'function lbMiniHTML\(\) \{.*?\n\}\n', '', s, count=1, flags=re.S)
    s = re.sub(r'\.lbm\{border:1px solid #dfe3dc.*?(?=\.lbx\{border-radius:14px;)', '', s, count=1, flags=re.S)
    s = s.replace('if(p.id==="lunchboard") h += lbMiniHTML();', 'if(p.id==="lunchboard") h += lunchFrameHTML();')
    for a, b in [('if(p.id==="lunchboard") h += lunchFrameHTML();', 'if(p.id==="lunchboard") h += lbMiniHTML();'),
                 ('function lunchFrameHTML() {', LBMINI_JS + 'function lunchFrameHTML() {'),
                 ('.lbx{border-radius:14px;', LBMINI_CSS + '.lbx{border-radius:14px;')]:
        assert s.count(a) == 1, a[:60]
        s = s.replace(a, b)
    if KICK_A in s: s = s.replace(KICK_A, KICK_B)
    return s
