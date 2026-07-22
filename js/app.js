// js/app.js
// Lógica principal do checklist. Depende de js/lang.js já carregado antes.
// Suporta categorias simples (ex: Conquistas) e categorias com subcategorias
// (ex: Armas -> Punhais, Katanas...; Feitiços -> Feitiçarias, Encantamentos).

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
const EXPANDED_KEY = 'er-checklist-expanded';

let LANG_DATA = null;
let checked = {};
let custom = {};
let expanded = {};
let activeCat = null;
let activeSubcat = null;

const PIECE_SLOTS = [
  { id: 'helm', pt: 'Elmo', en: 'Helm' },
  { id: 'chest', pt: 'Peitoral', en: 'Chest Armor' },
  { id: 'gauntlets', pt: 'Braçadeiras', en: 'Gauntlets' },
  { id: 'legs', pt: 'Grevas', en: 'Leg Armor' },
];

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

// Retorna a lista de "folhas" de uma categoria: se ela tem subcategorias,
// uma folha por subcategoria; senão, a própria categoria é a única folha.
function leavesOf(cat) {
  if (cat.subcategories && cat.subcategories.length) {
    return cat.subcategories.map(sub => ({ leafKey: cat.id + '::' + sub.id, leaf: sub }));
  }
  return [{ leafKey: cat.id, leaf: cat }];
}

function allItemsForLeaf(leafKey, leaf, catId) {
  let built;
  if (catId === 'armor') {
    built = [];
    (leaf.items || []).forEach((setObj, i) => {
      PIECE_SLOTS.forEach(slot => {
        const pieceName = (slot.id === 'helm' && setObj.helm) ? setObj.helm
          : (slot.id === 'chest' && setObj.chest) ? setObj.chest
          : null;
        built.push({
          id: leafKey + '-' + i + '-' + slot.id,
          setIndex: i,
          setName: setObj.name,
          slot: slot.id,
          pieceName,
          custom: false,
          img: null,
        });
      });
    });
  } else {
    built = (leaf.items || []).map((name, i) => ({
      id: leafKey + '-' + i,
      name,
      custom: false,
      img: (catId === 'trophies' && TROPHY_IMAGE_FILES[i])
        ? 'img/trophies/' + TROPHY_IMAGE_FILES[i]
        : null,
    }));
  }
  const extra = (custom[leafKey] || []).map(it => ({
    id: it.id, name: it.name, custom: true, img: null,
  }));
  return built.concat(extra);
}

function totalCounts() {
  let total = 0, done = 0;
  LANG_DATA.categories.forEach(cat => {
    leavesOf(cat).forEach(({ leafKey, leaf }) => {
      allItemsForLeaf(leafKey, leaf, cat.id).forEach(it => {
        total++;
        if (checked[it.id]) done++;
      });
    });
  });
  return { total, done };
}

function renderNav() {
  const nav = document.getElementById('nav');
  nav.innerHTML = '';
  LANG_DATA.categories.forEach(cat => {
    let total = 0, done = 0;
    leavesOf(cat).forEach(({ leafKey, leaf }) => {
      allItemsForLeaf(leafKey, leaf, cat.id).forEach(it => {
        total++;
        if (checked[it.id]) done++;
      });
    });
    const btn = document.createElement('button');
    btn.className = cat.id === activeCat ? 'active' : '';
    btn.innerHTML = escapeHtml(cat.name) + ' <span class="count">' + done + '/' + total + '</span>';
    btn.onclick = () => { activeCat = cat.id; activeSubcat = null; render(); };
    nav.appendChild(btn);
  });
}

