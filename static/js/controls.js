/* controls.js: wires the page together.
 *   - per-structure operation forms -> POST to the Flask API (the browser sends the current structure)
 *   - plays the returned stepLog through Animation.Player and draws it with Renderer
 *   - owns undo / redo / clear (the server keeps no state), the complexity + pseudocode panels,
 *     BFS-vs-DFS comparison, test-case generation, dark mode and the quiz button.
 * User-provided text is only ever inserted with textContent, never innerHTML.
 */
(function () {
  'use strict';

  // ------------------------------------------------------------------ structure / operation catalogue
  const EMPTY = {
    bst: null,
    graph: { vertices: [], edges: [] },
    heap: { array: [] },
    stack: { items: [] },
    queue: { items: [] }
  };

  const VALUE = { name: 'value', label: 'Value (integer)', kind: 'text', placeholder: 'e.g. 42' };
  const SOURCE = { name: 'source', label: 'Source vertex', kind: 'vertex', role: 'source' };
  const DEST = { name: 'destination', label: 'Destination (optional)', kind: 'vertex-optional', role: 'dest' };

  const STRUCTS = {
    bst: {
      label: 'Binary Search Tree', stateKey: 'tree',
      ops: [
        { id: 'insert', label: 'Insert', path: '/api/bst/insert', keys: ['bst.insert'], fields: [VALUE] },
        { id: 'delete', label: 'Delete', path: '/api/bst/delete', keys: ['bst.delete'], fields: [VALUE] },
        { id: 'search', label: 'Search', path: '/api/bst/search', keys: ['bst.search'],
          fields: [{ name: 'value', label: 'Value to find', kind: 'text', placeholder: 'e.g. 42' }] },
        { id: 'traverse', label: 'Traverse (pre / in / post)', path: '/api/bst/traverse', keys: ['bst.traverse'],
          fields: [{ name: 'order', label: 'Order', kind: 'select',
                     options: [['in', 'In-order'], ['pre', 'Pre-order'], ['post', 'Post-order']] }] }
      ]
    },
    graph: {
      label: 'Graph', stateKey: 'graph',
      ops: [
        { id: 'add_vertex', label: 'Add vertex', path: '/api/graph/add_vertex', keys: ['graph.add_vertex'],
          fields: [{ name: 'vertex', label: 'New vertex name', kind: 'text', placeholder: 'e.g. A' }] },
        { id: 'remove_vertex', label: 'Remove vertex', path: '/api/graph/remove_vertex', keys: ['graph.remove_vertex'],
          fields: [{ name: 'vertex', label: 'Vertex', kind: 'vertex', role: 'source' }] },
        { id: 'add_edge', label: 'Add edge', path: '/api/graph/add_edge', keys: ['graph.add_edge'],
          fields: [{ name: 'u', label: 'Vertex u', kind: 'vertex', role: 'source' },
                   { name: 'v', label: 'Vertex v', kind: 'vertex', role: 'dest' }] },
        { id: 'remove_edge', label: 'Remove edge', path: '/api/graph/remove_edge', keys: ['graph.remove_edge'],
          fields: [{ name: 'u', label: 'Vertex u', kind: 'vertex', role: 'source' },
                   { name: 'v', label: 'Vertex v', kind: 'vertex', role: 'dest' }] },
        { id: 'bfs', label: 'Breadth-First Search (BFS)', path: '/api/graph/bfs', keys: ['graph.bfs'], fields: [SOURCE, DEST] },
        { id: 'dfs', label: 'Depth-First Search (DFS)', path: '/api/graph/dfs', keys: ['graph.dfs'], fields: [SOURCE, DEST] },
        { id: 'compare', label: 'Compare BFS vs DFS (side by side)', path: '/api/graph/compare',
          keys: ['graph.bfs', 'graph.dfs'], compare: true, fields: [SOURCE, DEST] }
      ]
    },
    heap: {
      label: 'Priority Queue (min-heap)', stateKey: 'heap',
      ops: [
        { id: 'insert', label: 'Insert (sift-up)', path: '/api/heap/insert', keys: ['heap.insert'], fields: [VALUE] },
        { id: 'extract_min', label: 'Extract-min (sift-down)', path: '/api/heap/extract_min', keys: ['heap.extract_min'], fields: [] },
        { id: 'peek', label: 'Peek', path: '/api/heap/peek', keys: ['heap.peek'], fields: [] }
      ]
    },
    stack: {
      label: 'Stack', stateKey: 'stack',
      ops: [
        { id: 'push', label: 'push()', path: '/api/stack/push', keys: ['stack.push'], fields: [VALUE] },
        { id: 'pop', label: 'pop()', path: '/api/stack/pop', keys: ['stack.pop'], fields: [] },
        { id: 'peek', label: 'peek()', path: '/api/stack/peek', keys: ['stack.peek'], fields: [] },
        { id: 'is_empty', label: 'isEmpty()', path: '/api/stack/is_empty', keys: ['stack.is_empty'], fields: [] }
      ]
    },
    queue: {
      label: 'Queue', stateKey: 'queue',
      ops: [
        { id: 'enqueue', label: 'enqueue()', path: '/api/queue/enqueue', keys: ['queue.enqueue'], fields: [VALUE] },
        { id: 'dequeue', label: 'dequeue()', path: '/api/queue/dequeue', keys: ['queue.dequeue'], fields: [] },
        { id: 'front', label: 'front()', path: '/api/queue/front', keys: ['queue.front'], fields: [] },
        { id: 'rear', label: 'rear()', path: '/api/queue/rear', keys: ['queue.rear'], fields: [] },
        { id: 'is_empty', label: 'isEmpty()', path: '/api/queue/is_empty', keys: ['queue.is_empty'], fields: [] }
      ]
    }
  };

  // ------------------------------------------------------------------ app state
  const store = {};
  Object.keys(STRUCTS).forEach(function (k) {
    store[k] = { state: clone(EMPTY[k]), history: new Animation.History(), source: '', dest: '' };
  });
  let current = 'bst';
  let reference = null;          // {complexity, pseudocode} from GET /api/reference
  let views = [];                // [{title, type, steps}] currently loaded into the player
  let pcLists = [];              // <ol> elements, one per pseudocode block
  let panelsLive = false;        // true while the pseudocode panel belongs to the loaded views
  let busy = false;

  // ------------------------------------------------------------------ DOM
  const $ = function (id) { return document.getElementById(id); };
  const tabsEl = $('structure-tabs'), opSelect = $('op-select'), fieldsEl = $('op-fields');
  const messageEl = $('message'), viewsEl = $('views');
  const complexityEl = $('complexity'), pseudoEl = $('pseudocode');
  const btn = {
    run: $('btn-run'), play: $('btn-play'), back: $('btn-back'), forward: $('btn-forward'),
    restart: $('btn-restart'), undo: $('btn-undo'), redo: $('btn-redo'), clear: $('btn-clear'),
    generate: $('btn-generate'), quiz: $('btn-quiz'), theme: $('btn-theme')
  };
  const scrub = $('scrub'), speed = $('speed'), stepCounter = $('step-counter');
  const viewEls = [0, 1].map(function (i) {
    const el = $('view-' + i);
    return {
      el: el, title: el.querySelector('.view-title'), canvas: el.querySelector('canvas'),
      desc: el.querySelector('.step-desc'), aux: el.querySelector('.aux'),
      order: el.querySelector('.order'), counters: el.querySelector('.counters')
    };
  });

  function clone(x) { return x === undefined ? undefined : JSON.parse(JSON.stringify(x)); }

  function mk(tag, text, cls) {
    const e = document.createElement(tag);
    if (text !== undefined && text !== null) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  }

  // ------------------------------------------------------------------ messages
  function showMessage(kind, text) {
    messageEl.className = 'message ' + kind;
    messageEl.textContent = text;
  }
  function clearMessage() { messageEl.className = 'message'; messageEl.textContent = ''; }

  // ------------------------------------------------------------------ player
  const player = new Animation.Player({ onRender: renderFrame, onChange: updateControls });

  function renderFrame(index) {
    views.forEach(function (v, i) {
      const step = v.steps[Math.min(index, v.steps.length - 1)];
      const ve = viewEls[i];
      Renderer.draw(ve.canvas, v.type, step.structureState, step);
      renderInfo(ve, step, v.type);
      if (panelsLive && pcLists[i]) {
        Array.prototype.forEach.call(pcLists[i].children, function (li, n) {
          li.classList.toggle('active', n === step.line);
        });
      }
    });
  }

  function renderInfo(ve, step, type) {
    ve.desc.replaceChildren(mk('span', step.action, 'badge'), document.createTextNode(step.description));

    // BFS queue / DFS stack panel
    ve.aux.replaceChildren();
    const list = step.aux && (step.aux.queue || step.aux.stack);
    if (list) {
      const isQueue = !!step.aux.queue;
      ve.aux.appendChild(mk('span', isQueue ? 'Queue (front → rear):' : 'Stack (bottom → top):', 'label'));
      if (list.length === 0) ve.aux.appendChild(mk('span', '(empty)', 'chip'));
      list.forEach(function (id, i) {
        ve.aux.appendChild(mk('span', id, 'chip' + (!isQueue && i === list.length - 1 ? ' top' : '')));
      });
    }

    // traversal order so far (graph traversals and BST traversals)
    ve.order.replaceChildren();
    const seen = step.highlight.visited;
    if ((type === 'graph' || type === 'bst') && seen.length > 0) {
      ve.order.appendChild(mk('span', 'Visited / traversal order:', 'label'));
      seen.forEach(function (id) {
        ve.order.appendChild(mk('span', id, 'chip visited'));
      });
    }

    ve.counters.replaceChildren(mk('span',
      'Comparisons: ' + step.counters.comparisons + '  ·  Operations: ' + step.counters.operations, 'counters'));
  }

  function updateControls() {
    btn.play.textContent = player.playing ? '⏸ Pause' : '▶ Play';
    btn.play.disabled = !player.canPlay();
    btn.forward.disabled = !player.canForward();
    btn.back.disabled = !player.canBack();
    btn.restart.disabled = !player.hasSteps();
    scrub.disabled = !player.hasSteps();
    scrub.max = Math.max(0, player.total - 1);
    scrub.value = player.index;
    stepCounter.textContent = player.hasSteps() ? 'Step ' + (player.index + 1) + ' / ' + player.total : 'No steps';
    const h = store[current].history;
    btn.undo.disabled = !h.canUndo();
    btn.redo.disabled = !h.canRedo();
  }

  // ------------------------------------------------------------------ views
  function loadViews(list, autoplay) {
    views = list.map(function (v) { return { title: v.title, type: v.type, steps: v.resp.steps }; });
    viewsEl.classList.toggle('compare', list.length === 2);
    viewEls[1].el.hidden = list.length < 2;
    views.forEach(function (v, i) {
      viewEls[i].title.textContent = v.title;
      Renderer.resize(viewEls[i].canvas);
    });
    renderPanels(list.map(function (v) {
      return { title: v.resp.complexity.title, complexity: v.resp.complexity, pseudocode: v.resp.pseudocode };
    }), true);
    player.load(Math.max.apply(null, views.map(function (v) { return v.steps.length; })), autoplay);
  }

  function showStatic() {
    player.clear();
    views = [];
    viewsEl.classList.remove('compare');
    viewEls[1].el.hidden = true;
    viewEls[0].title.textContent = STRUCTS[current].label;
    Renderer.resize(viewEls[0].canvas);
    Renderer.draw(viewEls[0].canvas, current, store[current].state, null);
    ['desc', 'aux', 'order', 'counters'].forEach(function (k) { viewEls[0][k].replaceChildren(); });
    showSelectedOpPanels();
    updateControls();
  }

  // ------------------------------------------------------------------ complexity + pseudocode panels
  function renderPanels(entries, live) {
    panelsLive = live;
    complexityEl.replaceChildren();
    pseudoEl.replaceChildren();
    pcLists = [];
    entries.forEach(function (e) {
      if (e.complexity) {
        const c = e.complexity;
        complexityEl.appendChild(mk('h3', c.title));
        const table = mk('table', undefined, 'complexity');
        [['Worst-case time', c.worst, 'main'], ['Space', c.space, 'main'],
         ['Best case', c.best, ''], ['Average case', c.average, '']].forEach(function (row) {
          const tr = mk('tr', undefined, row[2]);
          tr.appendChild(mk('td', row[0]));
          tr.appendChild(mk('td', row[1]));
          table.appendChild(tr);
        });
        complexityEl.appendChild(table);
        if (c.note) complexityEl.appendChild(mk('p', c.note, 'note'));
      }
      const block = mk('div');
      if (entries.length > 1) block.appendChild(mk('h4', e.title));
      const ol = mk('ol', undefined, 'pc');
      (e.pseudocode || []).forEach(function (line) { ol.appendChild(mk('li', line)); });
      block.appendChild(ol);
      pseudoEl.appendChild(block);
      pcLists.push(ol);
    });
    if (entries.length === 0) complexityEl.appendChild(mk('p', 'Select an operation to see its complexity.', 'note'));
  }

  function showSelectedOpPanels() {
    const op = currentOp();
    if (!reference || !op) { renderPanels([], false); return; }
    renderPanels(op.keys.map(function (k) {
      return { title: reference.complexity[k].title, complexity: reference.complexity[k], pseudocode: reference.pseudocode[k] };
    }), false);
  }

  // ------------------------------------------------------------------ operation form
  function currentOp() {
    return STRUCTS[current].ops.find(function (o) { return o.id === opSelect.value; }) || STRUCTS[current].ops[0];
  }

  function readFields() {
    const out = {};
    fieldsEl.querySelectorAll('[data-name]').forEach(function (inp) { out[inp.dataset.name] = inp.value; });
    return out;
  }

  function buildFields(preset) {
    const op = currentOp();
    const prev = preset || readFields();
    const s = store[current];
    const vertices = (s.state && s.state.vertices) || [];
    fieldsEl.replaceChildren();
    op.fields.forEach(function (f) {
      const label = mk('label', f.label, 'field');
      let input;
      if (f.kind === 'select') {
        input = mk('select');
        f.options.forEach(function (o) { const opt = mk('option', o[1]); opt.value = o[0]; input.appendChild(opt); });
      } else if (f.kind === 'vertex' || f.kind === 'vertex-optional') {
        input = mk('select');
        if (f.kind === 'vertex-optional') { const none = mk('option', '(none: full traversal)'); none.value = ''; input.appendChild(none); }
        if (vertices.length === 0 && f.kind === 'vertex') { const e = mk('option', '(no vertices yet)'); e.value = ''; input.appendChild(e); }
        vertices.forEach(function (v) { const opt = mk('option', v); opt.value = v; input.appendChild(opt); });
      } else {
        input = mk('input');
        input.type = 'text';
        input.inputMode = f.name === 'value' ? 'numeric' : 'text';
        input.placeholder = f.placeholder || '';
        input.maxLength = 12;
      }
      input.dataset.name = f.name;
      const wanted = prev[f.name] !== undefined ? prev[f.name]
        : (f.role === 'source' ? s.source : f.role === 'dest' ? s.dest : undefined);
      if (wanted !== undefined && input.tagName === 'SELECT') {
        if (Array.prototype.some.call(input.options, function (o) { return o.value === wanted; })) input.value = wanted;
      } else if (wanted !== undefined) {
        input.value = wanted;
      }
      label.appendChild(input);
      fieldsEl.appendChild(label);
    });
  }

  function buildOpSelect() {
    opSelect.replaceChildren();
    STRUCTS[current].ops.forEach(function (o) { const opt = mk('option', o.label); opt.value = o.id; opSelect.appendChild(opt); });
  }

  function onOpChange() {
    buildFields({});
    showSelectedOpPanels();      // complexity panel follows the selected operation
    clearMessage();
  }

  // ------------------------------------------------------------------ structure tabs
  function buildTabs() {
    tabsEl.replaceChildren();
    Object.keys(STRUCTS).forEach(function (k) {
      const b = mk('button', STRUCTS[k].label, 'tab');
      b.type = 'button';
      b.setAttribute('role', 'tab');
      b.dataset.type = k;
      b.addEventListener('click', function () { selectStructure(k); });
      tabsEl.appendChild(b);
    });
  }

  function selectStructure(type) {
    current = type;
    tabsEl.querySelectorAll('.tab').forEach(function (t) { t.setAttribute('aria-selected', String(t.dataset.type === type)); });
    buildOpSelect();
    buildFields({});
    const isGraph = type === 'graph';
    $('graph-hint').hidden = !isGraph;
    $('gen-edges-wrap').hidden = !isGraph;
    $('gen-range').hidden = isGraph;
    $('gen-dist-wrap').hidden = isGraph;
    $('gen-count').previousSibling.textContent = isGraph ? 'Number of vertices ' : 'Number of values ';
    clearMessage();
    showStatic();
  }

  // ------------------------------------------------------------------ server calls
  function post(path, body) {
    return fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      .catch(function () { throw new Error('Could not reach the server. Is it still running?'); })
      .then(function (res) {
        return res.json().catch(function () { return { error: 'Unexpected server response' }; })
          .then(function (data) {
            if (!res.ok || data.error) throw new Error(data.error || 'Request failed');
            return data;
          });
      });
  }

  function setBusy(b) { busy = b; btn.run.disabled = b; btn.generate.disabled = b; }

  function commit(operation, params, resp, title) {
    const s = store[current];
    const before = s.state;
    const after = clone(resp.finalState);
    if (JSON.stringify(before) !== JSON.stringify(after)) {
      s.history.push({ operation: operation, params: params, before: clone(before), after: clone(after),
                       steps: resp.steps, resp: resp, title: title });
      s.state = after;
    }
  }

  function runOperation() {
    if (busy) return;
    const op = currentOp();
    const s = store[current];
    const params = readFields();
    const body = {};
    body[STRUCTS[current].stateKey] = clone(s.state);
    Object.keys(params).forEach(function (k) { body[k] = params[k]; });
    // remember the vertex choices
    if (current === 'graph') {
      op.fields.forEach(function (f) { if (f.role === 'source') s.source = params[f.name]; if (f.role === 'dest') s.dest = params[f.name]; });
    }
    setBusy(true);
    post(op.path, body).then(function (data) {
      clearMessage();
      if (op.compare) {
        loadViews([{ title: 'BFS (queue)', type: 'graph', resp: data.bfs },
                   { title: 'DFS (stack)', type: 'graph', resp: data.dfs }], true);
      } else {
        commit(op.id, params, data, op.label);
        loadViews([{ title: op.label, type: current, resp: data }], true);
        if (current === 'graph') buildFields(readFields());
      }
      describeResult(data);
    }).catch(function (err) {
      showMessage('error', err.message);       // structure unchanged, no animation started
    }).then(function () { setBusy(false); updateControls(); });
  }

  function describeResult(data) {
    const r = data.result || {};
    if (r.found === true && r.path) showMessage('info', 'Path found: ' + r.path.join(' → '));
    else if (r.found === true) showMessage('info', 'Found. Path taken: ' + (r.path || []).join(' → '));
    else if (r.found === false) showMessage('info', 'Not found.');
    else if (r.popped !== undefined) showMessage('info', 'Popped ' + r.popped);
    else if (r.dequeued !== undefined) showMessage('info', 'Dequeued ' + r.dequeued);
    else if (r.min !== undefined) showMessage('info', 'Extracted minimum ' + r.min);
    else if (r.empty !== undefined) showMessage('info', 'isEmpty() = ' + (r.empty ? 'True' : 'False'));
    else if (r.value !== undefined) showMessage('info', 'Value: ' + r.value);
  }

  function generate() {
    if (busy) return;
    const body = {
      structure: current,
      count: $('gen-count').value,
      min: $('gen-min').value,
      max: $('gen-max').value,
      distribution: $('gen-dist').value,
      edges: $('gen-edges').value
    };
    setBusy(true);
    post('/api/generate', body).then(function (data) {
      clearMessage();
      commit('generate', body, data, 'Generate test case');
      loadViews([{ title: 'Generated test case', type: current, resp: data }], false);
      if (current === 'graph') buildFields(readFields());
    }).catch(function (err) { showMessage('error', err.message); })
      .then(function () { setBusy(false); updateControls(); });
  }

  // ------------------------------------------------------------------ undo / redo / clear (browser only)
  function undo() {
    const e = store[current].history.undo();
    if (!e) return;
    store[current].state = clone(e.before);
    showStatic();
    buildFields(readFields());
    showMessage('info', 'Undid: ' + e.title);
  }

  function redo() {
    const e = store[current].history.redo();
    if (!e) return;
    store[current].state = clone(e.after);
    loadViews([{ title: e.title, type: current, resp: e.resp }], false);   // paused at step 0
    buildFields(readFields());
    showMessage('info', 'Redid: ' + e.title + '. Press Play or Step to watch it again.');
  }

  function clearAll() {
    const s = store[current];
    s.state = clone(EMPTY[current]);
    s.history.clear();
    s.source = ''; s.dest = '';
    buildFields({});
    clearMessage();
    showStatic();
  }

  // ------------------------------------------------------------------ theme
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    btn.theme.setAttribute('aria-pressed', String(theme === 'dark'));
    btn.theme.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
    Renderer.redrawAll();
  }

  function initTheme() {
    let theme = null;
    try { theme = localStorage.getItem('dsa-theme'); } catch (e) { /* storage unavailable */ }
    if (!theme) theme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    applyTheme(theme);
  }

  // ------------------------------------------------------------------ events
  $('op-form').addEventListener('submit', function (e) { e.preventDefault(); runOperation(); });
  $('gen-form').addEventListener('submit', function (e) { e.preventDefault(); generate(); });
  opSelect.addEventListener('change', onOpChange);

  btn.play.addEventListener('click', function () { player.toggle(); });
  btn.forward.addEventListener('click', function () { player.stepForward(); });
  btn.back.addEventListener('click', function () { player.stepBack(); });
  btn.restart.addEventListener('click', function () { player.restart(); });
  scrub.addEventListener('input', function () { player.goTo(Number(scrub.value)); });
  speed.addEventListener('input', function () { player.setSpeed(Number(speed.value)); });
  btn.undo.addEventListener('click', undo);
  btn.redo.addEventListener('click', redo);
  btn.clear.addEventListener('click', clearAll);
  btn.quiz.addEventListener('click', function () { Quiz.start(current, STRUCTS[current].label); });
  btn.theme.addEventListener('click', function () {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('dsa-theme', next); } catch (e) { /* ignore */ }
    applyTheme(next);
  });

  // click a vertex to choose the source, Shift+click for the destination
  viewEls[0].canvas.addEventListener('click', function (ev) {
    if (current !== 'graph') return;
    const id = Renderer.hitTest(viewEls[0].canvas, ev.clientX, ev.clientY);
    if (id === null) return;
    const s = store.graph;
    if (ev.shiftKey) s.dest = id; else s.source = id;
    const prev = readFields();
    currentOp().fields.forEach(function (f) {
      if (f.role === (ev.shiftKey ? 'dest' : 'source')) prev[f.name] = id;
    });
    buildFields(prev);
  });

  viewEls.forEach(function (ve) {
    if (typeof ResizeObserver !== 'undefined') new ResizeObserver(function () { Renderer.resize(ve.canvas); }).observe(ve.canvas);
  });
  window.addEventListener('resize', function () { viewEls.forEach(function (ve) { Renderer.resize(ve.canvas); }); });

  // ------------------------------------------------------------------ start
  buildTabs();
  initTheme();
  fetch('/api/reference').then(function (r) { return r.json(); })
    .then(function (data) { reference = data; })
    .catch(function () { showMessage('error', 'Could not load complexity information from the server.'); })
    .then(function () { selectStructure('bst'); });
})();
