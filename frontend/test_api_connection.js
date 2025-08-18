const axios = require('axios');

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

async function testApiConnection() {
    console.log('🔍 Testing API Connection...');
    console.log(`API URL: ${API_BASE_URL}`);
    
    try {
        // Test basic connection
        const response = await axios.get(`${API_BASE_URL.replace('/api', '')}/`);
        console.log('✅ Backend server is reachable');
        console.log('Response:', response.data);
        
        // Test login endpoint
        const loginResponse = await axios.post(`${API_BASE_URL}/auth/login/`, {
            username: 'user',
            password: 'user123'
        });
        
        console.log('✅ Login endpoint is working');
        console.log('Login response status:', loginResponse.status);
        console.log('User:', loginResponse.data.user.username);
        
    } catch (error) {
        console.log('❌ API Connection failed');
        console.log('Error:', error.message);
        
        if (error.response) {
            console.log('Response status:', error.response.status);
            console.log('Response data:', error.response.data);
        }
    }
}

testApiConnection();
