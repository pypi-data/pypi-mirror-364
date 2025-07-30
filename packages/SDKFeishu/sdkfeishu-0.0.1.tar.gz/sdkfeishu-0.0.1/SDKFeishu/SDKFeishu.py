from typing import Tuple
import requests, json
from requests_toolbelt import MultipartEncoder

def get_access_token(app_id: str=None, app_secret: str=None) -> str:
    """获取飞书应用的访问令牌，有效期 25~30 分钟
    
    :param app_id: 应用 ID
    :param app_secret: 应用 Secret
    :return: 访问令牌"""
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',}
    data = {
    "app_id": app_id,
    "app_secret": app_secret}
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        access_token = response.json().get('tenant_access_token')
        return access_token
    else:
        return f"{response.status_code}, {response.text}"
    
class Bitable(object):
    """飞书的多维表格类
    
    :param access_token: 飞书应用的访问令牌
    :type access_token: str
    :param app_token: 飞书应用的 app_token
    :type app_token: str
    """
    def __init__(self, access_token: str, app_token: str):
        self.access_token = access_token
        self.app_token = app_token
        
    def _update_params(self, params: dict, **kwargs):
        params.update({k: v for k, v in kwargs.items() if v})
        
    def get_wiki_space_list(self, page_size=20, page_token=None) -> list:
        """获取知识空间列表
        
        :param page_size: 分页大小，最大 50
        :type page_size: int
        :param page_token: 分页标记，第一次请求不填，表示从头开始遍历；分页查询结果还有更多项时会同时返回新的 page_token，下次遍历可采用该 page_token 获取查询结果
        :type page_token: str
        :return: 知识空间列表"""
        url = 'https://open.feishu.cn/open-apis/wiki/v2/spaces'
        access_token = self.access_token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=utf-8',}
        
        params = {'page_size': page_size}
        if page_token:
            params['page_token'] = page_token
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('data').get('items')
        else:
            return f"{response.status_code}, {response.text}"
    
    def get_wiki_child_space_list(self, space_id, page_size=10, page_token=None, parent_page_token=None) -> list:
        """获取知识空间子节点列表
        
        :param space_id: 知识空间 ID
        :type space_id: str
        :param page_size: 分页大小，最大 50
        :type page_size: int
        :param page_token: 分页标记，第一次请求不填，表示从头开始遍历；分页查询结果还有更多项时会同时返回新的 page_token，下次遍历可采用该 page_token 获取查询结果
        :type page_token: str
        :param parent_page_token: 父节点分页标记
        :type parent_page_token: str
        :return: 知识空间子节点列表"""
        url = f'https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes'
        
        access_token = self.access_token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=utf-8'}
        params = {'page_size': page_size}
        self._update_params(params, page_token=page_token, parent_page_token=parent_page_token)
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('data').get('items')
        else:
            return f"{response.status_code}, {response.text}"
        
    def get_wiki_space_info(self, token) -> dict:
        """获取知识空间节点信息
        
        :param token: 知识空间库 token
        :type token: str
        :return: 知识空间节点信息"""
        url = f'https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node'
        access_token = self.access_token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=utf-8'}
        data = {'token': token, 'obj_type': 'wiki'}
        
        response = requests.post(url, headers=headers, params=data)
        if response.status_code == 200:
            return response.json().get('data').get('node')
        else:
            return f"{response.status_code}, {response.text}"
        
    def find_table_record(self, table_id, page_size=10, view_id=None, field_names=None, automatic_fields=False) -> Tuple[list|str]:
        """查询表格记录
        
        :param table_id: 表格 ID
        :type table_id: str
        :param page_size: 分页大小，最大 500
        :type page_size: int
        :param view_id: 视图的唯一标识
        :type view_id: str
        :param field_names: 需要返回的字段名列表（缺省值为全部返回）
        :type field_names: list
        :param automatic_fields: 是否自动计算并返回创建时间（created_time）、修改时间（last_modified_time）、创建人（created_by）、修改人（last_modified_by）这四类字段。默认不返回。
        :type automatic_fields: bool
        :return: 表格记录列表"""
        
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/search'
        access_token = self.access_token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=utf-8'}
        params = {"page_size": page_size}
        self._update_params(params, view_id=view_id, field_names=field_names, automatic_fields=automatic_fields)
        
        response = requests.post(url, headers=headers, json=params)
        if response.status_code == 200:
            return response.json().get('data').get('items', [])
        else:
            return f"{response.status_code}, {response.text}"
        
    def create_table_record(self, table_id, fields) -> Tuple[dict|str]:
        """创建表格记录
        
        :param table_id: 表格 ID
        :type table_id: str
        :param fields: 要添加的表格字段数据
        :type fields: dict (格式: {'列名': '新值'})
        :return: 创建状态"""
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records'
        access_token = self.access_token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=utf-8'}
        data = {"fields": fields}
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return f"{response.status_code}, {response.text}"
        
    def update_table_record(self, table_id, record_id, fields) -> dict:
        """更新表格记录
        
        :param table_id: 表格 ID
        :type table_id: str
        :param record_id: 表格记录 ID
        :type record_id: str
        :param fields: 要更新的表格字段数据
        :type fields: dict (格式: {'列名': '新值'})
        :return: 更新状态"""
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}'
        access_token = self.access_token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=utf-8'}
        params = {"fields": fields}
        
        response = requests.put(url, headers=headers, json=params)
        if response.status_code == 200:
            return response.json()
        else:
            return f"{response.status_code}, {response.text}"
        
    def delete_table_record(self, table_id, record_id) -> dict:
        """删除表格记录
        
        :param table_id: 表格 ID
        :type table_id: str
        :param record_id: 表格记录 ID
        :type record_id: str
        :return: 删除状态"""
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}'
        access_token = self.access_token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=utf-8'}
        
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return f"{response.status_code}, {response.text}"
        
    def upload_media(self, file, file_name, file_size, parent_node, parent_type="bitable_file") -> str:
        """上传媒体文件
        
        :param file: 媒体文件的二进制内容
        :type file: bytes
        :param file_name: 媒体文件名
        :type file_name: str
        :param file_size: 媒体文件大小
        :type file_size: int
        :param parent_type: 媒体文件所属类型，如 doc_image
        :type parent_type: str
        :param parent_node: 媒体文件所属节点的 token
        :type parent_node: str
        :return: 媒体文件的 token"""
        url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
        form = {'file_name': file_name,
                'parent_type': parent_type,
                'parent_node': parent_node,
                'size': str(file_size),
                'file': file}  
        multi_form = MultipartEncoder(form)
        headers = {
            'Authorization': f'Bearer {self.access_token}',  ## 获取tenant_access_token, 需要替换为实际的token
        }
        headers['Content-Type'] = multi_form.content_type
        response = requests.request("POST", url, headers=headers, data=multi_form)
        if response.status_code == 200:
            return response.json().get('data', {}).get('file_token', "None")
        else:
            return f"{response.status_code}, {response.text}"
        
    def download_media_by_link(self, file_token) -> str:
        """下载媒体文件
        
        :param file_token: 媒体文件的 token
        :type file_token: str
        :return: 媒体文件内容的下载直链"""
        url = f"https://open.feishu.cn/open-apis/drive/v1/medias/batch_get_tmp_download_url"
        
        access_token = self.access_token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=utf-8'}
        data = {"file_tokens": [file_token]}
        
        response = requests.get(url, headers=headers, params=data)
        if response.status_code == 200: 
            return response.json().get('data', {}).get('tmp_download_urls', [])[0].get('tmp_download_url', "None")
        else:
            return f"{response.status_code}, {response.text}"
