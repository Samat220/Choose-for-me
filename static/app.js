const PLATFORMS = { game: ["PC", "PlayStation", "Xbox", "Nintendo"], movie: ["Netflix", "Amazon", "Apple TV", "Crunchyroll", "Ororo.tv"] };
let currentTab = 'all';
let currentTags = [];
let lastItems = [];
let editingId = null;
let isSpinning = false;

/* ---------- Utilities ---------- */
function randomIn(min, max) { return Math.random() * (max - min) + min; }

// Always multiple turns + slight jitter so it doesn't stop exactly at center
function computeTargetAngle(index, total) {
  const step = 360 / total;
  // Calculate the middle of the winning segment
  const segmentMid = index * step + step / 2;

  // Base rotations for excitement (whole numbers to avoid accumulation errors)
  const baseTurns = Math.floor(randomIn(5, 8)); // 5-7 full rotations (whole numbers)
  const jitter = randomIn(-3, 3);              // Small jitter for realism

  // The correct final position (we know this works)
  const finalPosition = 360 - segmentMid;

  // Add full rotations: ensure we end up at exactly the right position
  return (baseTurns * 360) + finalPosition + jitter;
}

// Simple, reliable wheel animation with smooth deceleration
function animateWheelTo(angle, durationMs) {
  const wheel = document.getElementById('wheel');

  // Reset to 0 and then apply the full target rotation
  // This ensures accuracy regardless of previous spins
  wheel.style.transition = 'none';
  wheel.style.transform = 'rotate(0deg)';

  // Force a reflow to ensure the reset takes effect
  wheel.offsetHeight;

  // Now apply the complete rotation from 0 to the target
  wheel.style.transition = `transform ${durationMs}ms cubic-bezier(0.165, 0.84, 0.44, 1)`;
  wheel.style.transform = `rotate(${angle}deg)`;

  console.log('Animation applied:', { startAngle: 0, targetAngle: angle, durationMs });
}

function initials(name) {
  const parts = (name || '').split(' ').filter(Boolean).slice(0, 2);
  return parts.map(p => p[0].toUpperCase()).join('') || '?';
}
function colorFromString(s) {
  let h = 0; for (const ch of (s || '')) { h = ch.charCodeAt(0) + ((h << 5) - h); }
  const hue = Math.abs(h) % 360; return `hsl(${hue} 80% 45%)`;
}
function fallbackBlock(title, cls) {
  const col = colorFromString(title);
  return `<div class="${cls} grid place-content-center" style="background:${col}20;border:1px dashed ${col}66">
            <div class="text-2xl font-bold" style="color:${col}">${initials(title)}</div>
            <div class="text-[10px] text-slate-400">No Cover</div>
          </div>`;
}

/* ---------- Error Handling ---------- */
function showError(message) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'fixed top-4 right-4 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg z-50';
  errorDiv.textContent = message;
  document.body.appendChild(errorDiv);

  setTimeout(() => {
    errorDiv.remove();
  }, 5000);
}

function showSuccess(message) {
  const successDiv = document.createElement('div');
  successDiv.className = 'fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-50';
  successDiv.textContent = message;
  document.body.appendChild(successDiv);

  setTimeout(() => {
    successDiv.remove();
  }, 3000);
}

/* ---------- Theme ---------- */
function getTheme() { return localStorage.getItem('theme') || 'dark'; }
function setTheme(t) { localStorage.setItem('theme', t); applyTheme(); }
function toggleTheme() { setTheme(getTheme() === 'dark' ? 'light' : 'dark'); }
function applyTheme() {
  const body = document.getElementById('appBody');
  const btn = document.getElementById('themeBtn');
  const dark = ['bg-gradient-to-br', 'from-slate-900', 'via-slate-950', 'to-black', 'text-slate-100'];
  const light = ['bg-gradient-to-br', 'from-white', 'via-white', 'to-slate-100', 'text-slate-900'];

  body.classList.remove(...dark, ...light);
  if (getTheme() === 'dark') {
    body.classList.remove('light');
    body.classList.add(...dark);
    btn.textContent = '🌙';
  } else {
    body.classList.add('light');
    body.classList.add(...light);
    btn.textContent = '☀️';
  }
}

/* ---------- Filters / Tabs ---------- */
function setTab(tab) { currentTab = tab; document.querySelectorAll('[data-tab]')?.forEach(b => { b.classList.toggle('bg-slate-800/60', b.getAttribute('data-tab') === tab); }); loadItems(); }
function applyTags() { currentTags = (document.getElementById('tagsInput').value || '').split(',').map(s => s.trim()).filter(Boolean); loadItems(); }

function syncPlatformOptions() {
  const t = document.getElementById('typeInput').value;
  const select = document.getElementById('platformInput');
  select.innerHTML = `<option value="">—</option>` + PLATFORMS[t].map(p => `<option value="${p}">${p}</option>`).join('');
}

