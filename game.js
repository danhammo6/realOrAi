(function () {
  const ROUNDS_PER_GAME = 12;
  const STORAGE_KEY = 'realOrAi.seen.v1';

  function loadSeen() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return new Set(raw ? JSON.parse(raw) : []);
    } catch {
      return new Set();
    }
  }

  function saveSeen(set) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...set]));
    } catch {}
  }

  let seen = loadSeen();

  const startScreen = document.getElementById('start-screen');
  const gameScreen = document.getElementById('game-screen');
  const endScreen = document.getElementById('end-screen');

  const startBtn = document.getElementById('start-btn');
  const playAgainBtn = document.getElementById('play-again-btn');
  const chooseRealBtn = document.getElementById('choose-real');
  const chooseAiBtn = document.getElementById('choose-ai');
  const nextBtn = document.getElementById('next-btn');

  const gameImage = document.getElementById('game-image');
  const imageLoading = document.getElementById('image-loading');
  const roundNumEl = document.getElementById('round-num');
  const roundTotalEl = document.getElementById('round-total');
  const scoreEl = document.getElementById('score');
  const feedbackEl = document.getElementById('feedback');
  const feedbackText = document.getElementById('feedback-text');
  const feedbackCaption = document.getElementById('feedback-caption');
  const finalScoreEl = document.getElementById('final-score');
  const finalTotalEl = document.getElementById('final-total');
  const finalMessageEl = document.getElementById('final-message');

  let deck = [];
  let roundIndex = 0;
  let score = 0;

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function showScreen(screen) {
    [startScreen, gameScreen, endScreen].forEach(s => s.classList.add('hidden'));
    screen.classList.remove('hidden');
  }

  function pickUnseen(pool, want) {
    // Prefer unseen items; if pool exhausted, reset that pool's seen entries and refill.
    const unseen = pool.filter(i => !seen.has(i.src));
    if (unseen.length >= want) return shuffle(unseen).slice(0, want);

    // Exhausted: take what's left unseen, then top up from items we've seen before
    // (after clearing just this pool's seen entries so the cycle restarts cleanly).
    const leftover = shuffle(unseen);
    pool.forEach(i => seen.delete(i.src));
    const refill = shuffle(pool.filter(i => !leftover.includes(i))).slice(0, want - leftover.length);
    return leftover.concat(refill);
  }

  function startGame() {
    const aiPool = IMAGES.filter(i => i.isAI);
    const realPool = IMAGES.filter(i => !i.isAI);
    const half = Math.floor(ROUNDS_PER_GAME / 2);
    const aiCount = Math.min(half, aiPool.length);
    const realCount = Math.min(ROUNDS_PER_GAME - aiCount, realPool.length);
    deck = shuffle(pickUnseen(aiPool, aiCount).concat(pickUnseen(realPool, realCount)));
    roundIndex = 0;
    score = 0;
    scoreEl.textContent = '0';
    roundTotalEl.textContent = deck.length;
    finalTotalEl.textContent = deck.length;
    updateSeenBadge();
    showScreen(gameScreen);
    loadRound();
  }

  function updateSeenBadge() {
    const badge = document.getElementById('seen-count');
    if (badge) badge.textContent = `${seen.size} / ${IMAGES.length} images seen`;
  }

  function resetProgress() {
    seen = new Set();
    saveSeen(seen);
    updateSeenBadge();
  }

  function loadRound() {
    feedbackEl.classList.add('hidden');
    chooseRealBtn.classList.remove('correct', 'wrong');
    chooseAiBtn.classList.remove('correct', 'wrong');
    chooseRealBtn.disabled = false;
    chooseAiBtn.disabled = false;

    const item = deck[roundIndex];
    roundNumEl.textContent = roundIndex + 1;

    imageLoading.textContent = 'Loading...';
    imageLoading.style.display = 'flex';
    gameImage.style.visibility = 'hidden';
    gameImage.onload = () => {
      imageLoading.style.display = 'none';
      gameImage.style.visibility = 'visible';
    };
    gameImage.onerror = () => {
      imageLoading.textContent = 'Image failed to load — click a button to continue.';
    };
    gameImage.src = item.src;
    gameImage.alt = item.alt || 'Guess the image';
  }

  function handleChoice(guessIsAI) {
    const item = deck[roundIndex];
    const correct = guessIsAI === item.isAI;

    seen.add(item.src);
    saveSeen(seen);
    updateSeenBadge();

    chooseRealBtn.disabled = true;
    chooseAiBtn.disabled = true;

    const actualBtn = item.isAI ? chooseAiBtn : chooseRealBtn;
    const pickedBtn = guessIsAI ? chooseAiBtn : chooseRealBtn;

    if (correct) {
      pickedBtn.classList.add('correct');
      score++;
      scoreEl.textContent = score;
      feedbackText.textContent = 'Correct!';
      feedbackText.className = 'correct';
    } else {
      pickedBtn.classList.add('wrong');
      actualBtn.classList.add('correct');
      feedbackText.textContent = item.isAI ? 'Nope — it was AI.' : 'Nope — it was real.';
      feedbackText.className = 'wrong';
    }

    feedbackCaption.textContent = item.caption || '';
    feedbackEl.classList.remove('hidden');
  }

  function nextRound() {
    roundIndex++;
    if (roundIndex >= deck.length) {
      endGame();
    } else {
      loadRound();
    }
  }

  function endGame() {
    finalScoreEl.textContent = score;
    const pct = score / deck.length;
    let msg;
    if (pct === 1) msg = 'Perfect! You have a sharp eye.';
    else if (pct >= 0.8) msg = 'Great — you can tell the difference most of the time.';
    else if (pct >= 0.5) msg = 'Not bad. AI is getting tricky!';
    else msg = 'Tough round. The AI fooled you more than half the time.';
    finalMessageEl.textContent = msg;
    showScreen(endScreen);
  }

  startBtn.addEventListener('click', startGame);
  playAgainBtn.addEventListener('click', startGame);
  chooseRealBtn.addEventListener('click', () => handleChoice(false));
  chooseAiBtn.addEventListener('click', () => handleChoice(true));
  nextBtn.addEventListener('click', nextRound);

  const resetBtn = document.getElementById('reset-btn');
  if (resetBtn) {
    resetBtn.addEventListener('click', (e) => {
      e.preventDefault();
      if (confirm('Reset progress? You\'ll start seeing images you\'ve already answered.')) {
        resetProgress();
      }
    });
  }

  updateSeenBadge();
})();
