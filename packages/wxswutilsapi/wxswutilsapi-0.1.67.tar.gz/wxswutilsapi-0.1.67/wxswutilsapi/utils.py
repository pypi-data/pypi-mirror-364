import ast
import base64
import json
import re
import zlib
import os
import numpy as np

def predict_to_chartdata(data):
    try:
        labels = []
        xs = []
        ys = {}

        # 解析数据
        for entry in data:
            if entry['used'] == '1':
                predict_data = entry['predict']
                if isinstance(predict_data, str):
                    predict_list =  ast.literal_eval(predict_data)
                else:
                    predict_list = predict_data 
                xs.append(entry['time'])  # 记录时间戳
                for predict in predict_list:
                    component = predict['component']
                    value = predict['value']

                    # 添加到labels
                    if component not in labels:
                        labels.append(component)
                        ys[component] = []

                    # 按组件存储数值
                    ys[component].append(value)

        # 构建ys为嵌套数组
        ys_list = [ys[label] for label in labels]

        # 生成最终的结构
        result = {
            'labels': labels,
            'xs': xs,
            'ys': ys_list
        }

        return result
    except Exception as e:
        raise ValueError(f"Unexpected error in predict_to_chartdata:{str(e)}") from e
        
def predict_average(data,resultIsObject = False):
    try:
        # 初始化用于存储每个物质的值
        values = {}

        # 解析数据
        for entry in data:
            if entry['used'] == '1':
                predict_data = entry['predict']
                # 检查 predict_data 是否为字符串，如果是则转换
                if isinstance(predict_data, str):
                    predict_list = ast.literal_eval(predict_data)
                else:
                    predict_list = predict_data 
                for predict in predict_list:
                    component = predict['component']
                    value = predict['value']

                    # 如果物质还没有出现在values中，初始化为空列表
                    if component not in values:
                        values[component] = []

                    # 将该物质的值添加到列表中
                    values[component].append(value)

        average_result = None
        # 计算去掉两个最大和两个最小值后的平均值
        if resultIsObject is False:
            average_result = []
        else:
            average_result = {}

        for component, component_values in values.items():
            # 对该物质的值进行排序
            sorted_values = sorted(component_values)

            # 确保有足够的值去掉两个最大和两个最小
            if len(sorted_values) > 4:
                trimmed_values = sorted_values[2:-2]  # 去掉两个最大和两个最小
            else:
                trimmed_values = sorted_values  # 如果值不足 4 个，不做裁剪

            # 计算平均值
            avg_value = np.mean(trimmed_values)
            if resultIsObject is False:
                average_result.append({'component': component, 'value': avg_value})
            else:
                average_result[component] = avg_value

        return average_result
    except Exception as e:
        raise ValueError(f"Unexpected error in predict_average:{str(e)}") from e
    
def is_number(value):
    try:
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            # 使用正则表达式检查是否为数字
            return bool(re.match(r'^-?\d+(\.\d+)?$', value))
        return False
    except Exception as e:
        raise ValueError(f"Unexpected error in is_number:{str(e)}") from e
    
def spectrum_sum(data, group_size):
    try:
        grouped_data = []  # 用来存放分组后的数据
        group = []  # 当前正在处理的分组
        ids = []  # 用来记录当前分组的 id
        merged_spectrum = []  # 用来合并当前分组的 Spectrum_Array
    
        for item in data:
            if len(group) < group_size:
                # 添加当前项到当前分组
                group.append(item)
                ids.append(item['id'])
                spectrum_array = eval(item['Spectrum_Array'])  # 将字符串转为列表
                
                # 合并当前 Spectrum_Array
                if not merged_spectrum:
                    merged_spectrum = spectrum_array
                else:
                    merged_spectrum = [x + y for x, y in zip(merged_spectrum, spectrum_array)]
            
            # 当分组满了时，保存分组结果，并重置用于下一组的变量
            if len(group) == group_size:
                grouped_data.append({
                    'Spectrum_Array': merged_spectrum,
                    'time': group[0]['time'],  # 假设同一组的时间相同
                    'ids': ids,
                    'filter_time': group[0]['filter_time'],
                    'plate_id':group[0]['plate_id'] if "plate_id" in group[0] else ""
                })
                # 清空当前分组，用于处理下一个分组
                group = []
                ids = []
                merged_spectrum = []
    
        # 处理最后剩余的不足 group_size 的数据，如果有就删除
        if group:
            # 如果最后一组的长度不足 group_size，则删除它
            if len(group) < group_size:
                return grouped_data  # 直接返回，最后一组将被忽略
    
        return grouped_data
    except Exception as e:
        raise ValueError(f"Unexpected error in spectrum_sum:{str(e)}") from e
    
