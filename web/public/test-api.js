// Test script to check API connectivity
console.log('Testing API connection...');

fetch('http://localhost:5000/api/symbols')
    .then(res => {
        console.log('API Response Status:', res.status);
        return res.json();
    })
    .then(data => {
        console.log('Symbols received:', data.length);
        console.log('First 5 symbols:', data.slice(0, 5));
    })
    .catch(err => {
        console.error('API Error:', err);
    });

// Test specific symbol
fetch('http://localhost:5000/api/symbol/THYAO')
    .then(res => res.json())
    .then(data => {
        console.log('THYAO data:', data);
        console.log('Data points:', data.data?.length);
    })
    .catch(err => {
        console.error('Symbol API Error:', err);
    });
