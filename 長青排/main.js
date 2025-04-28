document.addEventListener('DOMContentLoaded', function() {
  const fontClasses = [
    'text-xl/6', 
    'text-2xl/7', 
    'text-3xl/9', 
    'text-4xl/10',
    'text-5xl/14'
  ];

  const el = document.querySelector('#main');
  const plusBtn = document.querySelectorAll('button')[0]; // A+ 按鈕
  const minusBtn = document.querySelectorAll('button')[1]; // A- 按鈕

  let currentIndex = fontClasses.indexOf('text-4xl/10'); // 你的起始是 text-4xl

  function updateFont() {
    // 移除舊的 font class
    fontClasses.forEach(cls => el.classList.remove(cls));
    // 加上新的 font class
    el.classList.add(fontClasses[currentIndex]);
  }

  plusBtn.addEventListener('click', function() {
    if (currentIndex < fontClasses.length - 1) {
      currentIndex++;
      updateFont();
    }
  });

  minusBtn.addEventListener('click', function() {
    if (currentIndex > 0) {
      currentIndex--;
      updateFont();
    }
  });
});