import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: 'http://localhost:5000',
    timeout: 120000 // 120 seconds timeout
});

export default axiosInstance;