def spectrum_sum_mydb(data, group_size,time):
    try:
        grouped_data = []  # 用来存放分组后的数据
        group = []  # 当前正在处理的分组
        ids = []  # 用来记录当前分组的 id
        merged_spectrum = []  # 用来合并当前分组的 Spectrum_Array
    
        for item in data:
            if len(group) < group_size:
                # 添加当前项到当前分组
                group.append({k: v for k, v in item.items() if k != 'Spectrum_Array'})
                ids.append(item['id'])
                spectrum_array = item['Spectrum_Array']  # 将字符串转为列表
                # 💡 这里修复
                if isinstance(spectrum_array, str):
                    spectrum_array = json.loads(spectrum_array)
                if spectrum_array and not isinstance(spectrum_array[0], (int, float)):
                    spectrum_array = [float(x) for x in spectrum_array]
                # 合并当前 Spectrum_Array
                if not merged_spectrum:
                    merged_spectrum = spectrum_array
                else:
                    merged_spectrum = [x + y for x, y in zip(merged_spectrum, spectrum_array)]
            
            # 当分组满了时，保存分组结果，并重置用于下一组的变量
            if len(group) == group_size:
                grouped_data.append({
                    'Spectrum_Array': merged_spectrum,
                    'time': group[0]['time'],  # 假设同一组的时间相同
                    'ids': ids,
                    'filter_time': time,
                    'plate_id':group[0]['plate_id'] if "plate_id" in group[0] else ""
                })
                # 清空当前分组，用于处理下一个分组
                group = []
                ids = []
                merged_spectrum = []
    
        # 处理最后剩余的不足 group_size 的数据，如果有就删除
        if group:
            # 如果最后一组的长度不足 group_size，则删除它
            if len(group) < group_size:
                return grouped_data  # 直接返回，最后一组将被忽略
    
        return grouped_data
    except Exception as e:
        raise ValueError(f"Unexpected error in spectrum_sum:{str(e)}") from e
    
def spectrum_and_sum(data, group_size):
    try:
        """
        按指定组长度分组并计算 Spectrum_Array 的和。
    
        :param data: List[Dict], 原始数据列表。
        :param group_size: int, 每组的长度。
        :return: List[Dict], 分组计算后的结果列表。
        """
        if group_size <= 0:
            raise ValueError("group_and_sum: group_size 必须是正整数")

        result = []

        # 按组长度分组并计算
        for i in range(0, len(data) - group_size + 1, group_size):
            group = data[i:i + group_size]
            # 按 Spectrum_Array 累加
            combined_spectrum = [
                sum(values) for values in zip(
                    *(ast.literal_eval(item["Spectrum_Array"]) for item in group)
                )
            ]
            result.append({
                "Spectrum_Array": combined_spectrum,
                "time": group[0]["time"],
                "ids": [item["id"] for item in group]
            })

        return result
    except Exception as e:
        raise ValueError(f"Unexpected error in spectrum_and_sum:{str(e)}") from e
    
def send_zip(data):
    try:
        return base64.b64encode(
                    zlib.compress(json.dumps(data).encode('utf-8'))).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Unexpected error in send_zip:{str(e)}") from e

def send_unzip(data):
    try:
        # 尝试解码base64数据
        decoded_data = base64.b64decode(data)
    except base64.binascii.Error as e:
        raise ValueError(f"Base64 decoding failed: {str(e)}") from e
    
    try:
        # 尝试解压缩数据
        decompressed_data = zlib.decompress(decoded_data)
    except zlib.error as e:
        raise ValueError(f"Zlib decompression failed: {str(e)}") from e
    
    try:
        # 尝试将解压缩后的数据解析为JSON
        return json.loads(decompressed_data.decode('utf-8'))
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decoding failed: {str(e)}") from e
    except UnicodeDecodeError as e:
        raise ValueError(f"UTF-8 decoding failed: {str(e)}") from e
    
def create_unique_filename(folder_path, base_name, suffix):
    try:
        file_name = f"{base_name}{suffix}"
        file_path = os.path.join(folder_path, file_name)
        counter = 1

        while os.path.exists(file_path):
            file_name = f"{base_name}({counter}){suffix}"
            file_path = os.path.join(folder_path, file_name)
            counter += 1

        return file_name
    except Exception as e:
        raise ValueError(f"Error creating unique filename: {str(e)}") from e

def ensure_directory_existence(file_path):
    try:
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as e:
        raise ValueError(f"Error ensuring directory existence: {str(e)}") from e
    
def writeFile(filePath, fileName, data, suffix='.wxsw'):
    try:
        fileName = create_unique_filename(filePath, fileName, suffix)
        ensure_directory_existence(os.path.join(filePath, fileName))
        data_json = json.dumps(data, ensure_ascii=False)
        
        with open(os.path.join(filePath, fileName), 'w', encoding='utf-8') as file:
            file.write(data_json)
        return fileName
    except json.JSONEncodeError as e:
        raise ValueError(f"JSON encoding failed: {str(e)}") from e
    except IOError as e:
        raise ValueError(f"File writing failed: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"Unexpected error in writeFile: {str(e)}") from e