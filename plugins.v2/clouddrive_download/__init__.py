import json
import requests
from moviepy.common import logger
from moviepy.core.event import EventType, eventmanager
from moviepy.core.plugin import Plugin
from moviepy.core.config import settings

class CloudDriveDownload(Plugin):
    plugin_name = "CloudDrive下载器"
    plugin_version = "1.0.0"
    plugin_desc = "通过CloudDrive API将磁链发送到115网盘离线下载"
    plugin_icon = "https://raw.githubusercontent.com/jxxghp/MoviePilot-Plugins/main/icons/download.png"
    
    def __init__(self):
        super().__init__()
        self.cloudrive_api_url = settings.get("clouddrive_api_url", "http://localhost:19798")
        self.cloudrive_token = settings.get("clouddrive_token", "")
        
    def init_config(self):
        return [
            {
                "key": "clouddrive_api_url",
                "name": "CloudDrive API地址",
                "type": "text",
                "value": "http://localhost:19798",
                "desc": "CloudDrive的API地址，默认http://localhost:19798"
            },
            {
                "key": "clouddrive_token",
                "name": "CloudDrive API令牌",
                "type": "password",
                "value": "",
                "desc": "CloudDrive的API访问令牌"
            },
            {
                "key": "clouddrive_115_mount_id",
                "name": "115网盘挂载ID",
                "type": "text",
                "value": "",
                "desc": "115网盘在CloudDrive中的挂载ID"
            }
        ]
    
    def register(self):
        eventmanager.register(EventType.DownloadAdded, self.on_download_added)
    
    def on_download_added(self, event_data):
        """处理下载添加事件，将磁链发送到115网盘离线下载"""
        try:
            # 获取下载链接
            download_url = event_data.get("url", "")
            if not download_url:
                logger.warning("没有获取到下载链接")
                return
            
            # 检查是否为磁链
            if not download_url.startswith("magnet:"):
                logger.info(f"不是磁链，跳过处理: {download_url}")
                return
            
            # 获取115网盘挂载ID
            mount_id = settings.get("clouddrive_115_mount_id", "")
            if not mount_id:
                logger.error("未配置115网盘挂载ID")
                return
            
            # 调用CloudDrive API添加离线下载任务
            self.add_offline_task(mount_id, download_url)
            
        except Exception as e:
            logger.error(f"处理下载添加事件失败: {str(e)}")
    
    def add_offline_task(self, mount_id, url):
        """调用CloudDrive API添加离线下载任务"""
        try:
            # 构建API请求
            api_endpoint = f"{self.cloudrive_api_url}/api/v1/task/add"
            headers = {
                "Content-Type": "application/json"
            }
            if self.cloudrive_token:
                headers["Authorization"] = f"Bearer {self.cloudrive_token}"
            
            payload = {
                "mountId": mount_id,
                "url": url,
                "type": "magnet"
            }
            
            # 发送请求
            response = requests.post(api_endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                logger.info(f"成功添加离线下载任务: {url}")
            else:
                logger.error(f"添加离线下载任务失败: {result.get('message', '未知错误')}")
                
        except requests.RequestException as e:
            logger.error(f"调用CloudDrive API失败: {str(e)}")
        except Exception as e:
            logger.error(f"添加离线下载任务失败: {str(e)}")

    def get_mounts(self):
        """获取CloudDrive中的挂载点列表"""
        try:
            api_endpoint = f"{self.cloudrive_api_url}/api/v1/mount/list"
            headers = {}
            if self.cloudrive_token:
                headers["Authorization"] = f"Bearer {self.cloudrive_token}"
            
            response = requests.get(api_endpoint, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                return result.get("data", [])
            else:
                logger.error(f"获取挂载点列表失败: {result.get('message', '未知错误')}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"调用CloudDrive API失败: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"获取挂载点列表失败: {str(e)}")
            return []

    def get_tasks(self):
        """获取离线下载任务列表"""
        try:
            api_endpoint = f"{self.cloudrive_api_url}/api/v1/task/list"
            headers = {}
            if self.cloudrive_token:
                headers["Authorization"] = f"Bearer {self.cloudrive_token}"
            
            response = requests.get(api_endpoint, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                return result.get("data", [])
            else:
                logger.error(f"获取任务列表失败: {result.get('message', '未知错误')}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"调用CloudDrive API失败: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"获取任务列表失败: {str(e)}")
            return []