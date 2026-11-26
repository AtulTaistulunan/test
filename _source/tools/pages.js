(function(){
  var N=__N__,cur=0,body=document.body,$=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return (r||document).querySelectorAll(s)};
  var tg=$('#toggleAll'),score=$('#score'),sel=$('#sel'),picked=0,right=0;
  function setAll(on){body.classList.toggle('show-all',on);tg.checked=on;try{localStorage.setItem('showAll',on?'1':'0')}catch(e){}}
  try{if(localStorage.getItem('showAll')==='1')setAll(true)}catch(e){}
  tg.addEventListener('change',function(){setAll(tg.checked)});
  function upd(){score.textContent='已作答 '+picked+' / 200'+(picked?'，答對 '+right:'')}
  function pane(pg,name){$$('.pt',pg).forEach(function(b){b.classList.toggle('on',b.dataset.pane===name)});$$('.pane',pg).forEach(function(p){p.classList.toggle('on',p.dataset.pane===name)})}
  function showQ(pg,i){var qs=$$('.q',pg);if(!qs.length)return;i=Math.max(0,Math.min(qs.length-1,i));pg.dataset.qi=i;
    qs.forEach(function(q,k){q.classList.toggle('cur',k===i)});$$('.qc',pg).forEach(function(c,k){c.classList.toggle('cur',k===i)});
    $('.qp',pg).disabled=i===0;$('.qx',pg).disabled=i===qs.length-1;$('.qstage',pg).scrollTop=0}
  function show(i){i=Math.max(0,Math.min(N,i));cur=i;$$('.page').forEach(function(p){p.hidden=p.id!=='page-'+i});sel.value=i;
    $('#prev').disabled=i===0;$('#next').disabled=i===N;var pg=$('#page-'+i);if(i&&pg.dataset.qi===undefined)showQ(pg,0)}
  function go(i){i=Math.max(0,Math.min(N,i));if(location.hash!=='#page-'+i)location.hash='page-'+i;else show(i)}
  function route(){var m=/^#page-(\d+)$/.exec(location.hash);show(m?+m[1]:0)}
  window.addEventListener('hashchange',route);route();
  $('#prev').onclick=function(){go(cur-1)};$('#next').onclick=function(){go(cur+1)};sel.onchange=function(){go(+sel.value)};
  function setShow(q,on){q.classList.toggle('show',on);var b=$('.rv',q);b.textContent=on?'收起答案':'看答案';b.setAttribute('aria-expanded',on)}
  document.addEventListener('click',function(e){
    var t=e.target,pg=t.closest('.page'),x;
    if(x=t.closest('.pt')){pane(pg,x.dataset.pane);return}
    if(x=t.closest('.qc')){showQ(pg,+x.dataset.i);return}
    if(t.closest('.qp')){showQ(pg,+pg.dataset.qi-1);return}
    if(t.closest('.qx')){showQ(pg,+pg.dataset.qi+1);return}
    if(x=t.closest('.opt')){var q=x.closest('.q');
      if(!q.dataset.done){q.dataset.done='1';x.classList.add('picked');picked++;var ok=x.classList.contains('correct');if(ok)right++;upd();
        $$('.qc',pg)[+pg.dataset.qi].classList.add(ok?'ok':'ng')}
      setShow(q,true);return}
    if(x=t.closest('.rv')){var q2=x.closest('.q');setShow(q2,!q2.classList.contains('show'));return}
    if(x=t.closest('.cover')){x.classList.toggle('open')}
  });
  document.addEventListener('keydown',function(e){if(e.target.tagName==='SELECT'||!cur)return;var pg=$('#page-'+cur),qz=$('.pane[data-pane="quiz"].on',pg);if(!qz)return;
    if(e.key==='ArrowRight')showQ(pg,+pg.dataset.qi+1);if(e.key==='ArrowLeft')showQ(pg,+pg.dataset.qi-1)});
  $('#reset').onclick=function(){picked=0;right=0;upd();setAll(false);
    $$('.q').forEach(function(q){delete q.dataset.done;setShow(q,false)});
    $$('.picked').forEach(function(o){o.classList.remove('picked')});$$('.qc').forEach(function(c){c.classList.remove('ok','ng')});
    $$('.cover.open').forEach(function(c){c.classList.remove('open')})};
})();
