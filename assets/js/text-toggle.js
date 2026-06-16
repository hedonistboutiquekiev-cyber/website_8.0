/**
 * text-toggle.js
 * А  втоматически добавляет функцию раскрытия/скрытия текста
 * на все страницы с <model-viewer>.
 */
 
(function () {
  'use strict';
 
  function initTextToggle() {
    if (!document.querySelector('model-viewer')) {
      return;
    }
 
    const mainP = document.querySelector('main p, .container p, p');
    if (!mainP) {
      return;
    }
 
    if (mainP.id === 'textContent') {
      return;
    }
 
    const wrapper = document.createElement('div');
    wrapper.id = 'textContent';
    mainP.parentNode.insertBefore(wrapper, mainP);
    wrapper.appendChild(mainP);
 
    if (!document.getElementById('text-toggle-css')) {
      const style = document.createElement('style');
      style.id = 'text-toggle-css';
      style.textContent = `
        #textContent {
          display: -webkit-box;
          -webkit-line-clamp: 6;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        #textContent.expanded {
          display: block;
        }
        .toggle-btn {
          display: block;
          margin: 10px auto 30px auto;
          padding: 12px 24px;
          background-color: rgb(29, 73, 105);
          color: #fff;
          border: 1px solid #4192cc;
          border-radius: 8px;
          font-size: 16px;
          cursor: pointer;
          transition: all 0.3s ease;
          backdrop-filter: blur(4px);
        }
        .toggle-btn:hover {
          background-color: #0096ff;
          box-shadow: 0 0 15px rgba(0, 150, 255, 0.6);
        }
        @media (max-width: 480px) {
          .toggle-btn {
            padding: 10px 16px;
            font-size: 14px;
          }
        }
      `;
      document.head.appendChild(style);
    }
 
    const button = document.createElement('button');
    button.id = 'toggleBtn';
    button.className = 'toggle-btn';
    button.textContent = 'Show text';
    button.setAttribute('aria-expanded', 'false');
    button.setAttribute('aria-controls', 'textContent');
 
    wrapper.parentNode.insertBefore(button, wrapper.nextSibling);
 
    button.addEventListener('click', function () {
      const isExpanded = wrapper.classList.contains('expanded');
      wrapper.classList.toggle('expanded');
      button.setAttribute('aria-expanded', (!isExpanded).toString());
      button.textContent = isExpanded ? 'Show text' : 'Show less';
    });
  }
 
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTextToggle);
  } else {
    initTextToggle();
  }
})();


