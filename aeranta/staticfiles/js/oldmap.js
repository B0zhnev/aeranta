// map_click.js (OpenLayers + Stadia Maps с fallback на OSM)
(function () {
  // ----------------- Отображение прогноза (без изменений) -----------------
  function renderForecast(data) {
    const forecastList = Array.isArray(data?.forecast)
      ? data.forecast.slice(0, 5).map(item => `<li>${item.local_time}: ${item.temp}°C, ${item.description}</li>`).join('')
      : '';

    return `
      <div class="card mt-3" style="max-width: 500px;">
        <div class="card-body">
          <h3>${data.current.city} (${data.current.local_time})</h3>
          <img src="https://openweathermap.org/img/wn/${data.current.icon}@2x.png" alt="Weather icon">
          <p><strong>Weather:</strong> ${data.current.description}</p>
          <p><strong>Temperature:</strong> ${data.current.temp}°C (feels like ${data.current.feels_like}°C)</p>
          ${data.current.rain ? `<p><strong>Rain:</strong> ${data.current.rain} mm for ${data.current.rain_time} h</p>` : ''}
          <p><strong>Pressure:</strong> ${data.current.pressure} mm</p>
          <p><strong>Wind:</strong> ${data.current.wind} m/s</p>
          <p><strong>Wind direction:</strong> ${data.current.wind_deg}°</p>
          <p><strong>Humidity:</strong> ${data.current.humidity}%</p>
          <p><strong>Clouds:</strong> ${data.current.clouds}</p>
          <p><strong>Visibility:</strong> ${data.current.visibility}</p>
        </div>
      </div>
      <div class="card mt-3" style="max-width: 500px;">
        <div class="card-body">
          <h4>Forecast:</h4>
          <ul>${forecastList}</ul>
        </div>
      </div>
    `;
  }

  // ----------------- Инициализация карты (OL) с использованием Stadia Maps -----------------
  function mapInit(containerId, lat = 60.1699, lon = 24.9384, zoom = 10) {
    if (typeof ol === 'undefined') {
      console.error('OpenLayers (ol) not found. Make sure <script src="https://cdn.jsdelivr.net/npm/ol/ol.js"></script> is loaded before map_click.js');
      return null;
    }

    const target = (typeof containerId === 'string') ? containerId : (containerId && containerId.id) || 'map';
    const isRetina = (window.devicePixelRatio || 1) > 1;

    // API key для Stadia Maps
    const apiKey = 'ceb1568e-58f2-4265-91e0-15a67f8f250c';
    const stadiaUrl = isRetina
      ? `https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}@2x.png?api_key=${apiKey}`
      : `https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}.png?api_key=${apiKey}`;

    // Fallback OSM (покажем сразу — чтобы не было пустой страницы)
    const osmLayer = new ol.layer.Tile({
      source: new ol.source.OSM(),
      visible: true
    });

    // Stadia layer
    const stadiaLayer = new ol.layer.Tile({
      source: new ol.source.XYZ({
        url: stadiaUrl,
        attributions: '© Stadia Maps, © OpenMapTiles, © OpenStreetMap contributors'
      }),
      visible: false
    });

    const view = new ol.View({
      center: ol.proj.fromLonLat([lon, lat]), // [lon, lat]
      zoom: zoom
    });

    const map = new ol.Map({
      target: target,
      layers: [osmLayer], // сначала OSM
      view: view
    });

    // Проверяем доступность Stadia (через загрузку одного тайла)
    try {
      const sampleUrl = stadiaUrl.replace('{z}', '0').replace('{x}', '0').replace('{y}', '0');
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = function () {
        try {
          // добавляем слой Stadia поверх OSM и скрываем OSM
          map.addLayer(stadiaLayer);
          stadiaLayer.setVisible(true);
          osmLayer.setVisible(false);
          console.info('Stadia Maps tiles loaded and applied.');
        } catch (e) {
          console.warn('Stadia loaded but failed to apply layer:', e);
        }
      };
      img.onerror = function () {
        console.warn('Stadia Maps tile load failed — using OSM fallback.');
      };
      img.src = sampleUrl;
    } catch (err) {
      console.warn('Stadia check failed, using OSM fallback.', err);
    }

    return map;
  }

  // ----------------- Клик для прогноза (OL) -----------------
  function attachClickForecast(map, { endpoint, result = '#result', render = renderForecast } = {}) {
    if (!map || !endpoint) return () => {};

    const resultEl = typeof result === 'string' ? document.querySelector(result) : result;

    async function clickHandler(evt) {
      const [lon, lat] = ol.proj.toLonLat(evt.coordinate);

      try {
        if (resultEl) resultEl.innerHTML = '<div class="text-muted small">Загружаю прогноз…</div>';
        const res = await fetch(`${endpoint}?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`, {
          headers: { 'Accept': 'application/json' }
        });
        if (!res.ok) throw new Error(`request failed: ${res.status}`);
        const data = await res.json();
        if (resultEl) resultEl.innerHTML = render(data);
      } catch (err) {
        console.error(err);
        if (resultEl) resultEl.innerHTML = '<div class="text-danger">Не удалось получить прогноз.</div>';
      }
    }

    map.on('singleclick', clickHandler);

    return function detach() {
      map.un('singleclick', clickHandler);
    };
  }

  // ----------------- Клик для выбора точки (OL) -----------------
  function attachClickPick(map, { result = '#preview', markerOptions = { draggable: false }, single = true } = {}) {
    if (!map) return { detach() {}, getLastPicked() { return null; } };

    const resultEl = typeof result === 'string' ? document.querySelector(result) : result;

    // Слой для маркеров + видимый стиль
    const markerSource = new ol.source.Vector();
    const markerStyle = new ol.style.Style({
      image: new ol.style.Circle({
        radius: 7,
        fill: new ol.style.Fill({ color: 'rgba(220,20,60,0.9)' }),
        stroke: new ol.style.Stroke({ color: '#fff', width: 2 })
      })
    });
    const markerLayer = new ol.layer.Vector({ source: markerSource, style: markerStyle });
    map.addLayer(markerLayer);

    let lastFeature = null;
    let lastPicked = null;

    function placeMarker(lat, lon) {
      if (single && lastFeature) {
        markerSource.removeFeature(lastFeature);
        lastFeature = null;
      }

      const feature = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.fromLonLat([lon, lat]))
      });

      markerSource.addFeature(feature);
      lastFeature = feature;
      lastPicked = { lat, lon, marker: feature };

      if (resultEl) resultEl.innerHTML = `<div class="small text-muted">Выбранная точка: ${lat.toFixed(6)}, ${lon.toFixed(6)}</div>`;
      return lastPicked;
    }

    function clickHandler(evt) {
      const [lon, lat] = ol.proj.toLonLat(evt.coordinate);
      placeMarker(lat, lon);
    }

    map.on('singleclick', clickHandler);

    return {
      detach() {
        map.un('singleclick', clickHandler);
        try { map.removeLayer(markerLayer); } catch (e) { /* ignore */ }
      },
      getLastPicked() { return lastPicked; },
      placeMarker
    };
  }

  // ----------------- Экспорт -----------------
  window.mapInit = mapInit;
  window.attachClickForecast = attachClickForecast;
  window.attachClickPick = attachClickPick;
  window.renderForecast = renderForecast;
})();