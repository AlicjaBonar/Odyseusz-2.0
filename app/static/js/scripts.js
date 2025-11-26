const API_BASE = 'http://127.0.0.1:5000';

// Dodaj Travelera
document.getElementById('travelerForm').onsubmit = async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  const res = await fetch(`${API_BASE}/travelers`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  const json = await res.json();
  document.getElementById('travelerResult').textContent = JSON.stringify(json, null, 2);
  e.target.reset();
};

// Pobierz wszystkich Travelerów
document.getElementById('getTravelers').onclick = async () => {
  const res = await fetch(`${API_BASE}/travelers`);
  const json = await res.json();
  document.getElementById('travelerList').textContent = JSON.stringify(json, null, 2);
};

// Dodaj Kraj
document.getElementById('countryForm').onsubmit = async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  const res = await fetch(`${API_BASE}/countries`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  const json = await res.json();
  document.getElementById('countryResult').textContent = JSON.stringify(json, null, 2);
  e.target.reset();
};

// Dodaj Miasto
document.getElementById('cityForm').onsubmit = async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  const res = await fetch(`${API_BASE}/cities`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  const json = await res.json();
  document.getElementById('cityResult').textContent = JSON.stringify(json, null, 2);
  e.target.reset();
};

// Pobierz Kraj z Miastami
document.getElementById('getCountryBtn').onclick = async () => {
  const id = document.getElementById('getCountryId').value;
  const res = await fetch(`${API_BASE}/countries/${id}`);
  const json = await res.json();
  document.getElementById('countryWithCities').textContent = JSON.stringify(json, null, 2);
};

// Dodaj Trip
document.getElementById('tripForm').onsubmit = async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  const res = await fetch(`${API_BASE}/trips`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  const json = await res.json();
  document.getElementById('tripResult').textContent = JSON.stringify(json, null, 2);
  e.target.reset();
};

// Pobierz Tripy Podróżnika
document.getElementById('getTripsBtn').onclick = async () => {
  const pesel = document.getElementById('getTripsPesel').value;
  const res = await fetch(`${API_BASE}/travelers/${pesel}/trips`);
  const json = await res.json();
  document.getElementById('tripsList').textContent = JSON.stringify(json, null, 2);
};