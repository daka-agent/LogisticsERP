import axios from 'axios'

// 财务概览
export const financeAPI = {
  getOverview: () => axios.get('/finance/overview'),

  // 应付账款
  getPayableList: (params) => axios.get('/finance/payable', { params }),
  createPayable: (data) => axios.post('/finance/payable', data),
  getPayableDetail: (id) => axios.get(`/finance/payable/${id}`),
  recordPayment: (id, data) => axios.post(`/finance/payable/${id}/pay`, data),
  getPayablePayments: (id) => axios.get(`/finance/payable/${id}/payments`),

  // 应收账款
  getReceivableList: (params) => axios.get('/finance/receivable', { params }),
  createReceivable: (data) => axios.post('/finance/receivable', data),
  getReceivableDetail: (id) => axios.get(`/finance/receivable/${id}`),
  recordReceipt: (id, data) => axios.post(`/finance/receivable/${id}/receive`, data),
  getReceivablePayments: (id) => axios.get(`/finance/receivable/${id}/payments`)
}
