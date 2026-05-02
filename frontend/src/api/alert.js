import axios from 'axios'

/**
 * 预警提醒 API
 */
export const alertAPI = {
  /** 获取所有预警（按类型分组） */
  list: () => axios.get('/alerts'),

  /** 获取预警总数（用于 Header 徽标） */
  getCount: () => axios.get('/alerts/count'),
}
