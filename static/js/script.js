
let currentTheme = 'light';

function toggleTheme() {
  const body = document.body;
  const icon = document.getElementById('themeIcon');
  if (currentTheme === 'light') {
    body.classList.add('dark-mode');
    icon.innerHTML = '&#9790;'; // Moon icon
    currentTheme = 'dark';
  } else {
    body.classList.remove('dark-mode');
    icon.innerHTML = '&#9728;'; // Sun icon
    currentTheme = 'light';
  }
}

function analyzeSentiment() {
  const fileInput = document.getElementById('fileInput');
  const keyword = document.getElementById('keywordInput').value.toLowerCase();
  const errorMessage = document.getElementById('errorMessage');
  const loader = document.getElementById('loader');

  errorMessage.textContent = '';

  if (!fileInput.files.length) {
    errorMessage.textContent = 'Please upload a CSV file.';
    return;
  }

  loader.style.display = 'block';

  Papa.parse(fileInput.files[0], {
    header: true,
    skipEmptyLines: true,
    complete: function (results) {
      const data = results.data;
      const reviews = data.map(row => row.review || row.Review || '').filter(r => r);
      const filteredReviews = keyword ? reviews.filter(r => r.toLowerCase().includes(keyword)) : reviews;

      if (filteredReviews.length === 0) {
        loader.style.display = 'none';
        errorMessage.textContent = 'No reviews found with the given keyword.';
        return;
      }

      let positive = 0, negative = 0, neutral = 0;

      filteredReviews.forEach(review => {
        const lower = review.toLowerCase();
        if (lower.includes('good') || lower.includes('great') || lower.includes('excellent')) {
          positive++;
        } else if (lower.includes('bad') || lower.includes('poor') || lower.includes('terrible')) {
          negative++;
        } else {
          neutral++;
        }
      });

      loader.style.display = 'none';
      renderChart(positive, negative, neutral);
    },
    error: function (err) {
      loader.style.display = 'none';
      errorMessage.textContent = 'Error parsing CSV file.';
    }
  });
}

let chart;
function renderChart(positive, negative, neutral) {
  const ctx = document.getElementById('sentimentChart').getContext('2d');

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Positive', 'Negative', 'Neutral'],
      datasets: [{
        label: 'Sentiment Count',
        data: [positive, negative, neutral],
        backgroundColor: ['#4CAF50', '#f44336', '#FFC107']
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}