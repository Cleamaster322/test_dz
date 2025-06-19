import axios from 'axios';
import {baseURL} from './config.jsx';

class ApiClient{
    constructor(baseURL) {
        this.client = axios.create({
            baseURL: baseURL, withCredentials: true, headers: {
                'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest',
            },
        });

        this.setCsrfToken();
        this.setTokenAuth();
    }

    async setCsrfToken() {
    try {
        const response = await this.client.get('/lb/get_csrf_token/');
        if (response.data.csrfToken) {
            this.client.defaults.headers.common['X-CSRFToken'] = response.data.csrfToken;
        }
        } catch (error) {
            console.log('Ошибка получения CSRF токена', error);
        }
    }

        setTokenAuth() {
        const token = localStorage.getItem('accessToken');
        if (token) {
            this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }
    }

    async get(url, config = {}) {
        return this.client.get(url, config);
    }

    async post(url, data = {}, config = {}) {
        return this.client.post(url, data, config);
    }

    async put(url, data = {}, config = {}) {
        return this.client.put(url, data, config);
    }

    async patch(url, data = {}, config = {}) {
        return this.client.patch(url, data, config);
    }

    async delete(url, config = {}) {
        return this.client.delete(url, config);
    }
}

const api = new ApiClient(baseURL);
export default api;
