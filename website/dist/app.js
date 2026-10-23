'use strict';
const toggle=document.getElementById('language');
let language='zh';
toggle.addEventListener('click',()=>{
  language=language==='zh'?'en':'zh';
  document.documentElement.lang=language==='zh'?'zh-CN':'en';
  document.querySelectorAll('[data-zh][data-en]').forEach(element=>{element.innerHTML=element.dataset[language]});
  document.querySelectorAll('[data-href-zh][data-href-en]').forEach(element=>{element.href=element.getAttribute('data-href-'+language)});
  toggle.textContent=language==='zh'?'EN ↗':'中文 ↗';
  toggle.setAttribute('aria-label',language==='zh'?'Switch to English':'切换为中文');
});
