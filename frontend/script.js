let allLatest = [];
let allSummary = [];
let pmChartInstance = null;
let weatherChartInstance = null;

async function loadData() {
  const res = await fetch('/api/disruptions');
  const data = await res.json();
  allLatest = data.latest;
  allSummary = data.summary;

  const select = document.getElementById('cityFilter');
  const currentVal = select.value;
  select.innerHTML = '<option value="ALL">All Metro Hubs (6)</option>';
  allLatest.forEach(row => {
    const opt = document.createElement('option');
    opt.value = row.city;
    opt.textContent = row.city;
    select.appendChild(opt);
  });
  select.value = currentVal || 'ALL';

  if (allLatest.length > 0) {
    document.getElementById('lastUpdated').textContent = `Last Sync (UTC): ${allLatest[0].recorded_at_utc}`;
  }
  renderDashboard();
}

function renderDashboard() {
  const selectedCity = document.getElementById('cityFilter').value;
  const rows = selectedCity === 'ALL'
    ? allLatest
    : allLatest.filter(r => r.city === selectedCity);

  // KPIs
  const highHubs = rows.filter(r => r.disruption_risk === 'High Surge Risk');
  const modHubs = rows.filter(r => r.disruption_risk === 'Moderate Delay Risk');
  const avgPm = rows.length
    ? (rows.reduce((acc, r) => acc + Number(r.pm2_5), 0) / rows.length).toFixed(1)
    : 0;
  const totalReadings = allSummary.reduce((acc, r) => acc + Number(r.total_readings), 0);

  document.getElementById('kpiHigh').textContent = `(${highHubs.length})`;
  document.getElementById('kpiMod').textContent = `(${modHubs.length})`;
  document.getElementById('kpiPm25').textContent = avgPm;
  document.getElementById('kpiReadings').textContent = `(${totalReadings})`;

  // Alert Banner
  const banner = document.getElementById('alertBanner');
  if (highHubs.length > 0) {
    banner.textContent = `⚠️ ${highHubs.map(h => h.city).join(' & ')}: High Surge Risk Detected`;
  } else if (modHubs.length > 0) {
    banner.textContent = `⚡ ${modHubs.map(h => h.city).join(' & ')}: Moderate Delay Risk Active`;
  } else {
    banner.textContent = `✅ All Monitored Metro Hubs Operating Normally`;
  }

  // Table
  const tbody = document.getElementById('fleetTableBody');
  tbody.innerHTML = '';
  rows.forEach(r => {
    let badgeClass = 'badge-norm';
    if (r.disruption_risk === 'High Surge Risk') badgeClass = 'badge-high';
    else if (r.disruption_risk === 'Moderate Delay Risk') badgeClass = 'badge-mod';

    tbody.innerHTML += `
      <tr>
        <td><strong>${r.city}</strong></td>
        <td><span class="badge ${badgeClass}">${r.disruption_risk.toUpperCase()}</span></td>
        <td>${r.temp_c}°C</td>
        <td>${r.rain_mm}</td>
        <td>${r.wind_gusts_kmh}</td>
        <td><strong>${r.pm2_5}</strong></td>
      </tr>
    `;
  });

  // Charts
  const labels = rows.map(r => r.city);
  const pmValues = rows.map(r => r.pm2_5);
  const windValues = rows.map(r => r.wind_gusts_kmh);

  if (pmChartInstance) pmChartInstance.destroy();
  pmChartInstance = new Chart(document.getElementById('pmChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'PM2.5 (µg/m³)',
        data: pmValues,
        backgroundColor: '#c81e1e',
        borderRadius: 5
      }]
    },
    options: { plugins: { legend: { display: false } } }
  });

  if (weatherChartInstance) weatherChartInstance.destroy();
  weatherChartInstance = new Chart(document.getElementById('weatherChart'), {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Wind Gusts (km/h)',
        data: windValues,
        borderColor: '#9b1c1c',
        backgroundColor: 'rgba(200, 30, 30, 0.12)',
        fill: true,
        tension: 0.35
      }]
    },
    options: { plugins: { legend: { display: false } } }
  });
}

loadData();
setInterval(loadData, 60000);