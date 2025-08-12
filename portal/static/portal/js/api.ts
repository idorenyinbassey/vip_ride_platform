// Axios wrapper with token refresh, caching, optimistic updates, and offline queue
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

type Tokens = { access: string; refresh: string };
let tokens: Tokens | null = null;

// Simple in-memory cache
const cache = new Map<string, any>();

// Offline queue for requests to retry later
const offlineQueue: Array<() => Promise<any>> = [];

function setTokens(t: Tokens) { tokens = t; }
function getAccess() { return tokens?.access || ''; }
function getRefresh() { return tokens?.refresh || ''; }

const api: AxiosInstance = axios.create({ baseURL: '/api/v1' });

// Request interceptor: attach Authorization header and log
api.interceptors.request.use((config: AxiosRequestConfig) => {
  const access = getAccess();
  if (access) {
    config.headers = config.headers || {};
    (config.headers as any)['Authorization'] = `Bearer ${access}`;
  }
  // simple rate-limit header hint (server should apply real rate limiting)
  (config.headers as any)['X-Client-Request-Ts'] = Date.now().toString();
  return config;
});

// Response interceptor: handle 401, retries, and logging
api.interceptors.response.use(
  (res: AxiosResponse) => res,
  async (error: AxiosError) => {
    const original = error.config as AxiosRequestConfig & { _retry?: boolean };

    // Network error: offline mode -> queue request
    if (error.message === 'Network Error' || !error.response) {
      if (original && !original._retry) {
        return new Promise((resolve, reject) => {
          offlineQueue.push(async () => {
            try { const r = await api(original); resolve(r); }
            catch (e) { reject(e); }
          });
        });
      }
    }

    // Unauthorized: try refresh token once
    if (error.response?.status === 401 && !original._retry && getRefresh()) {
      original._retry = true;
      try {
        const r = await axios.post('/api/v1/accounts/refresh/', {
          refresh: getRefresh(),
        });
        const newTokens = { access: r.data.access, refresh: r.data.refresh || getRefresh() };
        setTokens(newTokens);
        (original.headers as any)['Authorization'] = `Bearer ${newTokens.access}`;
        return api(original);
      } catch (e) {
        // fall through
      }
    }

    return Promise.reject(error);
  }
);

// Simple typed API helpers
export interface RideEstimate { tier: string; distance: number; estimate: number; }
export async function getPricingEstimate(tier: string, distance: number): Promise<RideEstimate> {
  const key = `pricing:${tier}:${distance}`;
  if (cache.has(key)) return cache.get(key);
  const res = await api.get(`/pricing/estimate`, { params: { tier, distance } });
  cache.set(key, res.data);
  return res.data;
}

// Optimistic update example: add payment method (fake payload)
export async function addPaymentMethod(payload: any) {
  // optimistic UI can be updated by caller first; here we just call API
  return api.post('/payments/methods/', payload);
}

// Background sync: attempt queued requests when back online
window.addEventListener('online', async () => {
  while (offlineQueue.length) {
    const job = offlineQueue.shift();
    if (job) { try { await job(); } catch { /* keep going */ } }
  }
});

export default api;
