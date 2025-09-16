(function () {
  // ----------------- Отображение прогноза -----------------
  function renderForecast(data) {
    const forecastList = Array.isArray(data?.forecast)
      ? data.forecast.slice(0, 5).map(item => `
          <li>
            ${item.local_time}: ${item.temp}°C, ${item.description}
            ${item.rain ? ` | Rain: ${item.rain} mm` : ''}
            ${item.wind_speed ? ` | Wind: ${item.wind_speed} m/s, ${item.wind_deg}°` : ''}
            ${item.popr ? ` | Precipitation: ${item.popr}%` : ''}
          </li>
        `).join('')
      : '';

    return `
      <div class="row">
        <!-- Current Weather -->
        <div class="col-md-6 mb-3">
          <div class="card">
            <div class="card-body">
              <h3>${ data.current.city } (${data.current.local_time})</h3>
              <p class="text-muted"> Country: ${ data.current.country } </p>
              <img src="https://openweathermap.org/img/wn/${data.current.icon}@2x.png" alt="Weather icon">
              <p><strong>Weather:</strong> ${data.current.description}</p>
              <p><strong>Temperature:</strong> ${data.current.temp}°C (feels like ${data.current.feels_like}°C)</p>
              ${data.current.rain ? `<p><strong>Rain:</strong> ${data.current.rain} mm for ${data.current.rain_time} h</p>` : ''}
              <p><strong>Pressure:</strong> ${data.current.pressure} hPa</p>
              <p><strong>Wind:</strong> ${data.current.wind} m/s</p>
              <p><strong>Wind direction:</strong> ${data.current.wind_deg}°</p>
              <p><strong>Humidity:</strong> ${data.current.humidity}%</p>
              <p><strong>Clouds:</strong> ${data.current.clouds}%</p>
              <p><strong>Visibility:</strong> ${data.current.visibility} m</p>
            </div>
          </div>
        </div>

        <!-- Forecast -->
        <div class="col-md-6 mb-3">
          <div class="card">
            <div class="card-body">
              <h4>Forecast:</h4>
              <ul>${forecastList}</ul>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  // ----------------- Инициализация карты -----------------
  function mapInit(containerId, lat = 60.1699, lon = 24.9384, zoom = 10) {
    if (typeof ol === 'undefined') {
      console.error('OpenLayers (ol) not found.');
      return null;
    }

    const target = (typeof containerId === 'string') ? containerId : (containerId && containerId.id) || 'map';

    const voyagerLayer = new ol.layer.Tile({
      source: new ol.source.XYZ({
        url: 'https://{a-d}.basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}{r}.png',
        attributions: '© OpenLayers © CARTO',
        maxZoom: 19
      })
    });

    const view = new ol.View({
      center: ol.proj.fromLonLat([lon, lat]),
      zoom: zoom
    });

    const map = new ol.Map({
      target: target,
      layers: [voyagerLayer],
      view: view
    });

    return map;
  }

  // ----------------- Click Pick & Change Location -----------------
  function attachClickPick(map, { result = '#preview', markerOptions = { draggable: false }, single = true, showChangeButton = false } = {}) {
    if (!map) return { detach() {}, getLastPicked() { return null; } };

    const resultEl = typeof result === 'string' ? document.querySelector(result) : result;

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

    function placeMarker(lat, lon, silent = false) {
      if (single && lastFeature) markerSource.removeFeature(lastFeature);

      const feature = new ol.Feature({ geometry: new ol.geom.Point(ol.proj.fromLonLat([lon, lat])) });
      markerSource.addFeature(feature);
      lastFeature = feature;
      lastPicked = { lat, lon, marker: feature };

      if (!silent && resultEl) {
        let html = `<div class="small text-muted">chosen point: ${lat.toFixed(6)}, ${lon.toFixed(6)}</div>`;
        if (showChangeButton) {
          html += `
            <form id="change-location-form" method="post">
              <input type="hidden" name="lat" value="${lat}">
              <input type="hidden" name="lon" value="${lon}">
              <button type="submit" class="btn btn-sm btn-primary mt-2">Change location</button>
            </form>
          `;
        }
        resultEl.innerHTML = html;

        if (showChangeButton) {
          const form = resultEl.querySelector('#change-location-form');
          form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const formData = new FormData(form);
            const res = await fetch('/users/update-location/', {
              method: 'POST',
              headers: { 'X-CSRFToken': csrfToken },
              body: formData
            });
            if (res.ok) window.location.reload();
            else alert('Failed to update location');
          });
        }
      }
      return lastPicked;
    }

    function clickHandler(evt) {
      const [lon, lat] = ol.proj.toLonLat(evt.coordinate);
      placeMarker(lat, lon);
    }

    map.on('singleclick', clickHandler);

    return { detach() { map.un('singleclick', clickHandler); try { map.removeLayer(markerLayer); } catch {} }, getLastPicked() { return lastPicked; }, placeMarker };
  }

  // ----------------- Forecast on click -----------------
  function attachClickForecast(map, { endpoint = '/weather/forecast/', result = '#result' } = {}) {
    if (!map) return;

    const resultEl = typeof result === 'string' ? document.querySelector(result) : result;

    async function clickHandler(evt) {
      const [lon, lat] = ol.proj.toLonLat(evt.coordinate);
      try {
        const res = await fetch(`${endpoint}?lat=${lat}&lon=${lon}`);
        if (!res.ok) throw new Error('Failed fetching weather');
        const data = await res.json();
        if (resultEl) resultEl.innerHTML = renderForecast(data);
      } catch (err) {
        console.error(err);
      }
    }

    map.on('singleclick', clickHandler);
  }

  // ----------------- Search City -----------------
  async function placeCityByName(cityName, map, picker) {
    if (!cityName) return;
    try {
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(cityName)}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error('Geocoding failed');
      const data = await res.json();
      if (!data || !data.length) return alert('City not found');
      const { lat, lon } = data[0];
      map.getView().animate({ center: ol.proj.fromLonLat([parseFloat(lon), parseFloat(lat)]), zoom: 10 });
      picker.placeMarker(parseFloat(lat), parseFloat(lon));

      // Симулируем клик по карте, чтобы рендерить прогноз
      const evt = { coordinate: ol.proj.fromLonLat([parseFloat(lon), parseFloat(lat)]) };
      map.dispatchEvent({ type: 'singleclick', coordinate: evt.coordinate });
    } catch (err) {
      console.error(err);
      alert('Error searching city');
    }
  }

  // ----------------- Привязка input -----------------
  document.addEventListener('DOMContentLoaded', function () {
    const cityInput = document.querySelector('#city-search');
    const btn = document.querySelector('#city-search-btn');
    if (!cityInput || !btn) return;

    const map = window.mapInstance;
    const picker = window.cityPicker;
    if (!map || !picker) return;

    async function findCity() {
      const cityName = cityInput.value.trim();
      if (!cityName) return;
      await placeCityByName(cityName, map, picker);
    }

    btn.addEventListener('click', findCity);
    cityInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); findCity(); } });
  });

  // ----------------- Экспорт -----------------
  window.mapInit = mapInit;
  window.attachClickPick = attachClickPick;
  window.attachClickForecast = attachClickForecast;
  window.renderForecast = renderForecast;
  window.placeCityByName = placeCityByName;
})();