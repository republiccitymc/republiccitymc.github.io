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
