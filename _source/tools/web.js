(function(){
  var body=document.body,tg=document.getElementById('toggleAll'),score=document.getElementById('score');
  var picked=0,right=0;
  function setAll(on){body.classList.toggle('show-all',on);tg.checked=on;try{localStorage.setItem('showAll',on?'1':'0')}catch(e){}}
  try{if(localStorage.getItem('showAll')==='1')setAll(true)}catch(e){}
  tg.addEventListener('change',function(){setAll(tg.checked)});
  function upd(){score.textContent='已作答 '+picked+' / 200'+(picked?'，答對 '+right+' 題':'')}
  function setShow(q,on){q.classList.toggle('show',on);var b=q.querySelector('.rv');b.textContent=on?'收起答案':'看答案';b.setAttribute('aria-expanded',on)}
  document.addEventListener('click',function(e){
    var o=e.target.closest('.opt');
    if(o){var q=o.closest('.q');
      if(!q.dataset.done){q.dataset.done='1';o.classList.add('picked');picked++;if(o.classList.contains('correct'))right++;upd()}
      setShow(q,true);return}
    var r=e.target.closest('.rv');
    if(r){var q2=r.closest('.q');setShow(q2,!q2.classList.contains('show'));return}
    var c=e.target.closest('.cover');
    if(c){c.classList.toggle('open');return}
  });
  document.getElementById('reset').addEventListener('click',function(){
    picked=0;right=0;upd();setAll(false);
    document.querySelectorAll('.q').forEach(function(q){delete q.dataset.done;setShow(q,false)});
    document.querySelectorAll('.picked').forEach(function(o){o.classList.remove('picked')});
    document.querySelectorAll('.cover.open').forEach(function(c){c.classList.remove('open')});
  });
})();
