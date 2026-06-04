document.addEventListener('DOMContentLoaded', () => {
  const theme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-bs-theme', theme);

  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.setAttribute('aria-pressed', theme === 'dark');
    themeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-bs-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.classList.add('theme-transition');
      document.documentElement.setAttribute('data-bs-theme', next);
      localStorage.setItem('theme', next);
      themeToggle.setAttribute('aria-pressed', next === 'dark');
      const rmTransition = () => {
        document.documentElement.classList.remove('theme-transition');
        document.documentElement.removeEventListener('transitionend', rmTransition);
      };
      document.documentElement.addEventListener('transitionend', rmTransition, { once: true });
    });
  }

  document.querySelectorAll('.flip-card').forEach(card => {
    card.addEventListener('click', () => {
      card.classList.toggle('flipped');
    });

    let startX = 0, startY = 0;
    card.addEventListener('touchstart', e => {
      startX = e.changedTouches[0].screenX;
      startY = e.changedTouches[0].screenY;
    }, { passive: true });
    card.addEventListener('touchend', e => {
      const dx = e.changedTouches[0].screenX - startX;
      const dy = e.changedTouches[0].screenY - startY;
      if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 40) {
        card.classList.toggle('flipped');
      }
    }, { passive: true });
  });

  document.querySelectorAll('.tts-btn').forEach(btn => {
    const text = btn.dataset.text;
    const audioEl = btn.querySelector('audio') || (() => {
      const a = new Audio();
      a.classList.add('tts-player');
      btn.appendChild(a);
      return a;
    })();

    const onEnded = () => {
      btn.innerHTML = '🔊';
      btn.classList.remove('playing');
    };

    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      if (audioEl.dataset.loading) return;

      if (audioEl.src) {
        audioEl.currentTime = 0;
        const p = audioEl.play();
        btn.innerHTML = '▶️';
        btn.classList.add('playing');
        if (p) p.catch(() => onEnded());
        audioEl.addEventListener('ended', onEnded, { once: true });
        return;
      }

      audioEl.dataset.loading = '1';
      const orig = btn.innerHTML;
      btn.innerHTML = '<span class="tts-spinner"><span></span><span></span><span></span></span>';

      try {
        if (btn.dataset.audioUrl) {
          audioEl.src = btn.dataset.audioUrl;
          delete audioEl.dataset.loading;
          const p = audioEl.play();
          if (p) p.catch(() => onEnded());
          btn.innerHTML = '▶️';
          btn.classList.add('playing');
          audioEl.addEventListener('ended', onEnded, { once: true });
        } else {
          const res = await fetch(`/hangul/tts/?text=${encodeURIComponent(text)}`);
          const data = await res.json();
          if (data.url) {
            audioEl.src = data.url;
            delete audioEl.dataset.loading;
            const p = audioEl.play();
            if (p) p.catch(() => onEnded());
            btn.innerHTML = '▶️';
            btn.classList.add('playing');
            audioEl.addEventListener('ended', onEnded, { once: true });
          }
        }
      } catch (err) {
        console.error('TTS error:', err);
        btn.innerHTML = orig;
        delete audioEl.dataset.loading;
      }
    });
  });

  document.querySelectorAll('.quiz-option input[type="radio"]').forEach(input => {
    input.addEventListener('change', () => {
      const name = input.name;
      document.querySelectorAll(`input[name="${name}"]`).forEach(r => {
        r.closest('.quiz-option').classList.remove('selected');
      });
      if (input.checked) {
        input.closest('.quiz-option').classList.add('selected');
      }
    });
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.glass-card, .flip-card, .section-title').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

  document.querySelectorAll('.hangul-cell').forEach((cell, i) => {
    cell.style.opacity = '0';
    cell.style.transform = 'scale(0.8)';
    cell.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    setTimeout(() => {
      cell.style.opacity = '1';
      cell.style.transform = 'scale(1)';
    }, 50 + i * 30);
  });

  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  if (tooltips.length && typeof bootstrap !== 'undefined') {
    tooltips.forEach(t => new bootstrap.Tooltip(t));
  }

  document.querySelectorAll('.alert.achievement-unlock').forEach(el => {
    if (typeof confetti === 'function') {
      confetti({ particleCount: 120, spread: 80, origin: { y: 0.6 }, colors: ['#6C5CE7', '#00b894', '#fdcb6e', '#e17055'] });
      setTimeout(() => confetti({ particleCount: 60, spread: 100, origin: { y: 0.4 } }), 300);
    }
    const iconMatch = el.textContent.match(/[^\w\s]/);
    if (iconMatch) {
      const badge = document.createElement('span');
      badge.className = 'badge fs-3 ms-2 animate-badge';
      badge.textContent = iconMatch[0];
      el.querySelector('.btn-close')?.before(badge);
    }
  });

  const backBtn = document.getElementById('back-to-top');
  if (backBtn) {
    window.addEventListener('scroll', () => {
      backBtn.style.display = window.scrollY > 500 ? 'block' : 'none';
    }, { passive: true });
    backBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  let deferredPrompt;
  const installBanner = document.getElementById('pwa-install-banner');
  window.addEventListener('beforeinstallprompt', e => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBanner) installBanner.style.display = 'flex';
  });
  if (installBanner) {
    installBanner.querySelector('.pwa-install-btn')?.addEventListener('click', async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      const result = await deferredPrompt.userChoice;
      if (result.outcome === 'accepted') installBanner.style.display = 'none';
      deferredPrompt = null;
    });
    installBanner.querySelector('.pwa-dismiss-btn')?.addEventListener('click', () => {
      installBanner.style.display = 'none';
    });
  }

  const offlineToast = document.getElementById('offline-toast') || (() => {
    const t = document.createElement('div');
    t.id = 'offline-toast';
    t.className = 'offline-toast';
    t.textContent = '🌐 Нет соединения с интернетом';
    document.body.appendChild(t);
    return t;
  })();

  const updateOnlineStatus = () => {
    offlineToast.classList.toggle('visible', !navigator.onLine);
  };
  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  updateOnlineStatus();

  document.addEventListener('submit', async (e) => {
    const form = e.target;
    if (!form.classList.contains('ajax-form') && !form.querySelector('[data-ajax-form]')) return;
    e.preventDefault();
      const submitBtn = form.querySelector('[type="submit"]') || form.querySelector('button');
      const origHtml = submitBtn ? submitBtn.innerHTML : '';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '⏳';
      }
      try {
        const formData = new FormData(form);
        const res = await fetch(form.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: formData,
          credentials: 'same-origin'
        });
        const data = await res.json();
        if (data.success) {
          if (submitBtn) {
            submitBtn.innerHTML = '✅';
            submitBtn.classList.add('animate-badge');
            setTimeout(() => {
              submitBtn.innerHTML = origHtml;
              submitBtn.classList.remove('animate-badge');
              submitBtn.disabled = false;
            }, 1500);
          }
        } else {
          throw new Error('Unsuccessful status');
        }
      } catch (err) {
        console.error('AJAX error:', err);
        if (submitBtn) {
          submitBtn.innerHTML = '❌';
          setTimeout(() => {
            submitBtn.innerHTML = origHtml;
            submitBtn.disabled = false;
          }, 1500);
        }
      }
  });

  const navbar = document.querySelector('.glass-nav');
  if (navbar) {
    const handleScroll = () => {
      if (window.scrollY > 30) {
        navbar.classList.add('navbar-shrunk');
      } else {
        navbar.classList.remove('navbar-shrunk');
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
  }
});

