import scipy.io as sio
import numpy as np
import tifffile
import h5py

def mat_to_tiff(mat_path, tiff_path, variable_name=None):
    """
    将 .mat 格式的高光谱图像转换为 (Channel, Height, Width) 的 TIFF 格式
    
    参数:
        mat_path (str): 输入的 .mat 文件路径
        tiff_path (str): 输出的 .tiff 文件路径
        variable_name (str, optional): .mat 文件中存储图像数据的变量名。
                                       如果不指定，脚本会自动查找第一个非系统内置的变量。
    """
    
    # 1. 尝试读取 .mat 文件
    try:
        # scipy.io 适用于 MATLAB v7.2 及以下版本保存的 .mat 文件
        mat_data = sio.loadmat(mat_path)
        is_h5py = False
    except NotImplementedError:
        # 如果是 MATLAB v7.3 格式（基于 HDF5），则使用 h5py 读取
        mat_data = h5py.File(mat_path, 'r')
        is_h5py = True

    # 2. 提取图像矩阵
    if variable_name is None:
        # 自动过滤掉 '__header__' 等内置属性，提取真实变量名
        keys =[k for k in mat_data.keys() if not k.startswith('__') and not k.startswith('#')]
        if len(keys) == 0:
            raise ValueError("未在 .mat 文件中找到有效的数据变量！")
        variable_name = keys[0]
        print(f"[*] 自动匹配到数据变量名: '{variable_name}'")
        
    img_data = np.array(mat_data[variable_name])
    
    # 注意：如果使用 h5py 读取，MATLAB 默认保存顺序会被自动转置为 (C, W, H)，需要特殊处理
    if is_h5py:
        # 还原回常规的 (H, W, C) 以便统一处理
        img_data = np.transpose(img_data, (2, 1, 0))
        
    print(f"[*] 原始提取的数据维度: {img_data.shape} (通常为 Height, Width, Channel)")

    # 3. 转换维度为 (Channel, Height, Width)
    if img_data.ndim == 3:
        # 假设原始通常为 (H, W, C) -> 我们想要 (C, H, W)
        # 将第 2 个维度(C)移到最前，第 0(H) 和 1(W) 维度向后移
        img_data = np.transpose(img_data, (2, 0, 1))
        print(f"[*] 转换后的数据维度: {img_data.shape} (Channel, Height, Width)")
    else:
        print("[!] 警告：提取的数据不是 3 维张量，无法进行 (C, H, W) 转换。")

    # 4. 保存为 TIFF 格式
    # photometric='minisblack' 参数确保 tifffile 正确识别这是一种单通道多波段的数据
    tifffile.imwrite(
        tiff_path, 
        img_data, 
        photometric='minisblack',
        metadata={'axes': 'CYX'} # 显式声明轴的顺序：C (Channel), Y (Height), X (Width)
    )
    
    print(f"[+] 转换成功！文件已保存至: {tiff_path}")

# ================= 运行示例 =================
if __name__ == "__main__":
    # 替换为你的实际文件路径
    INPUT_MAT_FILE = "hyperspectral_image.mat"  
    OUTPUT_TIFF_FILE = "output_image.tiff"
    
    # 如果你知道在 matlab 里面变量的具体名称（例如 'indian_pines'），也可以这样调用:
    # mat_to_tiff(INPUT_MAT_FILE, OUTPUT_TIFF_FILE, variable_name='indian_pines')
    
    mat_to_tiff(INPUT_MAT_FILE, OUTPUT_TIFF_FILE)
