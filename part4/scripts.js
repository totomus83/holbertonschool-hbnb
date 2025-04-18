document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');

  if (loginForm) {
      loginForm.addEventListener('submit', async (event) => {
          event.preventDefault();
          const email = document.getElementById('email').value;
          const password = document.getElementById('password').value;
          await loginUser(email, password);
      });
  }

  checkAuthentication();
  setupPriceFilter();
});

async function loginUser(email, password) {
  const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
    method: 'POST',
    mode: 'cors',  // ✅ Ensures CORS headers are respected
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
});

  if (response.ok) {
      const data = await response.json();
      document.cookie = `token=${data.access_token}; path=/`;
      console.log("Cookie after login", document.cookie); // debug log to verify cookie
      window.location.href = 'index.html';

  } else {
      alert('Login failed: ' + response.statusText);
  }
}

function checkAuthentication() {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');
  console.log('Token:', token);
  console.log('loginLink:', loginLink);

  if (window.location.pathname.includes('index.html')) {
      if (loginLink) {
          if (!token) {
              loginLink.style.display = 'block';
          } else {
              loginLink.style.display = 'none';
              fetchPlaces(token);
          }
      } else {
          console.error('login-link element not found!');
      }
  }
}

function getCookie(name) {
  const cookies = document.cookie.split('; ');
  for (let cookie of cookies) {
      const [cookieName, cookieValue] = cookie.split('=');
      if (cookieName === name) {
          return cookieValue;
      }
  }
  return null;
}

async function fetchPlaces(token) {
  try {
      const response = await fetch('http://127.0.0.1:5000/api/v1/places', {
          method: 'GET',
          headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
          },
          credentials: 'include',
      });

      if (response.ok) {
          const data = await response.json();
          console.log('Fetched places data:', data);
          displayPlaces(data);
      } else {
          console.error('Failed to fetch places:', response.statusText);
      }
  } catch (error) {
      console.error('Error fetching places:', error);
  }
}

// Function to display the places
function displayPlaces(places) {
  const placesContainer = document.getElementById('places-list');
  placesContainer.innerHTML = '';

  places.forEach(place => {
      const placeElement = document.createElement('div');
      placeElement.classList.add('place');
      placeElement.innerHTML = `
          <h3>${place.title}</h3>
          <p>Description: ${place.description}</p>
          <p class="place-price">Price: ${place.price}€</p>
          <p>Latitude: ${place.latitude}</p>
          <p>Longitude: ${place.longitude}</p>
      `;
  // Make the box clickable
  placeElement.style.cursor = 'pointer';
  placeElement.addEventListener('click', () => {
  window.location.href = `place.html?id=${place.id}`;
  });
    
      placesContainer.appendChild(placeElement);
  });
}

function setupPriceFilter() {
  const priceFilter = document.getElementById('price-filter');
  
  if (priceFilter) {
      priceFilter.addEventListener('change', (event) => {
          const selectedPrice = event.target.value;
          filterPlacesByPrice(selectedPrice);
      });
  } else {
      console.log('price-filter element not found!');
  }
}

function filterPlacesByPrice(selectedPrice) {
  const places = document.querySelectorAll('.place');
  
  places.forEach(placeElement => {
      const price = parseFloat(placeElement.querySelector('.place-price').textContent.replace('Price: ', '').replace('€', '').trim());
      
      if (selectedPrice === 'All' || price <= selectedPrice) {
          placeElement.style.display = 'block';
      } else {
          placeElement.style.display = 'none';
      }
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  if (window.location.pathname.includes('place.html')) {
    const params = new URLSearchParams(window.location.search);
    const placeId = params.get('id');

    if (placeId) {
      await fetchPlaceDetails(placeId);
    } else {
      document.getElementById('place-details').innerHTML = '<p>Invalid or missing place ID.</p>';
    }
  }
});

async function fetchPlaceDetails(placeId) {
  try {
    const token = getCookie('token'); // Optional: depends on API security
    const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      const data = await response.json();
      console.log('Fetched place details:', data);
      const place = data.place;
      renderPlaceDetails(place);
    } else {
      console.error('Response not OK:', response.statusText);
      document.getElementById('place-details').innerHTML = '<p>Place not found.</p>';
    }
  } catch (error) {
    console.error('Error fetching place details:', error);
    document.getElementById('place-details').innerHTML = '<p>Failed to load place details.</p>';
  }
}

function renderPlaceDetails(place) {
  const container = document.getElementById('place-details');
  container.innerHTML = `
    <h1>${place.title}</h1>
    <p><strong>Description:</strong> ${place.description}</p>
    <p><strong>Price:</strong> ${place.price}€</p>
    <p><strong>Latitude:</strong> ${place.latitude}</p>
    <p><strong>Longitude:</strong> ${place.longitude}</p>
  `;
}
