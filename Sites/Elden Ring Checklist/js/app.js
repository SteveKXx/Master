// js/app.js
// Lógica principal do checklist. Depende de js/lang.js já carregado antes.

// Nomes dos arquivos de imagem dos troféus, na MESMA ordem dos itens
// da categoria "trophies" em qualquer idioma (a ordem é idêntica nos JSONs).
const TROPHY_IMAGE_FILES = [
  'roundtable_hold.png','margit__the_fell_omen.png','shardbearer_godrick.png','great_rune.png',
  'red_wolf_of_radagon.png','rennala__queen_of_the_full_moon.png','leonine_misbegotten_trophy.png',
  'royal_knight_loretta.png','shardbearer_radahn.png','mimic_tear.png','godfrey_the_first_lord.png',
  'shardbearer_morgott.png','magma_wyrm_makar.png','god-slaying_armament.png','fire_giant_trophy.png',
  'erdtree_aflame.png','commander_niall.png','shardbearer_rykard.png','astel__naturalborn_of_the_void.png',
  'godskin_duo.png','godskin_noble.png','ancestor_spirit_trophy.png','maliketh_the_black_blade.png',
  'shardbearer_mohg.png','hoarah_loux_the_warrior.png','valiant_gargoyle.png',
  'loretta__knight_of_the_haligtree.png','elemer_of_the_briar.png',
  'dragonkin_soldier_of_nokstella_trophy.png','regal_ancestor_spirit.png','shardbearer_malenia.png',
  'mohg__the_omen.png','dragonlord_placidusax.png','lichdragon_fortissax.png','age_of_stars.png',
  'elden_lord.png','legendary_armaments.png','legendary_talismans.png','legendary_ashen_remains.png',
  'legendary_sorceries_and_incantations.png','lord_of_frenzied_flame.png','elden_ring.png',
];

const STATE_KEY = 'er-checklist-checked';
const CUSTOM_KEY = 'er-checklist-custom';

let LANG_DATA = null;
let checked = {};
let custom = {};
let activeCat = null;

function loadLocalState() {
  try {
    const s = localStorage.getItem(STATE_KEY);
    checked = s ? JSON.parse(s) : {};
  } catch (e) { checked = {}; }
  try {
    const c = localStorage.getItem(CUSTOM_KEY);
    custom = c ? JSON.parse(c) : {};
  } catch (e) { custom = {}; }
}

function saveChecked() {
  try { localStorage.setItem(STATE_KEY, JSON.stringify(checked)); }
  catch (e) { console.error('Erro ao salvar progresso', e); }
}

function saveCustom() {
  try { localStorage.setItem(CUSTOM_KEY, JSON.stringify(custom)); }
  catch (e) { console.error('Erro ao salvar itens personalizados', e); }
}

function allItemsFor(cat) {
  const built = cat.items.map((name, i) => ({
    id: cat.id + '-' + i,
    name,
    custom: false,
    img: (cat.id === 'trophies' && TROPHY_IMAGE_FILES[i])
      ? 'img/trophies/' + TROPHY_IMAGE_FILES[i]
      : null,
  }));
  const extra = (custom[cat.id] || []).map(it => ({
    id: it.id, name: it.name, custom: true, img: null,
  }));
  return built.concat(extra);
}

function totalCounts() {
  let total = 0, done = 0;
  LANG_DATA.categories.forEach(cat => {
    allItemsFor(cat).forEach(it => {
      total++;
      if (checked[it.id]) done++;
    });
  });
  return { total, done };
}

function renderNav() {
  const nav = document.getElementById('nav');
  nav.innerHTML = '';
  LANG_DATA.categories.forEach(cat => {
    const items = allItemsFor(cat);
    const done = items.filter(it => checked[it.id]).length;
    const btn = document.createElement('button');
    btn.className = cat.id === activeCat ? 'active' : '';
    btn.innerHTML = escapeHtml(cat.name) + ' <span class="count">' + done + '/' + items.length + '</span>';
    btn.onclick = () => { activeCat = cat.id; render(); };
    nav.appendChild(btn);
  });
}

function renderRing() {
  const { total, done } = totalCounts();
  const pct = total ? Math.round((done / total) * 100) : 0;
  const circumference = 314;
  const offset = circumference - (pct / 100) * circumference;
  document.getElementById('ringFg').style.strokeDashoffset = offset;
  document.getElementById('pctLabel').textContent = pct + '%';
  document.getElementById('countLabel').textContent = done + '/' + total;
}

