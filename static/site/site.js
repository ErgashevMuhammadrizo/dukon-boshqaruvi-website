import { probeApk, formatBytes } from './download.js';
let ui = {};
try { ui = JSON.parse(document.querySelector('#ui-messages')?.textContent || '{}'); } catch {}
const header = document.querySelector('#site-header');
const menuButton = document.querySelector('#menu-toggle');
const nav = document.querySelector('#main-nav');
function setMenu(open) {
  nav?.classList.toggle('is-open', open);
  menuButton?.setAttribute('aria-expanded', String(open));
  menuButton?.setAttribute('aria-label', open ? ui.close : ui.open);
  const symbol = menuButton?.querySelector('use');
  symbol?.setAttribute('href', `/static/site/icons.svg#${open ? 'close' : 'menu'}`);
}
menuButton?.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') {
    setMenu(false); menuButton.focus();
  }
});
const compactHeader = () => header?.classList.toggle('is-scrolled', window.scrollY > 16);
window.addEventListener('scroll', compactHeader, { passive: true });
compactHeader();
document.querySelectorAll('[data-year]').forEach(element => { element.textContent = String(new Date().getFullYear()); });
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if ('IntersectionObserver' in window && !reduceMotion) {
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) if (entry.isIntersecting) {
      entry.target.classList.add('is-visible'); observer.unobserve(entry.target);
    }
  }, { threshold: 0.06 });
  document.querySelectorAll('.reveal').forEach(element => observer.observe(element));
  document.documentElement.classList.add('js');
}
let config = {};
try { config = JSON.parse(document.querySelector('#site-config')?.textContent || '{}'); } catch { /* Valid HTML remains usable without optional config. */ }
const button = document.querySelector('#download-button');
const status = document.querySelector('#download-status');
let busy = false;
if (button && status) {
  button.addEventListener('click', async event => {
    event.preventDefault();
    if (busy) return;
    busy = true; button.setAttribute('aria-busy', 'true');
    status.className = 'download-status';
    status.textContent = ui.checking;
    try {
      const url = config.download_url || button.getAttribute('href');
      const result = await probeApk(url, globalThis.fetch, 12000, ui);
      if (!result.available) {
        status.classList.add('is-error'); status.textContent = result.message;
        return;
      }
      status.classList.add('is-success'); status.textContent = ui.starting;
      const metadata = document.querySelector('#download-metadata');
      const size = document.querySelector('#apk-size');
      const version = document.querySelector('#apk-version');
      if (result.size && size) { size.textContent = `${ui.size} ${formatBytes(result.size)}`; size.hidden = false; }
      if (config.apk_version && version) { version.textContent = `${ui.version} ${config.apk_version}`; version.hidden = false; }
      if (metadata) metadata.hidden = !(result.size || config.apk_version);
      const anchor = document.createElement('a');
      anchor.href = url; anchor.download = 'e-dukon.apk';
      document.body.append(anchor); anchor.click(); anchor.remove();
    } finally { busy = false; button.removeAttribute('aria-busy'); }
  });
}