function renderSubNav(cat) {
  const subnav = document.getElementById('subnav');
  if (!cat.subcategories || !cat.subcategories.length) {
    subnav.innerHTML = '';
    subnav.style.display = 'none';
    return;
  }
  subnav.style.display = 'flex';
  if (!activeSubcat || !cat.subcategories.some(s => s.id === activeSubcat)) {
    activeSubcat = cat.subcategories[0].id;
  }
  subnav.innerHTML = '';
  cat.subcategories.forEach(sub => {
    const leafKey = cat.id + '::' + sub.id;
    const items = allItemsForLeaf(leafKey, sub, cat.id);
    const done = items.filter(it => checked[it.id]).length;
    const btn = document.createElement('button');
    btn.className = sub.id === activeSubcat ? 'active' : '';
    btn.innerHTML = escapeHtml(sub.name) + ' <span class="count">' + done + '/' + items.length + '</span>';
    btn.onclick = () => { activeSubcat = sub.id; renderSubNav(cat); renderContent(); renderRing(); };
    subnav.appendChild(btn);
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

function getActiveLeaf() {
  const cat = LANG_DATA.categories.find(c => c.id === activeCat);
  if (cat.subcategories && cat.subcategories.length) {
    let sub = cat.subcategories.find(s => s.id === activeSubcat);
    if (!sub) { sub = cat.subcategories[0]; activeSubcat = sub.id; }
    return { cat, leaf: sub, leafKey: cat.id + '::' + sub.id, leafDesc: sub.desc || cat.desc, leafName: sub.name };
  }
  return { cat, leaf: cat, leafKey: cat.id, leafDesc: cat.desc, leafName: cat.name };
}

function renderContent() {
  const ui = LANG_DATA.ui;
  const { cat, leaf, leafKey, leafDesc } = getActiveLeaf();
  const items = allItemsForLeaf(leafKey, leaf, cat.id);
  const done = items.filter(it => checked[it.id]).length;
  const content = document.getElementById('content');
  const isTable = cat.id === 'trophies';
  const isArmor = cat.id === 'armor';
  const langCode = (LangModule.getCurrentCode() || 'pt-BR').startsWith('pt') ? 'pt' : 'en';

  let listHtml;

  if (items.length === 0) {
    listHtml = '<p class="empty-note">' + escapeHtml(ui.emptyNote || 'Em construção — em breve.') + '</p>';
  } else if (isArmor) {
    const setsRaw = leaf.items || [];
    const rows = setsRaw.map((setObj, i) => {
      const expKey = leafKey + '-' + i;
      const isOpen = !!expanded[expKey];
      let setDone = 0;
      const pieceRows = PIECE_SLOTS.map(slot => {
        const pieceId = leafKey + '-' + i + '-' + slot.id;
        const isChecked = !!checked[pieceId];
        if (isChecked) setDone++;
        const pieceName = (slot.id === 'helm' && setObj.helm) ? setObj.helm
          : (slot.id === 'chest' && setObj.chest) ? setObj.chest
          : null;
        const slotLabel = slot[langCode];
        return '<div class="apiece ' + (isChecked ? 'checked' : '') + '" data-id="' + pieceId + '">'
          + '<div class="seal small"></div>'
          + '<div class="apiece-text">'
            + '<span class="apiece-slot">' + escapeHtml(slotLabel) + '</span>'
            + (pieceName
                ? '<span class="apiece-name">' + escapeHtml(pieceName) + '</span>'
                : '<span class="apiece-name pending">' + escapeHtml(langCode === 'pt' ? 'nome exato pendente' : 'exact name pending') + '</span>')
          + '</div>'
        + '</div>';
      }).join('');
      return '<div class="aset ' + (isOpen ? 'open' : '') + '">'
        + '<div class="aset-header" data-exp="' + expKey + '">'
          + '<span class="aset-chevron">▸</span>'
          + '<span class="aset-name">' + escapeHtml(setObj.name) + '</span>'
          + '<span class="aset-count">' + setDone + '/4</span>'
        + '</div>'
        + '<div class="aset-body">' + pieceRows + '</div>'
      + '</div>';
    }).join('');
    const customExtra = (custom[leafKey] || []);
    const customHtml = customExtra.length ? '<div class="grid">' + customExtra.map(it => {
      const isChecked = !!checked[it.id];
      return '<div class="item ' + (isChecked ? 'checked' : '') + '" data-id="' + it.id + '">'
        + '<div class="seal"></div>'
        + '<div class="item-text"><span class="name">' + escapeHtml(it.name) + '</span></div>'
        + '<button class="rm-btn" data-remove="' + it.id + '" title="' + escapeHtml(ui.removeTitle) + '">✕</button>'
        + '</div>';
    }).join('') + '</div>' : '';
    listHtml = '<div class="aset-list">' + rows + '</div>' + customHtml;
  } else if (isTable) {
    const rows = items.map(it => {
      const isChecked = !!checked[it.id];
      const parts = it.name.split(' — ');
      const title = parts[0];
      const desc = parts.slice(1).join(' — ');
      return '<div class="trow ' + (isChecked ? 'checked' : '') + '" data-id="' + it.id + '">'
        + '<div class="trow-check"><div class="seal small"></div></div>'
        + '<div class="trow-icon">' + (it.img ? '<img src="' + it.img + '" alt="" />' : '<div class="seal"></div>') + '</div>'
        + '<div class="trow-text">'
          + '<span class="trow-title">' + escapeHtml(title) + '</span>'
          + (desc ? '<span class="trow-desc">' + escapeHtml(desc) + '</span>' : '')
        + '</div>'
        + (it.custom ? '<button class="rm-btn" data-remove="' + it.id + '" title="' + escapeHtml(ui.removeTitle) + '">✕</button>' : '')
        + '</div>';
    }).join('');
    listHtml = '<div class="trophy-table">' + rows + '</div>';
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
    '<div class="section-head"><h2>' + escapeHtml(cat.subcategories ? cat.name + ' — ' + getActiveLeaf().leafName : cat.name) + '</h2><span class="stat">' + done + ' / ' + items.length + ' ' + escapeHtml(ui.completedLabel) + '</span></div>'
    + '<p class="section-desc">' + escapeHtml(leafDesc || '') + '</p>'
    + listHtml
    + '<div class="add-row"><input type="text" id="addInput" placeholder="' + escapeHtml(ui.addPlaceholder) + '"/><button id="addBtn">' + escapeHtml(ui.addBtn) + '</button></div>';

  content.querySelectorAll('.item, .trow, .apiece').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target.closest('.rm-btn')) return;
      toggleItem(el.getAttribute('data-id'));
    });
  });
  content.querySelectorAll('.aset-header').forEach(el => {
    el.addEventListener('click', () => {
      const key = el.getAttribute('data-exp');
      expanded[key] = !expanded[key];
      renderContent();
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
  const { leafKey } = getActiveLeaf();
  const id = 'custom-' + leafKey + '-' + Date.now();
  if (!custom[leafKey]) custom[leafKey] = [];
  custom[leafKey].push({ id, name: val });
  input.value = '';
  render();
  saveCustom();
}

function removeCustomItem(id) {
  const { leafKey } = getActiveLeaf();
  custom[leafKey] = (custom[leafKey] || []).filter(it => it.id !== id);
  delete checked[id];
  render();
  saveCustom();
  saveChecked();
}

function renderStaticText() {
  const ui = LANG_DATA.ui;
  document.getElementById('heroTitle').textContent = 'Elden Ring';
  document.getElementById('footerQuote').textContent = ui.footerQuote;
  document.getElementById('resetBtn').textContent = ui.resetBtn;
}

function render() {
  renderStaticText();
  renderNav();
  const cat = LANG_DATA.categories.find(c => c.id === activeCat);
  renderSubNav(cat);
  renderContent();
  renderRing();
}

async function initApp(langData) {
  LANG_DATA = langData;
  if (!activeCat || !LANG_DATA.categories.some(c => c.id === activeCat)) {
    activeCat = LANG_DATA.categories[0].id;
    activeSubcat = null;
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