function renderContent() {
  const ui = LANG_DATA.ui;
  const cat = LANG_DATA.categories.find(c => c.id === activeCat);
  const items = allItemsFor(cat);
  const done = items.filter(it => checked[it.id]).length;
  const content = document.getElementById('content');
  const isTable = cat.id === 'trophies';

  let listHtml;

  if (isTable) {
    const rows = items.map(it => {
      const isChecked = !!checked[it.id];
      // separa "Título — Descrição" em duas linhas, se houver " — "
      const parts = it.name.split(' — ');
      const title = parts[0];
      const desc = parts.slice(1).join(' — ');
      return '<div class="trow ' + (isChecked ? 'checked' : '') + '" data-id="' + it.id + '">'
        + '<div class="trow-icon">' + (it.img ? '<img src="' + it.img + '" alt="" />' : '<div class="seal"></div>') + '</div>'
        + '<div class="trow-text">'
          + '<span class="trow-title">' + escapeHtml(title) + '</span>'
          + (desc ? '<span class="trow-desc">' + escapeHtml(desc) + '</span>' : '')
        + '</div>'
        + '<div class="trow-check"><div class="seal small"></div></div>'
        + (it.custom ? '<button class="rm-btn" data-remove="' + it.id + '" title="' + escapeHtml(ui.removeTitle) + '">✕</button>' : '')
        + '</div>';
    }).join('');
    listHtml = '<div class="trophy-table">'
      + '<div class="trow trow-head"><div class="trow-icon">Ícone</div><div class="trow-text">Nome</div><div class="trow-check"></div></div>'
      + rows
      + '</div>';
  } else {
    listHtml = '<div class="grid">' + items.map(it => {
      const isChecked = !!checked[it.id];
      return '<div class="item ' + (isChecked ? 'checked' : '') + '" data-id="' + it.id + '">'
        + '<div class="seal"></div>'
        + (it.img ? '<img class="item-img" src="' + it.img + '" alt="" />' : '')
        + '<div class="item-text"><span class="name">' + escapeHtml(it.name) + '</span></div>'
        + (it.custom ? '<button class="rm-btn" data-remove="' + it.id + '" title="' + escapeHtml(ui.removeTitle) + '">✕</button>' : '')
        + '</div>';
    }).join('') + '</div>';
  }

  content.innerHTML =
    '<div class="section-head"><h2>' + escapeHtml(cat.name) + '</h2><span class="stat">' + done + ' / ' + items.length + ' ' + escapeHtml(ui.completedLabel) + '</span></div>'
    + '<p class="section-desc">' + escapeHtml(cat.desc) + '</p>'
    + listHtml
    + '<div class="add-row"><input type="text" id="addInput" placeholder="' + escapeHtml(ui.addPlaceholder) + '"/><button id="addBtn">' + escapeHtml(ui.addBtn) + '</button></div>';

  content.querySelectorAll('.item, .trow:not(.trow-head)').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target.closest('.rm-btn')) return;
      toggleItem(el.getAttribute('data-id'));
    });
  });
  content.querySelectorAll('[data-remove]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      removeCustomItem(el.getAttribute('data-remove'));
    });
  });
  document.getElementById('addBtn').addEventListener('click', addCustomItem);
  document.getElementById('addInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') addCustomItem();
  });
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function toggleItem(id) {
  checked[id] = !checked[id];
  render();
  saveChecked();
}

function addCustomItem() {
  const input = document.getElementById('addInput');
  const val = input.value.trim();
  if (!val) return;
  const id = 'custom-' + activeCat + '-' + Date.now();
  if (!custom[activeCat]) custom[activeCat] = [];
  custom[activeCat].push({ id, name: val });
  input.value = '';
  render();
  saveCustom();
}

function removeCustomItem(id) {
  custom[activeCat] = (custom[activeCat] || []).filter(it => it.id !== id);
  delete checked[id];
  render();
  saveCustom();
  saveChecked();
}

function renderStaticText() {
  const ui = LANG_DATA.ui;
  document.getElementById('heroTitle').textContent = ui.title;
  document.getElementById('heroSubtitle').textContent = ui.subtitle;
  document.getElementById('footerQuote').textContent = ui.footerQuote;
  document.getElementById('resetBtn').textContent = ui.resetBtn;
}

function render() {
  renderStaticText();
  renderNav();
  renderContent();
  renderRing();
}

async function initApp(langData) {
  LANG_DATA = langData;
  if (!activeCat || !LANG_DATA.categories.some(c => c.id === activeCat)) {
    activeCat = LANG_DATA.categories[0].id;
  }
  render();
}

document.getElementById('resetBtn').addEventListener('click', () => {
  const msg = LANG_DATA ? LANG_DATA.ui.resetConfirm : 'Reset progress?';
  if (!confirm(msg)) return;
  checked = {};
  render();
  saveChecked();
});

(async function start() {
  loadLocalState();
  LangModule.onChange((data) => { initApp(data); });
  const defaultLang = LangModule.detectDefaultLang();
  const data = await LangModule.loadLang(defaultLang);
  LangModule.renderSwitcher(document.getElementById('langSwitch'));
  await initApp(data);
})();
