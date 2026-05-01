import axios from 'axios'

// 供应商API
export const supplierAPI = {
  list: () => axios.get('/suppliers'),
  create: (data) => axios.post('/suppliers', data),
  update: (id, data) => axios.put(`/suppliers/${id}`, data),
  delete: (id) => axios.delete(`/suppliers/${id}`)
}

// 客户API
export const customerAPI = {
  list: () => axios.get('/customers'),
  create: (data) => axios.post('/customers', data),
  update: (id, data) => axios.put(`/customers/${id}`, data),
  delete: (id) => axios.delete(`/customers/${id}`)
}

// 商品API
export const goodsAPI = {
  list: () => axios.get('/goods'),
  create: (data) => axios.post('/goods', data),
  update: (id, data) => axios.put(`/goods/${id}`, data),
  delete: (id) => axios.delete(`/goods/${id}`)
}

// 车辆API
export const vehicleAPI = {
  list: (params) => axios.get('/vehicles', { params }),
  create: (data) => axios.post('/vehicles', data),
  update: (id, data) => axios.put(`/vehicles/${id}`, data),
  delete: (id) => axios.delete(`/vehicles/${id}`)
}

// 司机API
export const driverAPI = {
  list: (params) => axios.get('/drivers', { params }),
  create: (data) => axios.post('/drivers', data),
  update: (id, data) => axios.put(`/drivers/${id}`, data),
  delete: (id) => axios.delete(`/drivers/${id}`)
}

// 仓库API（含库区/货位）
export const warehouseAPI = {
  list: () => axios.get('/warehouses'),
  create: (data) => axios.post('/warehouses', data),
  update: (id, data) => axios.put(`/warehouses/${id}`, data),
  delete: (id) => axios.delete(`/warehouses/${id}`),
  getZones: (warehouseId) => axios.get(`/warehouses/${warehouseId}/zones`),
  createZone: (data) => axios.post('/zones', data),
  updateZone: (id, data) => axios.put(`/zones/${id}`, data),
  deleteZone: (id) => axios.delete(`/zones/${id}`),
  getLocations: (zoneId) => axios.get(`/zones/${zoneId}/locations`),
  createLocation: (data) => axios.post('/locations', data),
  updateLocation: (id, data) => axios.put(`/locations/${id}`, data),
  deleteLocation: (id) => axios.delete(`/locations/${id}`)
}
