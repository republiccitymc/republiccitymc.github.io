// Loads a tab from the public 'RCMC Wiki Data (public)' Google Sheet.

(function(){
  var SHEET_ID='1lrAKLlqSMb53BA7Nqu6ZWAsHj6sjnox-Gj0bOECKFHA';
  window.rcEsc=function(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});};
  window.rcLoadSheet=function(tab){
    var url='https://docs.google.com/spreadsheets/d/'+SHEET_ID+'/gviz/tq?tqx=out:json&headers=1&sheet='+encodeURIComponent(tab)+'&t='+Date.now();
    return fetch(url).then(function(r){return r.text();}).then(function(t){
      var j=JSON.parse(t.substring(t.indexOf('{'),t.lastIndexOf('}')+1));
      if(j.status==='error') throw new Error('sheet error');
      var cols=j.table.cols.map(function(c){return (c.label||'').trim();});
      return j.table.rows.map(function(r){
        var o={};
        cols.forEach(function(name,i){var c=r.c[i];o[name]=c?(c.f!=null?c.f:(c.v!=null?c.v:'')):'';});
        return o;
      });
    });
  };
  window.rcFail=function(el){
    el.innerHTML='<p class="loading">Couldn\'t load the live table right now. Try refreshing the page.</p>';
  };
})();
