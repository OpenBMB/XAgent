import request from '/@/utils/mockRequest'

export const getDataApi = (params?: any) => request.post('/api/getData', params)
export const refreshDataApi = (params?: any) => {
	return request.post('/api/getNewData', params)
}
// request({url:'/api/getNewData',method:'get',params:params})
export const getModalData = (params?: any) => request.post('/api/getModalData', params)
export const getNewTaskData = (params?: any) => request.post('/api/getNewTaskData', params)
export const runRequest = (params?: any) => request.post('/api/runRequest', params)
