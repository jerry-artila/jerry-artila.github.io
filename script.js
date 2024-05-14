window.onload = function(){
  let el, fontSize;
  [el, fontSize] = currentFontSize('#content');
  const span =  document.querySelector('#displayFontSize');  
  span.textContent = fontSize + 'px'; 
}

function changeFontSize(enlarge, step = 3){
    const span =  document.querySelector('#displayFontSize'); 
    let el, fontSize;
    [el, fontSize] = currentFontSize('#content');
    const newSize = enlarge ? fontSize + step : fontSize - step;
    el.style.fontSize = newSize + 'px';
    span.textContent = el.style.fontSize; 
}

function currentFontSize(query) {
  const el = document.querySelector(query);
  const fontSize = parseFloat(window.getComputedStyle(el, null).getPropertyValue('font-size'));
  return [el, fontSize];
}