/* ---------- Data / Cards ---------- */
async function loadItems() {
  try {
    const params = new URLSearchParams();
    if (currentTab !== 'all') params.set('type', currentTab);
    if (currentTags.length) params.set('tags', currentTags.join(','));
    if (document.getElementById('showArchived')?.checked) params.set('includeArchived', 'true');

    const res = await fetch('/api/items?' + params.toString());
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    const data = await res.json();
    lastItems = data;

    const grid = document.getElementById('grid');
    document.getElementById('empty').classList.toggle('hidden', data.length !== 0);

    grid.innerHTML = data.map(it => {
      const tagsHtml = (it.tags && it.tags.length) ? ('<div class="mt-1 flex flex-wrap gap-1">' + it.tags.map(t => '<span class="text-[10px] chip rounded-full px-2 py-0.5">' + t + '</span>').join('') + '</div>') : '';
      const stateBadge = it.status === 'done' ? '<span class="text-[10px] chip rounded-full px-2 py-0.5">Done</span>' : (it.status === 'archived' ? '<span class="text-[10px] chip rounded-full px-2 py-0.5">Archived</span>' : '');
      const cardClass = `group rounded-2xl overflow-hidden border border-slate-800/60 bg-slate-900/40 hover:border-slate-700 transition card ${it.status === 'done' ? 'done' : ''} ${it.status === 'archived' ? 'archived' : ''}`;

      return (
        `<div class="${cardClass}">
          <div class="relative h-40 w-full overflow-hidden">
            ${it.coverUrl ? `<img src="${it.coverUrl}" class="absolute inset-0 h-full w-full object-cover" onerror="this.style.display='none'"/>` : fallbackBlock(it.title, 'absolute inset-0 rounded-none')}
            <div class="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent"></div>
            <div class="absolute left-3 bottom-3 right-3 flex items-end justify-between gap-3">
              <div class="min-w-0">
                <div class="truncate font-semibold text-base drop-shadow">${it.title}</div>
                ${it.platform ? `<div class="text-xs text-slate-300/90 drop-shadow">${it.platform}</div>` : ''}
                ${tagsHtml}
              </div>
              <div class="flex gap-1 items-center">
                <span class="text-[10px] rounded-full px-2 py-0.5 chip">${it.type === 'game' ? 'Game' : 'Movie/TV'}</span>
                ${stateBadge}
              </div>
            </div>
          </div>
          <div class="p-3 flex items-center gap-2">
            <button class="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs border border-slate-700/60 hover:bg-slate-800/60" onclick="openEditById('${it.id}')">Edit</button>
            ${it.status === 'done'
          ? `<button class="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs border border-indigo-900/50 text-indigo-300 hover:bg-indigo-900/20" onclick="setStatus('${it.id}','active')">Mark Active</button>`
          : `<button class="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs border border-emerald-900/50 text-emerald-300 hover:bg-emerald-900/20" onclick="setStatus('${it.id}','done')">Mark Done</button>`
        }
            ${it.status === 'archived'
          ? `<button class="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs border border-yellow-900/50 text-yellow-300 hover:bg-yellow-900/20" onclick="setStatus('${it.id}','active')">Restore</button>`
          : `<button class="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs border border-yellow-900/50 text-yellow-300 hover:bg-yellow-900/20" onclick="setStatus('${it.id}','archived')">Archive</button>`
        }
            <div class="ml-auto"></div>
            <button class="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs border border-rose-900/50 text-rose-300 hover:bg-rose-900/30" onclick="removeItem('${it.id}')">Delete</button>
          </div>
        </div>`
      );
    }).join('');
  } catch (error) {
    console.error('Failed to load items:', error);
    showError('Failed to load items. Please try again.');
  }
}

function openAdd() {
  editingId = null;
  document.getElementById('dialogTitle').textContent = 'Add Item';
  const typeInput = document.getElementById('typeInput');
  typeInput.value = (currentTab === 'movie' ? 'movie' : 'game');
  syncPlatformOptions();
  document.getElementById('titleInput').value = '';
  document.getElementById('platformInput').value = '';
  document.getElementById('coverInput').value = '';
  document.getElementById('tagsAddInput').value = '';
  document.getElementById('editStatusNote').classList.add('hidden');
  document.getElementById('addDialog').showModal();
  setTimeout(() => document.getElementById('titleInput').focus(), 50);
}

