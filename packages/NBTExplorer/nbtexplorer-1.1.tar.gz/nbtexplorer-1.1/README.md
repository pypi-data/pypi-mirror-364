# 使用
### 1.导入
```python
import NBTExplorer
```
### 2.使用
##### 1.创建
类初始化参数:
- path: str, 待解析文件路径, 如: "C:/Users/Administrator/Desktop/test.nbt",默认空窗口
- parent: tk.Tk(), 父窗口, 默认None, 即无父窗口(创建一个顶级窗口)
- wintitle: str, 窗口标题, 默认"PyNBTExplorer"
- app_name: str, 应用名称, 默认"PyNBTExplorer"(关于窗口等显示)
- icon: str, 窗口图标, 默认"./icon.png"
- about_text: str, 关于页内容, 不填默认
##### 2.示例
```python
import NBTExplorer
app = NBTExplorer.NBTExplorer(path="C:/Users/Administrator/Desktop/test.nbt", parent=None,wintitle="PyNBTExplorer", app_name="PyNBTExplorer", icon="./icon.png", about_text="PyNBTExplorer")
```