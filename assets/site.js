// Republic City MC — shared bits for every page.
// ► SERVER ADDRESS: set it here once (e.g. 'play.republiccitymc.net') and every page updates.
//   Leave it '' to show "Address coming soon".
var RC_SERVER = { address: 'republiccitymc.play.minekube.net', version: '1.21.11' };

(function(){
  var addr = RC_SERVER.address;
  document.querySelectorAll('.js-ip').forEach(function(el){
    el.textContent = addr || 'Address coming soon';
    el.classList.toggle('tbd', !addr);
  });
  document.querySelectorAll('.js-ver').forEach(function(el){ el.textContent = RC_SERVER.version; });
  document.querySelectorAll('.js-copy').forEach(function(btn){
    if(!addr){ btn.disabled = true; btn.textContent = 'Coming soon'; return; }
    btn.addEventListener('click', function(){
      navigator.clipboard.writeText(addr).then(function(){
        btn.textContent = 'Copied!'; setTimeout(function(){ btn.textContent = 'Copy'; }, 1500);
      });
    });
  });
  // Live online / player count (only once a real address is set).
  var st = document.querySelectorAll('.js-status');
  if(!st.length) return;
  if(!addr){ st.forEach(function(el){ el.textContent = 'Opening for beta soon'; }); return; }
  fetch('https://api.mcsrvstat.us/3/' + encodeURIComponent(addr)).then(function(r){ return r.json(); }).then(function(d){
    st.forEach(function(el){
      el.classList.add(d.online ? 'on' : 'off');
      el.textContent = d.online ? ('Online · ' + d.players.online + '/' + d.players.max + ' players') : 'Offline right now';
    });
  }).catch(function(){ st.forEach(function(el){ el.textContent = 'Status unavailable'; }); });
})();

// Wiki search (top bar and sidebar): searches every page section plus the Field Guide's mobs and
// items (assets/search-index.js, built by tools/build.py). "/" focuses it; arrows + Enter pick.
(function(){
  var DATA = window.RC_SEARCH || [];
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function norm(s){ return String(s).toLowerCase(); }
  DATA.forEach(function(e){ e._h = norm(e.h); e._p = norm(e.p); e._x = norm(e.x); });
  function reEsc(s){ return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  // Terms match at the start of a word, so "tea" finds "teas" but not "steam".
  function search(q){
    var terms = norm(q).split(/\s+/).filter(Boolean);
    if(!terms.length) return [];
    var res = terms.map(function(t){ return new RegExp('(^|[^a-z0-9])' + reEsc(t), 'g'); });
    var out = [];
    DATA.forEach(function(e){
      var score = 0;
      for(var i = 0; i < res.length; i++){
        var re = res[i], s = 0, n;
        re.lastIndex = 0; if(re.test(e._h)) s += (e._h.indexOf(terms[i]) === 0 ? 14 : 10);
        re.lastIndex = 0; if(re.test(e._p)) s += 3;
        n = (e._x.match(re) || []).length; s += Math.min(n, 4);
        if(!s) return;
        score += s;
      }
      out.push({e: e, s: score});
    });
    out.sort(function(a, b){ return b.s - a.s; });
    return out.slice(0, 8).map(function(r){ return r.e; });
  }
  function snippet(e, q){
    var x = e.x, t = norm(q).split(/\s+/).filter(Boolean)[0] || '', i = t ? norm(x).indexOf(t) : -1;
    var start = Math.max(0, i - 40), s = (start ? '…' : '') + x.substr(start, 140) + (x.length > start + 140 ? '…' : '');
    s = esc(s);
    norm(q).split(/\s+/).filter(Boolean).forEach(function(w){
      s = s.replace(new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>');
    });
    return s;
  }
  document.querySelectorAll('.search').forEach(function(wrap){
    var box = wrap.querySelector('.js-search'), list = wrap.querySelector('.results'), hits = [], sel = -1;
    function draw(){
      var q = box.value.trim();
      hits = search(q); sel = hits.length ? 0 : -1;
      if(!q){ list.hidden = true; return; }
      list.innerHTML = hits.length ? hits.map(function(e, i){
        return '<a href="' + e.u + '"' + (i === sel ? ' class="sel"' : '') + '><b>' + esc(e.h) + '</b>'
          + (e.h !== e.p ? ' <span class="pg">' + esc(e.p) + '</span>' : '') + '<small>' + snippet(e, q) + '</small></a>';
      }).join('') : '<div class="none">Nothing found for “' + esc(q) + '”.</div>';
      list.hidden = false;
    }
    function move(d){
      var a = list.querySelectorAll('a'); if(!a.length) return;
      if(sel > -1) a[sel].classList.remove('sel');
      sel = (sel + d + a.length) % a.length; a[sel].classList.add('sel'); a[sel].scrollIntoView({block: 'nearest'});
    }
    box.addEventListener('input', draw);
    box.addEventListener('focus', function(){ if(box.value.trim()) draw(); });
    box.addEventListener('keydown', function(e){
      if(e.key === 'ArrowDown'){ e.preventDefault(); move(1); }
      else if(e.key === 'ArrowUp'){ e.preventDefault(); move(-1); }
      else if(e.key === 'Enter' && sel > -1){ e.preventDefault(); window.location = hits[sel].u; }
      else if(e.key === 'Escape'){ list.hidden = true; box.blur(); }
    });
    document.addEventListener('click', function(e){ if(!wrap.contains(e.target)) list.hidden = true; });
  });
  document.addEventListener('keydown', function(e){
    if(e.key !== '/' || /input|textarea/i.test(document.activeElement.tagName)) return;
    var box = Array.prototype.filter.call(document.querySelectorAll('.js-search'), function(b){ return b.offsetParent; })[0];
    if(box){ e.preventDefault(); box.focus(); }
  });
})();
