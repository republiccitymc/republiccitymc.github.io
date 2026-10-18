// Republic City MC — shared bits for every page.
// ► SERVER ADDRESS: set it here once (e.g. 'play.republiccitymc.net') and every page updates.
//   Leave it '' to show "Address coming soon".
var RC_SERVER = { address: '', version: '1.21.11' };

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

// Wiki sidebar search: typing filters the page links; Enter opens the first match.
(function(){
  var box = document.querySelector('.js-find');
  if(!box) return;
  var links = Array.prototype.slice.call(document.querySelectorAll('.side .grp a'));
  box.addEventListener('input', function(){
    var q = box.value.trim().toLowerCase();
    links.forEach(function(a){ a.classList.toggle('hidden', q && a.textContent.toLowerCase().indexOf(q) < 0); });
    document.querySelectorAll('.side .grp').forEach(function(g){
      g.classList.toggle('hidden', q && !g.querySelector('a:not(.hidden)'));
    });
  });
  box.addEventListener('keydown', function(e){
    if(e.key !== 'Enter') return;
    var first = links.filter(function(a){ return !a.classList.contains('hidden'); })[0];
    if(first) window.location = first.href;
  });
})();
