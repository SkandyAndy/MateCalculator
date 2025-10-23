const CACHE_NAME = 'mate-rechner-cache-v2.3'; // WICHTIG: Nummer erhöhen!
const urlsToCache = [
    './', // Bedeutet: "Dieser Ordner"
    './index.html', // (oder index.html)
    './manifest.json', // Sicher ist sicher, nimm das Manifest mit auf
    './icon-192.png',
    './icon-512.png'
];
    // Wenn du CSS/JS wieder auslagern würdest, kämen sie auch hier rein.

// Installation: Cache öffnen und die App-Shell-Dateien hinzufügen
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Cache geöffnet');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch: Anfragen abfangen und aus dem Cache bedienen
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Wenn im Cache gefunden, von dort zurückgeben
                if (response) {
                    return response;
                }
                // Sonst: Vom Netzwerk holen
                return fetch(event.request);
            })
    );
});