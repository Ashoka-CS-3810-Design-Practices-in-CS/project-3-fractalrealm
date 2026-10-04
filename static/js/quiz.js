/* quiz.js: interactive quiz. Questions come from a static JSON file
 * (static/data/quiz.json); the browser picks questions for the current topic,
 * keeps the score and shows a summary at the end.
 * Exposes window.Quiz = { start }.
 */
(function (global) {
  'use strict';

  const QUESTIONS_PER_QUIZ = 5;
  let allQuestions = null;
  let state = null;

  const dialog = document.getElementById('quiz-dialog');
  const title = document.getElementById('quiz-title');
  const body = document.getElementById('quiz-body');
  const nextBtn = document.getElementById('quiz-next');
  const closeBtn = document.getElementById('quiz-close');

  function el(tag, text, cls) {
    const e = document.createElement(tag);
    if (text !== undefined) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  }

  function shuffle(a) {
    const arr = a.slice();
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    }
    return arr;
  }

  function loadQuestions() {
    if (allQuestions) return Promise.resolve(allQuestions);
    return fetch('/static/data/quiz.json')
      .then(function (r) { if (!r.ok) throw new Error('Could not load the quiz questions'); return r.json(); })
      .then(function (data) { allQuestions = data; return data; });
  }

  function start(topic, topicLabel) {
    loadQuestions().then(function (all) {
      const pool = all.filter(function (q) { return q.topic === topic; });
      if (pool.length === 0) {
        title.textContent = 'Quiz';
        body.replaceChildren(el('p', 'There are no quiz questions for this topic yet.'));
        nextBtn.hidden = true;
      } else {
        state = { topic: topicLabel || topic, questions: shuffle(pool).slice(0, QUESTIONS_PER_QUIZ), index: 0, score: 0, answered: false };
        showQuestion();
      }
      if (!dialog.open) dialog.showModal();
    }).catch(function (err) {
      title.textContent = 'Quiz';
      body.replaceChildren(el('p', err.message));
      nextBtn.hidden = true;
      if (!dialog.open) dialog.showModal();
    });
  }

  function showQuestion() {
    const q = state.questions[state.index];
    state.answered = false;
    title.textContent = 'Quiz: ' + state.topic + ' (' + (state.index + 1) + ' / ' + state.questions.length + ')';
    const options = el('div', undefined, 'quiz-options');
    const feedback = el('div', '', 'quiz-feedback');
    q.options.forEach(function (text, i) {
      const b = el('button', text);
      b.type = 'button';
      b.addEventListener('click', function () { answer(i, options, feedback); });
      options.appendChild(b);
    });
    body.replaceChildren(el('p', q.prompt), options, feedback);
    nextBtn.hidden = true;
  }

  function answer(i, options, feedback) {
    if (state.answered) return;
    state.answered = true;
    const q = state.questions[state.index];
    const buttons = options.querySelectorAll('button');
    buttons.forEach(function (b, k) {
      b.disabled = true;
      if (k === q.correct) b.classList.add('correct');
      else if (k === i) b.classList.add('wrong');
    });
    if (i === q.correct) state.score++;
    feedback.textContent = (i === q.correct ? 'Correct. ' : 'Not quite. ') + (q.explanation || '');
    nextBtn.textContent = state.index + 1 < state.questions.length ? 'Next' : 'See results';
    nextBtn.hidden = false;
  }

  function showSummary() {
    title.textContent = 'Quiz results';
    const pct = Math.round((state.score / state.questions.length) * 100);
    body.replaceChildren(
      el('p', 'You scored ' + state.score + ' out of ' + state.questions.length + ' (' + pct + '%).'),
      el('p', pct >= 80 ? 'Great work!' : 'Try running the operations step by step again, then retake the quiz.')
    );
    nextBtn.hidden = true;
  }

  nextBtn.addEventListener('click', function () {
    if (!state) return;
    state.index++;
    if (state.index < state.questions.length) showQuestion(); else showSummary();
  });
  closeBtn.addEventListener('click', function () { dialog.close(); });

  global.Quiz = { start: start };
})(window);
