// api.js - Axios wrapper with token refresh, caching, optimistic updates, and offline queue
// Requires axios to be loaded globally (via <script src="https://unpkg.com/axios/dist/axios.min.js"></script>)
(function(){
  const cache = new Map();
  const offlineQueue = [];
  let tokens = null;

  function setTokens(t){ tokens = t; }
  function getAccess(){ return tokens && tokens.access || ''; }
  function getRefresh(){ return tokens && tokens.refresh || ''; }

  const api = axios.create({ baseURL: '/api/v1' });

  api.interceptors.request.use(function(config){
    const access = getAccess();
    if (access){
      config.headers = config.headers || {};
      config.headers['Authorization'] = 'Bearer ' + access;
    }
    config.headers = config.headers || {};
    config.headers['X-Client-Request-Ts'] = Date.now().toString();
    return config;
  });

  api.interceptors.response.use(
    function(res){ return res; },
    async function(error){
      const original = error.config || {};

      // Network/offline -> queue
      if (error.message === 'Network Error' || !error.response){
        if (!original._retry){
          return new Promise(function(resolve, reject){
            offlineQueue.push(async function(){
              try { const r = await api(original); resolve(r); }
              catch(e){ reject(e); }
            });
          });
        }
      }

      // 401 -> refresh once
      if (error.response && error.response.status === 401 && !original._retry && getRefresh()){
        original._retry = true;
        try {
          const r = await axios.post('/api/v1/accounts/refresh/', { refresh: getRefresh() });
          const newTokens = { access: r.data.access, refresh: r.data.refresh || getRefresh() };
          setTokens(newTokens);
          original.headers = original.headers || {};
          original.headers['Authorization'] = 'Bearer ' + newTokens.access;
          return api(original);
        } catch (e){ /* fall through */ }
      }
      return Promise.reject(error);
    }
  );

  async function getPricingEstimate(tier, distance){
    const key = 'pricing:' + tier + ':' + distance;
    if (cache.has(key)) return cache.get(key);
    // Server supports JSON via Accept header or ?format=json on marketing view
    const res = await axios.get('/pricing/', {
      params: { tier: tier, distance: distance, format: 'json' },
      headers: { Accept: 'application/json' }
    });
    cache.set(key, res.data);
    return res.data;
  }

  window.API = {
    api: api,
    setTokens: setTokens,
    getPricingEstimate: getPricingEstimate,
  };

  window.addEventListener('online', async function(){
    while (offlineQueue.length){
      const job = offlineQueue.shift();
      if (job){ try { await job(); } catch(e){} }
    }
  });
})();
