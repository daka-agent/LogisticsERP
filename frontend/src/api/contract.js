import axios from 'axios'

/**
 * 采购合同 API
 */
export const purchaseContractAPI = {
  getList: (params) => axios.get('/api/contracts/purchase', { params }),
  getEligibleOrders: () => axios.get('/api/contracts/purchase/eligible'),
  create: (data) => axios.post('/api/contracts/purchase', data),
  getDetail: (id) => axios.get(`/api/contracts/purchase/${id}`),
  approve: (id, data) => axios.put(`/api/contracts/purchase/${id}/approve`, data),
  reject: (id, data) => axios.put(`/api/contracts/purchase/${id}/reject`, data),
  terminate: (id) => axios.put(`/api/contracts/purchase/${id}/terminate`)
}

/**
 * 运输合同 API
 */
export const transportContractAPI = {
  getList: (params) => axios.get('/api/contracts/transport', { params }),
  getEligibleOrders: () => axios.get('/api/contracts/transport/eligible'),
  create: (data) => axios.post('/api/contracts/transport', data),
  getDetail: (id) => axios.get(`/api/contracts/transport/${id}`),
  approve: (id, data) => axios.put(`/api/contracts/transport/${id}/approve`, data),
  reject: (id, data) => axios.put(`/api/contracts/transport/${id}/reject`, data),
  terminate: (id) => axios.put(`/api/contracts/transport/${id}/terminate`)
}

/**
 * 合同概览统计 API
 */
export const contractOverviewAPI = {
  getOverview: () => axios.get('/api/contracts/overview')
}
