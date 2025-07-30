import os
import time
import sys
import requests
import importlib
import inspect
import traceback
import json
from loguru import logger
from datetime import datetime
from getmac import get_mac_address

class Executor:
    """函数调用执行器，负责函数调用"""

    def __init__(self, url, function_folder = "./functions"):
        """
        初始化 Executor 对象

        参数:
            url (str): 服务器地址
            function_folder (str): 存放函数的文件夹路径

        返回:
            None
        """
        self.url = url
        self.function_folder = function_folder
        # 检查存放函数的文件夹是否存在，不存在则创建
        if not os.path.exists(self.function_folder):
            os.makedirs(self.function_folder)
        # 函数名称到函数对象的映射
        self.func_map = {}
        # 上一次调用结果
        self.last_call_entry = {}
        # 目前的 prompt
        self.func_prompt = self._register()
        # 本机 mac 地址
        self.mac_address = get_mac_address()

    # 添加文件到搜索路径
    def _add_pathself(self):
        FUNCTIONS_DIR = os.path.abspath(self.function_folder)
        if FUNCTIONS_DIR not in sys.path:
            sys.path.insert(0, FUNCTIONS_DIR)
    
    def _register(self):
        """注册函数
        参数:
            None
        返回:
            str: 包含函数信息的 prompt
        """
        # 获取函数参数的类型
        def get_annotation_name(ann):
            if ann is inspect.Parameter.empty:
                return "Any"
            elif hasattr(ann, '__name__'):  # 普通类型，如 int, str
                return ann.__name__
            elif hasattr(ann, '_name'):  # 泛型类型，如 List, Optional
                return ann._name or str(ann)
            else:
                return str(ann).replace('typing.', '')
        
        # 获取类的字段信息（从 __init__ 方法中提取）
        def get_class_info(cls):
            class_info = {}
            init = cls.__init__
            if init and inspect.isfunction(init):
                sig = inspect.signature(init)
                for param_name, param in list(sig.parameters.items())[1:]:  # 跳过 self
                    ann = get_annotation_name(str(param.annotation))
                    if param.default is inspect.Parameter.empty:
                        class_info[param_name] = ann
                    else:
                        class_info[param_name] = f"{ann} (optional)"
            return class_info

        
        logger.info("导入函数信息开始")
        function_infos = []
        class_infos = []

        # 遍历 functions 文件夹
        for filename in os.listdir("./functions"):
            if filename.endswith(".py") and not filename.startswith('__'):
                filepath = os.path.join("./functions", filename)
                module_name = os.path.splitext(filename)[0]

                try:
                    # 动态加载指定路径下的模块
                    spec = importlib.util.spec_from_file_location(module_name, filepath)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        # 遍历模块中的函数成员
                        for name, func in inspect.getmembers(module, inspect.isfunction):
                            # 确保这个函数来自这个模块，因为有可能是导入的
                            if func.__module__ == module_name:
                                self.func_map[name] = func  # 注册函数

                                # 提取函数说明
                                doc = func.__doc__.strip() if func.__doc__ else "无说明"
                                # 获取函数签名，参数信息
                                sig = inspect.signature(func)
                                
                                # 解析每个参数的类型和名称
                                param_strs = []
                                for param_name, param in sig.parameters.items():
                                    ann = str(param.annotation)
                                    param_strs.append(f"{param_name}: {get_annotation_name(ann)}")
                                param_display = ", ".join(param_strs)

                                function_infos.append(f"{doc}：{name}({param_display})")
                        for cls_name, cls_obj in inspect.getmembers(module, inspect.isclass):
                            if cls_obj.__module__ == module_name:
                                # 获取类的 docstring
                                cls_doc = cls_obj.__doc__.strip() if cls_obj.__doc__ else "无说明"

                                # 收集构造函数字段信息
                                fields = get_class_info(cls_obj)
                                field_display = ", ".join(f"{k}: {v}" for k, v in fields.items())

                                # 组合输出
                                class_infos.append(f"{cls_doc}：类 {cls_name}({field_display})")


                except Exception as e:
                    logger.error(f"导入模块 {module_name} 失败: {e}")

        prompt_lines = ["\n以下是你可调用的函数，你不能够调用不存在的函数：\n",'"如果没有合适的函数可以调用，请把请把 func_call 设为 []："\n']
        for i, line in enumerate(function_infos, 1):
            prompt_lines.append(f"{i}. {line}")

        prompt_lines.append("以下是类的信息，格式为类的描述+名称+参数列表，之后调用函数如果需要这些类作为函数的参数，就把它们按照字典格式展开写在json里面\n")
        for i, line in enumerate(class_infos, 1):
            prompt_lines.append(f"{i}. {line}")

        logger.info("导入函数信息成功")
        return "\n".join(prompt_lines)

    def execute_functions(self, llm_response):
        try:    
            list_of_function_calls = llm_response.get("func_call", [])
        except Exception as e:
            logger.error(f"json解析发生错误: {e}")
            return
        for single_func_call_dict in list_of_function_calls:
            try:    
                name = single_func_call_dict.get("name")
                args = single_func_call_dict.get("arguments", {})
            except Exception as e: 
                logger.error(f"json解析发生错误: {e}")
                return
                
            if name == 'None':
                logger.info("该请求不需要调用函数")
                return
                    
            try:    
                func = self.func_map[name]
            except Exception as e:
                logger.error(f"不存在这个函数")
                return
            
            # 记录函数调用信息
            start_time = time.time()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            e = None
            try:
                result = func(**args)
            except Exception as e:
                logger.error(f"函数调用出错: {e}")

            self.last_call_entry = {
                "name": name,
                "args": args,
                "timestamp": timestamp,
                "result": result,
                "duration": time.time() - start_time,
                "exception": None
            }