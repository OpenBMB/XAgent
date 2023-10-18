import request from '/@/utils/mockRequest'

export const getDataApi = (params?: any) => request.post('/getData', params)
export const refreshDataApi = (params?: any) => {
	return request.post('/getNewData', params)
}
// request({url:'/getNewData',method:'get',params:params})
export const getModalData = (params?: any) => request.post('/getModalData', params)
export const getNewTaskData = (params?: any) => request.post('/getNewTaskData', params)
export const runRequest = (params?: any) => request.post('/runRequest', params)
