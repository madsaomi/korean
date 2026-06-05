(function() {
  'use strict';

  const csrf = document.querySelector('[name=csrfmiddlewaretoken]');
  const csrfToken = csrf ? csrf.value : '';
  const slug = typeof LIBRARY_SLUG !== 'undefined' ? LIBRARY_SLUG : '';
  const lang = typeof LIBRARY_LANG !== 'undefined' ? LIBRARY_LANG : 'korean';
  const apiBase = `/library/${lang}/api`;

  function getCSRF() {
    const c = document.querySelector('[name=csrfmiddlewaretoken]');
    return c ? c.value : csrfToken;
  }

  const HIGHLIGHT_COLORS = {
    yellow: { bg: '#fef08a', text: '#92400e' },
    green: { bg: '#bbf7d0', text: '#166534' },
    blue: { bg: '#bfdbfe', text: '#1e40af' },
    pink: { bg: '#fbcfe8', text: '#9d174d' },
    orange: { bg: '#fed7aa', text: '#9a3412' },
    purple: { bg: '#e9d5ff', text: '#6b21a8' },
  };

  // ─── HIGHLIGHT RENDERING ──────────────────────────────────────────────
  const contentEl = document.getElementById('md-content') || document.getElementById('reader-content');

  if (contentEl && slug) {
    fetchHighlights();
  }

  async function fetchHighlights() {
    try {
      const res = await fetch(`${apiBase}/highlights/?slug=${encodeURIComponent(slug)}`);
      const data = await res.json();
      if (data.highlights) {
        data.highlights.forEach(h => renderHighlight(h));
      }
    } catch (e) { console.error('fetch highlights error:', e); }
  }

  function renderHighlight(h) {
    const anchorEl = h.anchor ? document.getElementById(h.anchor) : contentEl;
    if (!anchorEl) return;
    const colors = HIGHLIGHT_COLORS[h.color] || HIGHLIGHT_COLORS.yellow;
    try {
      const result = applyOffsetHighlight(anchorEl, h.start_offset, h.end_offset, h.text, h.color, h.id);
      if (!result) fallbackTextHighlight(anchorEl, h);
    } catch (e) { fallbackTextHighlight(anchorEl, h); }
  }

  function applyOffsetHighlight(root, startOff, endOff, text, color, id) {
    const textNodes = [];
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    let node;
    while (node = walker.nextNode()) {
      if (node.parentElement && node.parentElement.closest('.korean-tts, mark, .highlight-toolbar, .note-chip, .toc-nav, .word-popup')) continue;
      textNodes.push(node);
    }
    let charCount = 0;
    let startNode = null, startNodeOff = 0, endNode = null, endNodeOff = 0;
    for (const n of textNodes) {
      const len = n.textContent.length;
      if (!startNode && charCount + len > startOff) {
        startNode = n;
        startNodeOff = startOff - charCount;
      }
      if (!endNode && charCount + len >= endOff) {
        endNode = n;
        endNodeOff = endOff - charCount;
        break;
      }
      charCount += len;
    }
    if (!startNode || !endNode) return false;
    const range = document.createRange();
    range.setStart(startNode, Math.max(0, startNodeOff));
    range.setEnd(endNode, Math.min(endNode.textContent.length, endNodeOff));
    try {
      const mark = document.createElement('mark');
      mark.style.cssText = `background:${HIGHLIGHT_COLORS[color].bg};color:${HIGHLIGHT_COLORS[color].text};border-radius:3px;padding:0 2px;cursor:pointer;transition:opacity .15s;`;
      mark.dataset.highlightId = id;
      mark.dataset.highlightColor = color;
      mark.dataset.highlightText = text;
      range.surroundContents(mark);
      return true;
    } catch (e) { return false; }
  }

  function fallbackTextHighlight(anchorEl, h) {
    const colors = HIGHLIGHT_COLORS[h.color] || HIGHLIGHT_COLORS.yellow;
    const walker = document.createTreeWalker(anchorEl, NodeFilter.SHOW_TEXT, null, false);
    let node;
    while (node = walker.nextNode()) {
      if (node.parentElement && node.parentElement.closest('.korean-tts, mark, .highlight-toolbar')) continue;
      const idx = node.textContent.indexOf(h.text);
      if (idx === -1) continue;
      const range = document.createRange();
      range.setStart(node, idx);
      range.setEnd(node, idx + h.text.length);
      const mark = document.createElement('mark');
      mark.style.cssText = `background:${colors.bg};color:${colors.text};border-radius:3px;padding:0 2px;cursor:pointer;transition:opacity .15s;`;
      mark.dataset.highlightId = h.id;
      mark.dataset.highlightColor = h.color;
      mark.dataset.highlightText = h.text;
      try { range.surroundContents(mark); } catch (e) {}
      break;
    }
  }

  // ─── HIGHLIGHT CLICK → DELETE ──────────────────────────────────────────
  document.addEventListener('click', async (e) => {
    const mark = e.target.closest('mark[data-highlight-id]');
    if (!mark) return;
    e.preventDefault();
    e.stopPropagation();
    if (!confirm('Удалить выделение?')) return;
    const id = mark.dataset.highlightId;
    try {
      const res = await fetch(`${apiBase}/highlight/toggle/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRF(), 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `slug=${encodeURIComponent(slug)}&text=${encodeURIComponent(mark.dataset.highlightText)}`,
      });
      const data = await res.json();
      if (data.highlighted === false) {
        const parent = mark.parentNode;
        const textNode = document.createTextNode(mark.textContent);
        parent.replaceChild(textNode, mark);
        parent.normalize();
      }
    } catch (e) { console.error(e); }
  });

  // ─── COLOR PICKER ON SELECTION ─────────────────────────────────────────
  let toolbar = null;

  function createToolbar() {
    const div = document.createElement('div');
    div.className = 'highlight-toolbar';
    div.style.cssText = 'position:fixed;z-index:9999;display:none;background:var(--glass-bg,#1e1e2e);backdrop-filter:blur(16px);border:1px solid var(--glass-border,rgba(255,255,255,0.1));border-radius:12px;padding:6px 10px;box-shadow:0 8px 32px rgba(0,0,0,0.4);gap:4px;align-items:center;';
    div.style.display = 'flex';
    Object.entries(HIGHLIGHT_COLORS).forEach(([name, c]) => {
      const btn = document.createElement('button');
      btn.style.cssText = `width:24px;height:24px;border-radius:50%;border:2px solid transparent;background:${c.bg};cursor:pointer;transition:transform .15s, border-color .15s;padding:0;`;
      btn.dataset.color = name;
      btn.addEventListener('mouseenter', () => { btn.style.transform = 'scale(1.2)'; btn.style.borderColor = c.text; });
      btn.addEventListener('mouseleave', () => { btn.style.transform = ''; btn.style.borderColor = 'transparent'; });
      btn.addEventListener('click', (e) => { e.stopPropagation(); handleColorPick(name); });
      div.appendChild(btn);
    });
    const sep = document.createElement('span');
    sep.textContent = '|';
    sep.style.cssText = 'color:var(--text-secondary,#888);margin:0 4px;font-size:12px;opacity:0.4;';
    div.appendChild(sep);
    const noteBtn = document.createElement('button');
    noteBtn.textContent = '📝';
    noteBtn.title = 'Заметка';
    noteBtn.style.cssText = 'background:none;border:none;cursor:pointer;font-size:16px;padding:2px;';
    noteBtn.addEventListener('click', (e) => { e.stopPropagation(); handleNoteFromSelection(); });
    div.appendChild(noteBtn);
    const bookmarkBtn = document.createElement('button');
    bookmarkBtn.textContent = '🔖';
    bookmarkBtn.title = 'Закладка';
    bookmarkBtn.style.cssText = 'background:none;border:none;cursor:pointer;font-size:16px;padding:2px;';
    bookmarkBtn.addEventListener('click', (e) => { e.stopPropagation(); handleBookmarkFromSelection(); });
    div.appendChild(bookmarkBtn);
    document.body.appendChild(div);
    return div;
  }

  let lastSelection = null;

  function getAnchorFromNode(node) {
    let el = node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement;
    while (el && el !== contentEl) {
      if (el.id && /^h\d+-/.test(el.id)) return el.id;
      el = el.parentElement;
    }
    return '';
  }

  function computeOffset(root, node, offset) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    let charCount = 0;
    let n;
    while (n = walker.nextNode()) {
      if (n.parentElement && n.parentElement.closest('.korean-tts, mark, .highlight-toolbar')) continue;
      if (n === node) return charCount + offset;
      charCount += n.textContent.length;
    }
    return charCount + offset;
  }

  function handleColorPick(color) {
    if (!lastSelection) return;
    const range = lastSelection.getRangeAt(0);
    const text = lastSelection.toString().trim();
    if (!text || text.length < 2) return;
    const anchor = getAnchorFromNode(range.startContainer);
    const startOff = computeOffset(contentEl, range.startContainer, range.startOffset);
    const endOff = computeOffset(contentEl, range.endContainer, range.endOffset);

    saveHighlight(text, color, anchor, startOff, endOff);
    hideToolbar();
    lastSelection = null;
  }

  function handleNoteFromSelection() {
    if (!lastSelection) return;
    const text = lastSelection.toString().trim();
    if (!text || text.length < 3) return;
    const modal = document.getElementById('noteModal');
    if (!modal) return;
    document.getElementById('note-highlighted-preview').textContent = `📝 "${text.substring(0, 100)}"`;
    document.getElementById('note-highlighted').value = text;
    const id = getAnchorFromNode(lastSelection.getRangeAt(0).startContainer);
    document.getElementById('note-anchor').value = id;
    new bootstrap.Modal(modal).show();
    hideToolbar();
    lastSelection = null;
  }

  function handleBookmarkFromSelection() {
    if (!lastSelection) return;
    const text = lastSelection.toString().trim();
    if (!text || text.length < 3) return;
    saveBookmark(text);
    hideToolbar();
    lastSelection = null;
  }

  function notify(msg) {
    let el = document.getElementById('hl-toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'hl-toast';
      el.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:99999;background:var(--glass-bg,#1e1e2e);backdrop-filter:blur(16px);border:1px solid var(--glass-border,rgba(255,255,255,0.1));border-radius:12px;padding:10px 18px;font-size:0.85rem;color:var(--text-primary,#fff);box-shadow:0 8px 32px rgba(0,0,0,0.4);opacity:0;transition:opacity .3s;';
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.style.opacity = '1';
    setTimeout(() => { el.style.opacity = '0'; }, 2000);
  }

  async function saveHighlight(text, color, anchor, startOff, endOff) {
    try {
      const res = await fetch(`${apiBase}/highlight/toggle/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRF(), 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `slug=${encodeURIComponent(slug)}&text=${encodeURIComponent(text)}&color=${encodeURIComponent(color)}&anchor=${encodeURIComponent(anchor)}&start_offset=${startOff}&end_offset=${endOff}`,
      });
      if (!res.ok) { notify('Ошибка: ' + res.status); return; }
      const data = await res.json();
      if (data.highlighted) { fetchHighlights(); notify('✅ Выделено'); }
      else { notify('🗑️ Выделение удалено'); }
    } catch (e) { notify('Ошибка сохранения'); console.error(e); }
  }

  async function saveBookmark(text) {
    try {
      const title = document.querySelector('h1')?.textContent?.trim() || slug;
      const res = await fetch(`${apiBase}/bookmark/update/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRF(), 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `slug=${encodeURIComponent(slug)}&title=${encodeURIComponent(title)}&note=${encodeURIComponent(text)}`,
      });
      if (!res.ok) { notify('Ошибка: ' + res.status); return; }
      const data = await res.json();
      if (data.bookmarked) {
        const btn = document.getElementById('btn-toggle-bookmark');
        if (btn) { btn.classList.add('active'); }
        notify('🔖 Закладка добавлена');
      }
    } catch (e) { notify('Ошибка сохранения'); console.error(e); }
  }

  function hideToolbar() {
    if (toolbar) toolbar.style.display = 'none';
  }

  function showToolbar(x, y) {
    if (!toolbar) toolbar = createToolbar();
    toolbar.style.left = Math.min(x, window.innerWidth - toolbar.offsetWidth - 10) + 'px';
    toolbar.style.top = (y - toolbar.offsetHeight - 8) + 'px';
    toolbar.style.display = 'flex';
  }

  document.addEventListener('mouseup', (e) => {
    if (!contentEl || !slug) return;
    const sel = window.getSelection();
    const text = sel.toString().trim();
    if (!text || text.length < 2) { hideToolbar(); return; }
    const range = sel.getRangeAt(0);
    if (!contentEl.contains(range.commonAncestorContainer)) { hideToolbar(); return; }
    lastSelection = sel;
    const rect = range.getBoundingClientRect();
    showToolbar(rect.left + rect.width / 2, rect.top);
  });

  document.addEventListener('mousedown', (e) => {
    if (toolbar && !toolbar.contains(e.target)) {
      hideToolbar();
    }
  });

  // ─── TTS for Korean spans ──────────────────────────────────────────────
  document.querySelectorAll('.korean-tts').forEach(el => {
    const text = el.dataset.tts;
    if (!text) return;
    const audio = new Audio();
    let loading = false;
    el.addEventListener('click', async (e) => {
      e.stopPropagation();
      if (loading) return;
      if (audio.src) {
        audio.currentTime = 0;
        audio.play().catch(() => {});
        return;
      }
      loading = true;
      el.style.opacity = '0.6';
      try {
        const res = await fetch(`/hangul/tts/?text=${encodeURIComponent(text)}`);
        const data = await res.json();
        if (data.url) { audio.src = data.url; audio.play().catch(() => {}); }
      } catch (err) { console.error('TTS error:', err); }
      loading = false;
      el.style.opacity = '1';
    });
  });

  // ─── Word lookup popup ─────────────────────────────────────────────────
  const popup = document.getElementById('word-popup');
  const popupContent = document.getElementById('word-popup-content');
  let popupTimeout = null;
  let currentWordId = null;

  function showPopup(word, x, y) {
    if (!popup) return;
    popupContent.innerHTML = '<div class="text-center py-2"><span class="tts-spinner"><span></span><span></span><span></span></span></div>';
    popup.style.left = Math.min(x, window.innerWidth - 320) + 'px';
    popup.style.top = Math.min(y, window.innerHeight - 200) + 'px';
    popup.classList.add('show');
  }

  function hidePopup() {
    if (popup) popup.classList.remove('show');
    popupTimeout = null;
  }

  async function lookupWord(wordText) {
    if (!wordText || wordText.length < 2) return;
    showPopup(wordText, 0, 0);
    try {
      const res = await fetch(`${apiBase}/word-lookup/?word=${encodeURIComponent(wordText)}`);
      const data = await res.json();
      if (data.found) {
        currentWordId = data.id;
        popupContent.innerHTML = `
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h6 class="mb-0 fw-bold" style="font-size:1.2rem;">${data.korean}</h6>
              <small style="color:var(--text-secondary);">${data.romanization || ''}</small>
            </div>
            <span class="badge" style="background:rgba(0,184,148,0.15);color:#00b894;">${data.in_vocab ? '✓ В словаре' : '✚'}</span>
          </div>
          <p class="mt-2 mb-1 fw-medium">${data.russian}</p>
          ${data.example ? `<div class="small" style="color:var(--text-secondary);"><em>${data.example}</em></div>` : ''}
          ${data.example_tr ? `<div class="small" style="color:var(--text-secondary);">${data.example_tr}</div>` : ''}
          ${!data.in_vocab ? `<button class="btn-glass btn-sm mt-2 px-3 add-to-vocab-btn" data-word-id="${data.id}">➕ В словарь</button>` : ''}
        `;
        const btn = popupContent.querySelector('.add-to-vocab-btn');
        if (btn) {
          btn.addEventListener('click', async () => {
            try {
              const r = await fetch(`${apiBase}/add-to-vocab/`, {
                method: 'POST',
                headers: {'X-CSRFToken': getCSRF(), 'Content-Type': 'application/x-www-form-urlencoded'},
                body: `word_id=${data.id}`,
              });
              const j = await r.json();
              if (j.success) { btn.textContent = '✅ Добавлено'; btn.disabled = true; btn.style.opacity = '0.6'; }
            } catch (e) { console.error(e); }
          });
        }
      } else {
        popupContent.innerHTML = `<div class="text-center py-2" style="color:var(--text-secondary);">Слово не найдено в словаре</div>`;
        popupTimeout = setTimeout(hidePopup, 2000);
      }
    } catch (err) {
      popupContent.innerHTML = `<div class="text-center py-2" style="color:var(--text-secondary);">Ошибка</div>`;
      console.error('Lookup error:', err);
    }
  }

  document.addEventListener('dblclick', (e) => {
    const sel = window.getSelection();
    const text = sel.toString().trim();
    // Korean or Japanese characters trigger word lookup
    if (text && /[\uac00-\ud7af\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]/.test(text)) {
      const word = text.split(/\s+/)[0];
      lookupWord(word);
      const range = sel.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      showPopup(word, rect.right + 10, rect.top + window.scrollY);
    }
  });

  document.addEventListener('click', (e) => {
    if (popup && !popup.contains(e.target)) hidePopup();
  });

  // ─── Toggle read status ────────────────────────────────────────────────
  const readBtn = document.getElementById('btn-toggle-read');
  if (readBtn && slug) {
    readBtn.addEventListener('click', async () => {
      try {
        const res = await fetch(window.location.pathname, {
          method: 'POST',
          headers: {'X-CSRFToken': getCSRF(), 'Content-Type': 'application/x-www-form-urlencoded'},
          body: `action=toggle_read`,
        });
        const data = await res.json();
        if (data.read !== undefined) {
          readBtn.innerHTML = data.read ? '✅ Прочитано' : '📖 Не прочитано';
          readBtn.classList.toggle('active', data.read);
        }
      } catch (e) { console.error(e); }
    });
  }

  // ─── Toggle bookmark (simple) ─────────────────────────────────────────
  const bookmarkBtn = document.getElementById('btn-toggle-bookmark');
  if (bookmarkBtn && slug) {
    bookmarkBtn.addEventListener('click', async () => {
      try {
        const res = await fetch(window.location.pathname, {
          method: 'POST',
          headers: {'X-CSRFToken': getCSRF(), 'Content-Type': 'application/x-www-form-urlencoded'},
          body: `action=toggle_bookmark`,
        });
        const data = await res.json();
        bookmarkBtn.classList.toggle('active', data.bookmarked);
      } catch (e) { console.error(e); }
    });
  }

  // ─── Save note ─────────────────────────────────────────────────────────
  const noteModal = document.getElementById('noteModal');
  const saveNoteBtn = document.getElementById('btn-save-note');
  if (saveNoteBtn && slug) {
    saveNoteBtn.addEventListener('click', async () => {
      const content = document.getElementById('note-content').value.trim();
      const highlighted = document.getElementById('note-highlighted').value;
      const anchor = document.getElementById('note-anchor').value;
      if (!content) return;
      try {
        const res = await fetch(window.location.pathname, {
          method: 'POST',
          headers: {'X-CSRFToken': getCSRF(), 'Content-Type': 'application/x-www-form-urlencoded'},
          body: `action=save_note&content=${encodeURIComponent(content)}&highlighted=${encodeURIComponent(highlighted)}&anchor=${encodeURIComponent(anchor)}`,
        });
        const data = await res.json();
        if (data.id) {
          const notesList = document.getElementById('notes-list');
          const chip = document.createElement('div');
          chip.className = 'note-chip';
          chip.dataset.noteId = data.id;
          chip.innerHTML = `
            <div class="d-flex justify-content-between">
              <small style="color:var(--text-secondary);">${data.highlighted_text ? data.highlighted_text.substring(0, 60) : ''}</small>
              <button class="btn-delete-note action-btn" style="font-size:0.65rem;padding:0.1rem 0.4rem;" data-note-id="${data.id}">✕</button>
            </div>
            <p class="mb-0 mt-1">${data.content}</p>
          `;
          if (notesList) notesList.prepend(chip);
          document.getElementById('note-content').value = '';
          document.getElementById('note-highlighted').value = '';
          document.getElementById('note-anchor').value = '';
          const modal = bootstrap.Modal.getInstance(noteModal);
          if (modal) modal.hide();
        }
      } catch (e) { console.error(e); }
    });
  }

  // ─── Delete note ──────────────────────────────────────────────────────
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-delete-note');
    if (!btn || !slug) return;
    const noteId = btn.dataset.noteId;
    if (!noteId || !confirm('Удалить заметку?')) return;
    fetch(window.location.pathname, {
      method: 'POST',
      headers: {'X-CSRFToken': getCSRF(), 'Content-Type': 'application/x-www-form-urlencoded'},
      body: `action=delete_note&note_id=${noteId}`,
    }).then(r => r.json()).then(data => {
      if (data.deleted) {
        const chip = btn.closest('.note-chip');
        if (chip) chip.remove();
      }
    }).catch(e => console.error(e));
  });

  // ─── Tags ──────────────────────────────────────────────────────────────
  const tagForm = document.getElementById('tag-form');
  const tagInput = document.getElementById('tag-input');
  if (tagForm && slug) {
    tagForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const tag = tagInput.value.trim().toLowerCase();
      if (!tag) return;
      try {
        const res = await fetch(window.location.pathname, {
          method: 'POST',
          headers: {'X-CSRFToken': getCSRF(), 'Content-Type': 'application/x-www-form-urlencoded'},
          body: `action=add_tag&tag=${encodeURIComponent(tag)}`,
        });
        const data = await res.json();
        if (data.tags) { tagInput.value = ''; location.reload(); }
      } catch (e) { console.error(e); }
    });
  }

  // ─── Keyboard shortcuts ────────────────────────────────────────────────
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagNAME === 'TEXTAREA') return;
    if (e.key === 'b' || e.key === 'B') {
      const bm = document.getElementById('btn-toggle-bookmark');
      if (bm) bm.click();
    }
    if (e.key === 'r' || e.key === 'R') {
      const rd = document.getElementById('btn-toggle-read');
      if (rd) rd.click();
    }
    if (e.key === 'n' || e.key === 'N') {
      const modal = new bootstrap.Modal(document.getElementById('noteModal'));
      modal.show();
    }
  });
})();
