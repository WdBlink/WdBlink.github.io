self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const legacy = ['precache-v1', 'runtime', 'main-precache-v1', 'main-runtime'];
    const keys = await caches.keys();
    await Promise.all(keys.filter(key => key.startsWith('main-') || legacy.includes(key)).map(key => caches.delete(key)));
    await self.clients.claim();
    await self.registration.unregister();
  })());
});
