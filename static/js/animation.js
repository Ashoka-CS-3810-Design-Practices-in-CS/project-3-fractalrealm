/* animation.js: playback over a precomputed stepLog (never re-runs an algorithm), plus the
 * two browser-side structures from Assignment 2: the Animation Frame Buffer (FIFO queue of
 * upcoming step indexes) and the Operation History Stack (undo + redo stacks).
 * Exposes window.Animation = { FrameBuffer, Player, History }.
 */
(function (global) {
  'use strict';

  // ------------------------------------------------------------ Frame Buffer (FIFO)
  function FrameBuffer(capacity) {
    this.capacity = capacity || 8;
    this.items = [];
  }
  FrameBuffer.prototype.enqueue = function (i) {
    if (this.items.length >= this.capacity) this.items.shift();   // drop the oldest if the renderer lags
    this.items.push(i);
  };
  FrameBuffer.prototype.dequeue = function () { return this.items.shift(); };
  FrameBuffer.prototype.isEmpty = function () { return this.items.length === 0; };
  FrameBuffer.prototype.clear = function () { this.items = []; };

  // ------------------------------------------------------------ Player
  /* total = length of the longest step list (compare mode plays two lists in lock-step). */
  function Player(callbacks) {
    this.onRender = callbacks.onRender;       // (index) => draw frame
    this.onChange = callbacks.onChange;       // () => refresh button states
    this.total = 0;
    this.index = 0;
    this.playing = false;
    this.speed = 4;
    this.timer = null;
    this.buffer = new FrameBuffer(8);
    this.rafId = null;
  }

  Player.prototype.interval = function () { return Math.round(1600 / this.speed); };

  Player.prototype.load = function (total, autoplay) {
    this._stopTimer();
    this.playing = false;
    this.total = total;
    this.index = 0;
    this._jumpRender(0);
    this.onChange();
    if (autoplay && total > 1) this.play();
  };

  Player.prototype.clear = function () {
    this._stopTimer();
    this.playing = false;
    this.total = 0;
    this.index = 0;
    this.buffer.clear();
    this.onChange();
  };

  Player.prototype.hasSteps = function () { return this.total > 0; };
  Player.prototype.atEnd = function () { return this.index >= this.total - 1; };
  Player.prototype.canPlay = function () { return this.hasSteps() && (this.playing || !this.atEnd()); };
  Player.prototype.canForward = function () { return this.hasSteps() && !this.atEnd(); };
  Player.prototype.canBack = function () { return this.hasSteps() && this.index > 0; };

  Player.prototype.play = function () {
    if (!this.canPlay() || this.playing) return;
    this.playing = true;
    this.onChange();
    this._schedule();
  };

  Player.prototype.pause = function () {
    this._stopTimer();
    this.playing = false;
    this.onChange();
  };

  Player.prototype.toggle = function () { if (this.playing) this.pause(); else this.play(); };

  Player.prototype.stepForward = function () {
    if (!this.canForward()) return;
    this._stopTimer();
    this.playing = false;
    this.index++;
    this._enqueueRender(this.index);
    this.onChange();
  };

  Player.prototype.stepBack = function () {
    if (!this.canBack()) return;
    this._stopTimer();
    this.playing = false;
    this._jumpRender(this.index - 1);
    this.onChange();
  };

  Player.prototype.restart = function () {
    if (!this.hasSteps()) return;
    this._stopTimer();
    this.playing = false;
    this._jumpRender(0);
    this.onChange();
  };

  Player.prototype.goTo = function (i) {
    if (!this.hasSteps()) return;
    this._stopTimer();
    this.playing = false;
    this._jumpRender(Math.max(0, Math.min(this.total - 1, i)));
    this.onChange();
  };

  Player.prototype.setSpeed = function (s) {
    this.speed = s;                          // only the timer interval changes
    if (this.playing) { this._stopTimer(); this._schedule(); }
  };

  // ---- internals
  Player.prototype._schedule = function () {
    const self = this;
    this.timer = setTimeout(function () {
      self.timer = null;
      if (!self.playing) return;
      if (self.index < self.total - 1) {
        self.index++;
        self._enqueueRender(self.index);
      }
      if (self.index >= self.total - 1) { self.playing = false; self.onChange(); return; }
      self.onChange();
      self._schedule();
    }, this.interval());
  };

  Player.prototype._stopTimer = function () {
    if (this.timer) { clearTimeout(this.timer); this.timer = null; }
  };

  Player.prototype._jumpRender = function (i) {
    this.buffer.clear();                     // a jump must not replay stale frames
    this.index = i;
    this._enqueueRender(i);
  };

  Player.prototype._enqueueRender = function (i) {
    this.buffer.enqueue(i);
    if (this.rafId === null) this._flush();
  };

  /* One buffered frame per animation frame, in order. */
  Player.prototype._flush = function () {
    const self = this;
    this.rafId = requestAnimationFrame(function () {
      self.rafId = null;
      if (!self.buffer.isEmpty()) self.onRender(self.buffer.dequeue());
      if (!self.buffer.isEmpty()) self._flush();
    });
  };

  // ------------------------------------------------------------ Operation History Stack
  function History() {
    this.undoStack = [];
    this.redoStack = [];
  }
  /* entry: { operation, params, before, after, steps } */
  History.prototype.push = function (entry) { this.undoStack.push(entry); this.redoStack = []; };
  History.prototype.canUndo = function () { return this.undoStack.length > 0; };
  History.prototype.canRedo = function () { return this.redoStack.length > 0; };
  History.prototype.undo = function () {
    if (!this.canUndo()) return null;
    const e = this.undoStack.pop();
    this.redoStack.push(e);
    return e;
  };
  History.prototype.redo = function () {
    if (!this.canRedo()) return null;
    const e = this.redoStack.pop();
    this.undoStack.push(e);
    return e;
  };
  History.prototype.clear = function () { this.undoStack = []; this.redoStack = []; };

  global.Animation = { FrameBuffer: FrameBuffer, Player: Player, History: History };
})(window);
