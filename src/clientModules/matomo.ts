import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

const MATOMO_URL = 'https://matomo.docksky.fr';
const MATOMO_SITE_ID = '2';

if (ExecutionEnvironment.canUseDOM) {
  const w = window as Window & { _paq?: unknown[][] };
  const _paq = (w._paq = w._paq || []);
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);

  (function loadMatomo() {
    const base = MATOMO_URL.endsWith('/') ? MATOMO_URL : `${MATOMO_URL}/`;
    _paq.push(['setTrackerUrl', `${base}matomo.php`]);
    _paq.push(['setSiteId', MATOMO_SITE_ID]);
    const doc = document;
    const script = doc.createElement('script');
    const first = doc.getElementsByTagName('script')[0];
    script.async = true;
    script.src = `${base}matomo.js`;
    first?.parentNode?.insertBefore(script, first);
  })();
}

export {};