function openEditById(id) {
  const it = lastItems.find(x => x.id === id);
  if (!it) return;
  editingId = it.id;
  document.getElementById('dialogTitle').textContent = 'Edit Item';
  const typeInput = document.getElementById('typeInput');
  typeInput.value = it.type;
  syncPlatformOptions();
  document.getElementById('titleInput').value = it.title || '';
  document.getElementById('platformInput').value = it.platform || '';
  document.getElementById('coverInput').value = it.coverUrl || '';
  document.getElementById('tagsAddInput').value = (it.tags || []).join(', ');
  const note = document.getElementById('editStatusNote');
  note.textContent = `Current status: ${it.status || 'active'}`;
  note.classList.remove('hidden');
  document.getElementById('addDialog').showModal();
  setTimeout(() => document.getElementById('titleInput').focus(), 50);
}

async function submitAdd(e) {
  e.preventDefault();
  try {
    const type = document.getElementById('typeInput').value;
    const title = document.getElementById('titleInput').value.trim();
    const platform = document.getElementById('platformInput').value.trim();
    const coverUrl = document.getElementById('coverInput').value.trim();
    const tags = (document.getElementById('tagsAddInput').value || '').split(',').map(s => s.trim()).filter(Boolean);

    if (!title) {
      showError('Please enter a title.');
      return;
    }

    const requestData = { type, title, platform, coverUrl, tags };
    let response;

    if (editingId) {
      response = await fetch(`/api/items/${editingId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });
    } else {
      response = await fetch('/api/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });
    }

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const wasEditing = !!editingId;
    document.getElementById('addDialog').close();
    editingId = null;
    await loadItems();
    showSuccess(wasEditing ? 'Item updated successfully' : 'Item added successfully');
  } catch (error) {
    console.error('Failed to submit item:', error);
    showError(error.message || 'Failed to save item. Please try again.');
  }
}

async function setStatus(id, status) {
  try {
    const response = await fetch(`/api/items/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    await loadItems();
    showSuccess(`Item marked as ${status}`);
  } catch (error) {
    console.error('Failed to update status:', error);
    showError('Failed to update item status. Please try again.');
  }
}

async function removeItem(id) {
  if (!confirm('Are you sure you want to delete this item?')) {
    return;
  }

  try {
    const response = await fetch('/api/items?id=' + encodeURIComponent(id), { method: 'DELETE' });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    await loadItems();
    showSuccess('Item deleted successfully');
  } catch (error) {
    console.error('Failed to delete item:', error);
    showError('Failed to delete item. Please try again.');
  }
}

// TODO: cover fetcher: integrate a server-side proxy to TMDB/IGDB and store the resolved image URL.

/* ---------- Wheel rendering & spin ---------- */
function buildWheel(pool) {
  const wheel = document.getElementById('wheel');
  const legend = document.getElementById('wheelLegend');
  const wrap = document.getElementById('wheelWrap');

  if (!pool || pool.length === 0) {
    wrap.classList.add('hidden');
    wheel.style.background = '';
    wheel.style.transition = 'none';
    wheel.style.transform = 'rotate(0deg)';
    legend.textContent = '';
    return;
  }

  wrap.classList.remove('hidden');

  // Reset wheel position and transition
  wheel.style.transition = 'none';
  wheel.style.transform = 'rotate(0deg)';

  // Force a reflow to ensure reset takes effect
  wheel.offsetHeight;

  const n = pool.length;
  const step = 360 / n;
  let start = 0;
  const stops = [];
  const legendBits = [];
  for (let i = 0; i < n; i++) {
    const it = pool[i];
    // Check if this title appears multiple times in the pool
    const duplicateCount = pool.filter(item => item.title === it.title).length;
    const duplicateIndex = pool.slice(0, i).filter(item => item.title === it.title).length;

    let color;
    if (duplicateCount > 1) {
      // For duplicates, add a small hue shift to differentiate them
      const baseColor = colorFromString(it.title);
      const hueMatch = baseColor.match(/hsl\((\d+)/);
      const baseHue = hueMatch ? parseInt(hueMatch[1]) : 0;
      const shiftedHue = (baseHue + (duplicateIndex * 60)) % 360; // 60° shift per duplicate
      color = `hsl(${shiftedHue} 80% 45%)`;
    } else {
      // Single items use the original beautiful color
      color = colorFromString(it.title);
    }

    const end = start + step;
    stops.push(`${color} ${start}deg ${end}deg`);
    legendBits.push(`<span class="inline-flex items-center gap-1 mr-2 mb-1"><span class="inline-block w-2.5 h-2.5 rounded" style="background:${color}"></span>${it.title}</span>`);
    start = end;
  }
  wheel.style.background = `conic-gradient(${stops.join(',')})`;
  legend.innerHTML = legendBits.join('');
}

async function spinWheel(event) {
  // Prevent any default behavior that might cause page jumping
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  if (isSpinning) {
    console.log('Already spinning, ignoring...');
    return; // prevent double-trigger during animation
  }

  console.log('Starting spin...');

  // Funny messages to show while spinning
  const funnyMessages = [
    "Pondering...", "Cogitating...", "Mulling...", "Ruminating...", "Contemplating...",
    "Analyzing...", "Synthesizing...", "Bamboozling...", "Wrangling...", "Juggling...",
    "Fiddling...", "Conjuring...", "Whipping up magic...", "Assembling choices...",
    "Consulting the universe...", "Channeling randomness...", "Shuffling possibilities...",
    "Brewing decisions...", "Stirring the pot...", "Rolling the dice...",
    "Spinning destiny...", "Calculating chaos...", "Mixing mayhem...",
    "Summoning serendipity...", "Unleashing randomness...", "Tickling fate...",
    "Confusing algorithms...", "Puzzling over options...", "Deciphering desires..."
  ];

  const randomMessage = funnyMessages[Math.floor(Math.random() * funnyMessages.length)];

  // Replace winner panel with "looking" message to prevent layout shift
  const winnerPanel = document.getElementById('winnerPanel');
  winnerPanel.classList.remove('hidden');
  winnerPanel.style.visibility = 'visible';
  winnerPanel.style.opacity = '1';
  winnerPanel.style.transition = 'opacity 0.3s ease';
  winnerPanel.innerHTML = `
    <div class="text-sm uppercase tracking-wider text-blue-400 mb-1">Spinning...</div>
    <div class="flex items-center gap-3">
      <div class="h-12 w-12 rounded-xl bg-slate-800/60 border border-slate-700 grid place-content-center">
        <div class="text-lg">🎲</div>
      </div>
      <div>
        <div class="font-semibold text-lg text-slate-300">Looking for a winner...</div>
        <div class="text-xs text-slate-400">${randomMessage}</div>
      </div>
    </div>`;

  try {
    const params = new URLSearchParams();
    if (currentTab !== 'all') params.set('type', currentTab);
    if (currentTags.length) params.set('tags', currentTags.join(','));

    const res = await fetch('/api/spin?' + params.toString());
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();

    const pool = data.pool || [];
    const winner = data.winner;

    console.log('Pool size:', pool.length, 'Winner:', winner?.title);

    if (!pool.length || !winner) {
      document.getElementById('wheelWrap').classList.add('hidden');
      const panel = document.getElementById('winnerPanel');
      panel.classList.remove('hidden');
      panel.innerHTML = '<div class="text-slate-400">No matching items. Adjust filters or add more.</div>';
      return;
    }

    // Rebuild wheel (resets to 0deg and ensures clean state)
    buildWheel(pool);

    const n = pool.length;
    const index = pool.findIndex(it => it.id === winner.id);
    const wheel = document.getElementById('wheel');
    const targetAngle = computeTargetAngle(index, n);

    // Duration scales with rotation amount for more realistic physics
    const durationMs = Math.round(3000 + (targetAngle / 360) * 200); // ~3-4.5s based on rotations

    console.log('Spin details:', {
      winnerTitle: winner.title,
      rotations: Math.round(targetAngle / 360),
      durationMs
    });

    isSpinning = true;

    // Small delay to ensure wheel is properly rendered before animation
    setTimeout(() => {
      animateWheelTo(targetAngle, durationMs);
    }, 50);

    const done = () => {
      console.log('Spin animation completed');
      wheel.removeEventListener('transitionend', done);
      isSpinning = false;

      const panel = document.getElementById('winnerPanel');
      panel.classList.remove('hidden');
      const tagsHtml = (winner.tags && winner.tags.length)
        ? ('<div class="mt-1 flex flex-wrap gap-1">' + winner.tags.map(t => '<span class="text-[10px] chip rounded-full px-2 py-0.5">' + t + '</span>').join('') + '</div>')
        : '';
      panel.innerHTML = `
        <div class="text-sm uppercase tracking-wider text-emerald-300 mb-1">Winner</div>
        <div class="flex items-center gap-3">
          ${winner.coverUrl ? `<img src="${winner.coverUrl}" class="h-12 w-12 rounded-xl object-cover"/>` : fallbackBlock(winner.title, 'h-12 w-12 rounded-xl')}
          <div>
            <div class="font-semibold text-lg flex items-center gap-2">${winner.title} <span class="text-emerald-400">✔</span></div>
            <div class="text-xs text-slate-400">${winner.platform || ''}</div>
            ${tagsHtml}
          </div>
        </div>`;
    };

    wheel.addEventListener('transitionend', done, { once: true });

    // Fallback timeout in case transitionend doesn't fire
    setTimeout(() => {
      if (isSpinning) {
        console.log('Fallback timeout triggered');
        done();
      }
    }, durationMs + 500);

  } catch (error) {
    console.error('Failed to spin wheel:', error);
    showError('Failed to spin the wheel. Please try again.');
    isSpinning = false;
  }
}

/* ---------- Init ---------- */
applyTheme();
setTab('all');
