/* canvas.js: draws every structure on an HTML canvas from a plain state + step.
 * It contains no algorithms: it only renders what the stepLog says.
 * Exposes window.Renderer = { draw, resize, redrawAll, hitTest }.
 */
(function (global) {
  'use strict';

  function css(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function palette() {
    return {
      bg: css('--canvas-bg'), text: css('--text'), muted: css('--muted'), edge: css('--edge'),
      node: css('--node-fill'), nodeStroke: css('--node-stroke'),
      current: css('--c-current'), frontier: css('--c-frontier'), visited: css('--c-visited'),
      compared: css('--c-compared'), found: css('--c-found')
    };
  }

  const EMPTY_HL = { current: [], visited: [], compared: [], edges: [] };
  const canvases = new Set();

  // ------------------------------------------------------------------ styling
  function auxIds(aux) {
    if (!aux) return [];
    return aux.queue || aux.stack || [];
  }

  function styleFor(id, hl, aux, P) {
    const has = function (arr) { return arr && arr.indexOf(id) !== -1; };
    if (has(hl.current)) return { fill: P.current, stroke: P.text, width: 4, dash: [] };
    if (has(hl.compared)) return { fill: P.compared, stroke: P.text, width: 3, dash: [2, 3] };
    if (auxIds(aux).indexOf(id) !== -1) return { fill: P.frontier, stroke: P.text, width: 3, dash: [6, 3] };
    if (has(hl.visited)) return { fill: P.visited, stroke: P.text, width: 2, dash: [] };
    return { fill: P.node, stroke: P.nodeStroke, width: 1.5, dash: [] };
  }

  function drawNode(ctx, x, y, r, label, st, P) {
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle = st.fill;
    ctx.fill();
    ctx.setLineDash(st.dash);
    ctx.lineWidth = st.width;
    ctx.strokeStyle = st.stroke;
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = (st.fill === P.node) ? P.text : '#111';
    ctx.font = 'bold ' + Math.max(8, Math.min(15, r * 0.95)) + 'px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(String(label), x, y + 1);
  }

  function drawLine(ctx, x1, y1, x2, y2, color, width) {
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
  }

  function drawMessage(ctx, W, H, text, P) {
    ctx.fillStyle = P.muted;
    ctx.font = '16px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, W / 2, H / 2);
  }

  function edgeHighlighted(hl, a, b) {
    return (hl.edges || []).some(function (e) {
      return (e[0] === a && e[1] === b) || (e[0] === b && e[1] === a);
    });
  }

  // ------------------------------------------------------------------ BST
  function drawBST(ctx, W, H, state, hl, aux, P, layout) {
    if (!state) { drawMessage(ctx, W, H, 'Empty tree: insert a value to begin', P); return; }
    const order = [];
    let maxDepth = 0;
    (function walk(n, d) {
      if (!n) return;
      walk(n.left, d + 1);
      order.push({ n: n, d: d });
      maxDepth = Math.max(maxDepth, d);
      walk(n.right, d + 1);
    })(state, 0);

    const count = order.length;
    const dx = Math.min(64, (W - 60) / Math.max(count, 1));
    const dy = Math.min(72, (H - 80) / Math.max(maxDepth, 1));
    const r = Math.max(6, Math.min(22, dx * 0.48, dy * 0.48));
    const startX = W / 2 - ((count - 1) * dx) / 2;
    const pos = new Map();
    order.forEach(function (o, i) { pos.set(o.n, { x: startX + i * dx, y: 40 + o.d * dy }); });

    (function edges(n) {
      if (!n) return;
      const p = pos.get(n);
      [n.left, n.right].forEach(function (c) {
        if (c) {
          const q = pos.get(c);
          const active = (hl.current || []).indexOf(c.value) !== -1 && (hl.visited || []).indexOf(n.value) !== -1;
          drawLine(ctx, p.x, p.y, q.x, q.y, active ? P.current : P.edge, active ? 3 : 1.5);
          edges(c);
        }
      });
    })(state);

    order.forEach(function (o) {
      const p = pos.get(o.n);
      layout.nodes.push({ id: o.n.value, x: p.x, y: p.y, r: r });
      drawNode(ctx, p.x, p.y, r, o.n.value, styleFor(o.n.value, hl, aux, P), P);
    });
  }

  // ------------------------------------------------------------------ graph
  function graphPositions(vertices, W, H) {
    const n = vertices.length;
    const cx = W / 2, cy = H / 2;
    const R = Math.max(30, Math.min(W, H) / 2 - 38);
    const pos = {};
    vertices.forEach(function (v, i) {
      if (n === 1) { pos[v] = { x: cx, y: cy }; return; }
      const a = -Math.PI / 2 + (2 * Math.PI * i) / n;
      pos[v] = { x: cx + R * Math.cos(a), y: cy + R * Math.sin(a) };
    });
    const r = Math.max(9, Math.min(24, (Math.PI * R / Math.max(n, 1)) * 0.8));
    return { pos: pos, r: r };
  }

  function drawGraph(ctx, W, H, state, hl, aux, P, layout) {
    const vertices = (state && state.vertices) || [];
    const edges = (state && state.edges) || [];
    if (vertices.length === 0) { drawMessage(ctx, W, H, 'Empty graph: add vertices to begin', P); return; }
    const g = graphPositions(vertices, W, H);

    edges.forEach(function (e) {
      const a = g.pos[e[0]], b = g.pos[e[1]];
      if (!a || !b) return;
      const active = edgeHighlighted(hl, e[0], e[1]);
      drawLine(ctx, a.x, a.y, b.x, b.y, active ? P.current : P.edge, active ? 4 : 1.5);
    });
    vertices.forEach(function (v) {
      const p = g.pos[v];
      layout.nodes.push({ id: v, x: p.x, y: p.y, r: g.r });
      drawNode(ctx, p.x, p.y, g.r, v, styleFor(v, hl, aux, P), P);
    });
  }

  // ------------------------------------------------------------------ heap
  function drawHeap(ctx, W, H, state, hl, aux, P, layout) {
    const arr = (state && state.array) || [];
    if (arr.length === 0) { drawMessage(ctx, W, H, 'Empty priority queue: insert a value to begin', P); return; }
    const n = arr.length;
    const levels = Math.floor(Math.log2(n)) + 1;
    const treeH = H - 90;
    const dy = Math.min(80, (treeH - 50) / Math.max(levels - 1, 1));
    const r = Math.max(7, Math.min(20, ((W - 40) / Math.pow(2, levels - 1)) / 2 * 0.9));
    const pos = arr.map(function (_, i) {
      const l = Math.floor(Math.log2(i + 1));
      const p = i + 1 - Math.pow(2, l);
      return { x: 20 + ((p + 0.5) / Math.pow(2, l)) * (W - 40), y: 36 + l * dy };
    });

    for (let i = 1; i < n; i++) {
      const par = Math.floor((i - 1) / 2);
      const active = (hl.current || []).indexOf(i) !== -1 && (hl.compared || []).indexOf(par) !== -1 ||
                     (hl.current || []).indexOf(par) !== -1 && (hl.compared || []).indexOf(i) !== -1;
      drawLine(ctx, pos[par].x, pos[par].y, pos[i].x, pos[i].y, active ? P.current : P.edge, active ? 3 : 1.5);
    }
    arr.forEach(function (val, i) {
      layout.nodes.push({ id: i, x: pos[i].x, y: pos[i].y, r: r });
      drawNode(ctx, pos[i].x, pos[i].y, r, val, styleFor(i, hl, aux, P), P);
    });

    // array strip below the tree, so the array form is visible too
    const cell = Math.min(44, (W - 40) / n);
    const x0 = W / 2 - (cell * n) / 2;
    const y0 = H - 52;
    arr.forEach(function (val, i) {
      const st = styleFor(i, hl, aux, P);
      ctx.fillStyle = st.fill;
      ctx.fillRect(x0 + i * cell, y0, cell, 28);
      ctx.setLineDash(st.dash);
      ctx.lineWidth = Math.min(st.width, 3);
      ctx.strokeStyle = st.stroke;
      ctx.strokeRect(x0 + i * cell, y0, cell, 28);
      ctx.setLineDash([]);
      ctx.fillStyle = st.fill === P.node ? P.text : '#111';
      ctx.font = 'bold ' + Math.max(8, Math.min(13, cell * 0.4)) + 'px system-ui, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(String(val), x0 + i * cell + cell / 2, y0 + 15);
      ctx.fillStyle = P.muted;
      ctx.font = '10px system-ui, sans-serif';
      ctx.fillText(String(i), x0 + i * cell + cell / 2, y0 + 40);
    });
  }

  // ------------------------------------------------------------------ stack
  function drawBox(ctx, x, y, w, h, label, st, P) {
    ctx.fillStyle = st.fill;
    ctx.fillRect(x, y, w, h);
    ctx.setLineDash(st.dash);
    ctx.lineWidth = st.width;
    ctx.strokeStyle = st.stroke;
    ctx.strokeRect(x, y, w, h);
    ctx.setLineDash([]);
    ctx.fillStyle = st.fill === P.node ? P.text : '#111';
    ctx.font = 'bold ' + Math.max(9, Math.min(16, h * 0.5)) + 'px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(String(label), x + w / 2, y + h / 2 + 1);
  }

  function drawStack(ctx, W, H, state, hl, aux, P, layout) {
    const items = (state && state.items) || [];
    const baseY = H - 30;
    const bw = 170, bx = W / 2 - bw / 2;
    // floor
    drawLine(ctx, bx - 14, baseY, bx + bw + 14, baseY, P.text, 3);
    if (items.length === 0) { drawMessage(ctx, W, H, 'Empty stack: push a value to begin', P); return; }
    const bh = Math.min(40, (H - 80) / items.length);
    items.forEach(function (v, i) {
      const y = baseY - (i + 1) * bh;
      layout.nodes.push({ id: i, x: W / 2, y: y + bh / 2, r: bh / 2 });
      drawBox(ctx, bx, y, bw, bh - 3, v, styleFor(i, hl, aux, P), P);
    });
    const topY = baseY - items.length * bh + (bh - 3) / 2;
    ctx.fillStyle = P.text;
    ctx.font = 'bold 14px system-ui, sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText('TOP →', bx - 10, topY);
    ctx.textAlign = 'left';
    ctx.fillStyle = P.muted;
    ctx.font = '12px system-ui, sans-serif';
    ctx.fillText('bottom (index 0)', bx + bw + 12, baseY - bh / 2);
  }

  // ------------------------------------------------------------------ queue
  function drawQueue(ctx, W, H, state, hl, aux, P, layout) {
    const items = (state && state.items) || [];
    if (items.length === 0) { drawMessage(ctx, W, H, 'Empty queue: enqueue a value to begin', P); return; }
    const n = items.length;
    const bw = Math.min(72, (W - 140) / n);
    const bh = 56;
    const x0 = W / 2 - (bw * n) / 2;
    const y0 = H / 2 - bh / 2;
    items.forEach(function (v, i) {
      layout.nodes.push({ id: i, x: x0 + i * bw + bw / 2, y: y0 + bh / 2, r: bw / 2 });
      drawBox(ctx, x0 + i * bw, y0, bw - 3, bh, v, styleFor(i, hl, aux, P), P);
    });
    ctx.fillStyle = P.text;
    ctx.font = 'bold 14px system-ui, sans-serif';
    ctx.textBaseline = 'middle';
    ctx.textAlign = 'center';
    ctx.fillText('FRONT', x0 + bw / 2, y0 - 34);
    ctx.fillText('▼', x0 + bw / 2, y0 - 16);
    ctx.fillText('REAR', x0 + (n - 1) * bw + bw / 2, y0 + bh + 34);
    ctx.fillText('▲', x0 + (n - 1) * bw + bw / 2, y0 + bh + 16);
    ctx.fillStyle = P.muted;
    ctx.font = '13px system-ui, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText('dequeue (out) ←', x0 - 8, y0 + bh / 2);
    ctx.textAlign = 'left';
    ctx.fillText('← enqueue (in)', x0 + n * bw + 4, y0 + bh / 2);
  }

  const DRAWERS = { bst: drawBST, graph: drawGraph, heap: drawHeap, stack: drawStack, queue: drawQueue };

  // ------------------------------------------------------------------ public API
  function resize(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    canvas._cssW = w;
    canvas._cssH = h;
    canvas._dpr = dpr;
    if (canvas._last) draw(canvas, canvas._last.type, canvas._last.state, canvas._last.step);
  }

  function draw(canvas, type, state, step) {
    canvases.add(canvas);
    canvas._last = { type: type, state: state, step: step };
    if (!canvas._cssW) { resize(canvas); if (!canvas._cssW) return; }
    const ctx = canvas.getContext('2d');
    const dpr = canvas._dpr || 1;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const W = canvas._cssW, H = canvas._cssH;
    const P = palette();
    ctx.fillStyle = P.bg;
    ctx.fillRect(0, 0, W, H);
    const hl = step ? step.highlight : EMPTY_HL;
    const aux = step ? step.aux : null;
    const layout = { type: type, nodes: [] };
    DRAWERS[type](ctx, W, H, state, hl, aux, P, layout);
    canvas._layout = layout;
  }

  function redrawAll() {
    canvases.forEach(function (c) {
      if (c._last) draw(c, c._last.type, c._last.state, c._last.step);
    });
  }

  function hitTest(canvas, clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const x = clientX - rect.left, y = clientY - rect.top;
    const nodes = (canvas._layout && canvas._layout.nodes) || [];
    for (let i = nodes.length - 1; i >= 0; i--) {
      const n = nodes[i];
      if ((x - n.x) * (x - n.x) + (y - n.y) * (y - n.y) <= n.r * n.r) return n.id;
    }
    return null;
  }

  global.Renderer = { draw: draw, resize: resize, redrawAll: redrawAll, hitTest: hitTest };
})(window);
