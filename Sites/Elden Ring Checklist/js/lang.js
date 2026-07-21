// js/lang.js
// Responsável por carregar os arquivos de idioma (lang/*.json) e
// notificar o app quando o idioma muda.

const AVAILABLE_LANGS = [
  { code: 'pt-BR', label: 'PT-BR' },
  { code: 'en-US', label: 'EN-US' },
];

const LangModule = (() => {
  const LANG_STORAGE_KEY = 'er-checklist-lang';
  let currentLangCode = null;
  let currentData = null;
  let onChangeCallback = null;

  function detectDefaultLang() {
    const saved = localStorage.getItem(LANG_STORAGE_KEY);
    if (saved && AVAILABLE_LANGS.some(l => l.code === saved)) return saved;
    const nav = (navigator.language || 'pt-BR').toLowerCase();
    if (nav.startsWith('pt')) return 'pt-BR';
    return 'en-US';
  }

  async function loadLang(code) {
    const res = await fetch(`lang/${code}.json`);
    if (!res.ok) throw new Error('Falha ao carregar idioma: ' + code);
    const data = await res.json();
    currentLangCode = code;
    currentData = data;
    localStorage.setItem(LANG_STORAGE_KEY, code);
    document.documentElement.setAttribute('lang', code);
    if (onChangeCallback) onChangeCallback(data, code);
    return data;
  }

  function renderSwitcher(containerEl) {
    containerEl.innerHTML = '';
    AVAILABLE_LANGS.forEach(l => {
      const btn = document.createElement('button');
      btn.textContent = l.label;
      btn.className = l.code === currentLangCode ? 'active' : '';
      btn.addEventListener('click', async () => {
        if (l.code === currentLangCode) return;
        await loadLang(l.code);
        renderSwitcher(containerEl);
      });
      containerEl.appendChild(btn);
    });
  }

  function onChange(cb) {
    onChangeCallback = cb;
  }

  function getCurrentCode() {
    return currentLangCode;
  }

  function getCurrentData() {
    return currentData;
  }

  return {
    detectDefaultLang,
    loadLang,
    renderSwitcher,
    onChange,
    getCurrentCode,
    getCurrentData,
  };
})();
