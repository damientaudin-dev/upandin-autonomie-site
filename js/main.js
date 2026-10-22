(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const root = document.documentElement;
  root.classList.add('js');
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---- Accessibilité : taille du texte et contraste ---- */
  const sizeBtns = $$('.a11y [data-size]');
  const cBtn = $('.a11y [data-contrast]');
  function applySize(n) {
    root.dataset.size = n;
    sizeBtns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.size === String(n))));
    store.set('fo-size', n);
  }
  function applyContrast(on) {
    if (on) root.dataset.contrast = '1'; else delete root.dataset.contrast;
    cBtn.setAttribute('aria-pressed', String(on));
    store.set('fo-contrast', on ? '1' : '0');
  }
  sizeBtns.forEach(b => b.addEventListener('click', () => {
    // sur mobile, le bouton A+ est masqué : A++ bascule entre normal et très grand
    const n = b.dataset.size;
    applySize(n === root.dataset.size && n !== '0' ? '0' : n);
  }));
  cBtn.addEventListener('click', () => applyContrast(root.dataset.contrast !== '1'));
  applySize(store.get('fo-size') || '0');
  applyContrast(store.get('fo-contrast') === '1');

  /* ---- Menu mobile ---- */
  const burger = $('.burger'), nav = $('#nav');
  const closeNav = () => { nav.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); burger.setAttribute('aria-label', 'Ouvrir le menu'); };
  burger.addEventListener('click', () => {
    const open = !nav.classList.contains('open');
    nav.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
  });
  $$('a', nav).forEach(a => a.addEventListener('click', closeNav));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeNav(); });

  /* ---- Onglets senior / aidant ---- */
  $$('[data-tabs]').forEach(box => {
    const tabs = $$('[role=tab]', box);
    const select = t => tabs.forEach(x => {
      const on = x === t;
      x.setAttribute('aria-selected', String(on));
      x.tabIndex = on ? 0 : -1;
      $('#' + x.getAttribute('aria-controls')).hidden = !on;
    });
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => select(t));
      t.addEventListener('keydown', e => {
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          const n = tabs[(i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length];
          select(n); n.focus();
        }
      });
    });
  });

  /* ---- Apparition au défilement + compteurs ---- */
  const fmt = (v, d) => v.toLocaleString('fr-FR', { minimumFractionDigits: d, maximumFractionDigits: d });
  function count(el) {
    const end = parseFloat(el.dataset.count), d = +(el.dataset.decimals || 0), suf = el.dataset.suffix || '';
    const t0 = performance.now(), dur = 1300;
    const step = t => {
      const p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(end * e, d) + suf;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if ('IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (!en.isIntersecting) return;
      en.target.classList.add('is-in');
      $$('[data-count]', en.target).forEach(count);
      if (en.target.matches('[data-count]')) count(en.target);
      io.unobserve(en.target);
    }), { threshold: .15, rootMargin: '0px 0px -40px 0px' });
    $$('.reveal').forEach(el => io.observe(el));
  } else {
    $$('.reveal').forEach(el => el.classList.add('is-in'));
  }

  /* ---- Simulateur crédit d'impôt ---- */
  const eur = v => v.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });
  const m = $('#sim-m'), n = $('#sim-n'), no = $('#sim-n-o');
  function sim() {
    const monthly = Math.max(0, parseFloat(m.value) || 0);
    const months = +n.value;
    const seniors = +($('input[name=sim-a]:checked') || { value: 0 }).value;
    no.textContent = months + (months > 1 ? ' mois' : ' mois');
    const cap = Math.min(12000 + 1500 * seniors, 15000);
    const dep = monthly * months;
    const ci = 0.5 * Math.min(dep, cap);
    const net = months ? (dep - ci) / months : 0;
    $('#r-dep').textContent = monthly ? eur(dep) : '—';
    $('#r-ci').textContent = monthly ? eur(ci) : '—';
    $('#r-net').textContent = monthly ? eur(net) : '—';
    $('#r-cap').textContent = monthly
      ? `Plafond de dépenses retenu : ${eur(cap)} par an.` + (dep > cap ? ' Votre dépense dépasse le plafond : le crédit est limité.' : '') + ' Estimation applicable dès l’obtention de l’agrément.'
      : 'Saisissez le montant mensuel indiqué sur votre devis.';
  }
  [m, n, ...$$('input[name=sim-a]')].forEach(el => el.addEventListener('input', sim));
  sim();

  /* ---- Formulaire de contact ---- */
  const form = $('#form'), msg = $('.form__msg', form);
  function mailtoFallback(d) {
    const body = `Nom : ${d.nom}\nTéléphone : ${d.tel}\nE-mail : ${d.email}\nVous êtes : ${d.profil}\nDemande : ${d.objet}\n\n${d.message}`;
    location.href = `mailto:damientaudin@icloud.com?cc=natachataudin7@icloud.com&subject=${encodeURIComponent('[Site] ' + d.objet + ' — ' + d.nom)}&body=${encodeURIComponent(body)}`;
    msg.className = 'form__msg ok';
    msg.textContent = 'Votre messagerie s’ouvre avec votre demande pré-remplie. Vous pouvez aussi nous appeler au 07 64 05 89 45.';
  }
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const d = Object.fromEntries(new FormData(form).entries());
    msg.className = 'form__msg';
    if (!d.nom.trim() || (!d.tel.trim() && !d.email.trim())) {
      msg.className = 'form__msg err';
      msg.textContent = 'Merci d’indiquer votre nom et un téléphone ou un e-mail.';
      (d.nom.trim() ? $('#f-tel') : $('#f-nom')).focus();
      return;
    }
    const btn = $('button[type=submit]', form);
    btn.disabled = true; btn.textContent = 'Envoi en cours…';
    try {
      const r = await fetch('/api/contact', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) });
      const j = await r.json().catch(() => ({}));
      if (r.ok && j.ok) {
        form.reset();
        msg.className = 'form__msg ok';
        msg.textContent = 'Merci, votre demande est bien envoyée. Nous vous recontactons très vite.';
      } else if (j.fallback || r.status === 404 || r.status === 405) {
        mailtoFallback(d);
      } else {
        msg.className = 'form__msg err';
        msg.textContent = j.error || 'L’envoi n’a pas abouti. Appelez-nous au 07 64 05 89 45.';
      }
    } catch (err) {
      mailtoFallback(d);
    } finally {
      btn.disabled = false; btn.textContent = 'Envoyer ma demande';
    }
  });

  $('#year').textContent = new Date().getFullYear();
})();
