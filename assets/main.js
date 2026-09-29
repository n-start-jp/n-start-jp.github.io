(function(){
  var b=document.querySelector('.menu-btn');if(!b)return;
  function set(o){document.body.classList.toggle('nav-open',o);b.setAttribute('aria-expanded',o?'true':'false');b.setAttribute('aria-label',o?'メニューを閉じる':'メニューを開く');}
  b.addEventListener('click',function(){set(!document.body.classList.contains('nav-open'));});
  document.querySelectorAll('#gnav a').forEach(function(a){a.addEventListener('click',function(){set(false);});});
  document.addEventListener('keydown',function(e){if(e.key==='Escape')set(false);});
})();
