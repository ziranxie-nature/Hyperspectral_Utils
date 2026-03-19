import scipy.io as sio
import numpy as np
import tifffile

def tiff_to_mat(tiff_path, mat_path, variable_name='hsi_data'):
    """
    将 (Channel, Height, Width) 顺序的高光谱 TIFF 图像转换为 .mat 格式
    并自动将维度还原回 (Height, Width, Channel)
    
    参数:
        tiff_path (str): 输入的 .tiff 文件路径
        mat_path (str): 输出的 .mat 文件路径
        variable_name (str): 保存到 .mat 文件中时使用的变量名，默认为 'hsi_data'
    """
    
    # 1. 读取 TIFF 文件
    try:
        img_data = tifffile.imread(tiff_path)
        print(f"[*] 成功读取 TIFF 文件，当前数据维度: {img_data.shape} (预期为 Channel, Height, Width)")
    except Exception as e:
        raise RuntimeError(f"读取 TIFF 文件失败: {e}")

    # 2. 维度重排 (C, H, W) -> (H, W, C)
    if img_data.ndim == 3:
        # 原始维度索引为: 0:Channel, 1:Height, 2:Width
        # 我们希望新的顺序为: Height (1), Width (2), Channel (0)
        img_data = np.transpose(img_data, (1, 2, 0))
        print(f"[*] 转换后的数据维度: {img_data.shape} (Height, Width, Channel)")
    else:
        print(f"[!] 警告：读取的数据是 {img_data.ndim} 维，不是预期的 3 维，未进行 (H, W, C) 维度重排。")

    # 3. 构造字典并保存为 .mat 文件
    # .mat 文件实质上是保存字典对象，键是 MATLAB 里的变量名，值是对应的数据
    mat_dict = {
        variable_name: img_data
    }
    
    # do_compression=True 可以在保存高光谱这种大型三维矩阵时大幅减小文件体积
    sio.savemat(mat_path, mat_dict, do_compression=True)
    
    print(f"[+] 转换成功！文件已保存至: {mat_path}")
    print(f"[*] 在 MATLAB 中你可以通过 load('{mat_path}') 得到名为 '{variable_name}' 的变量。")

# ================= 运行示例 =================
if __name__ == "__main__":
    # 替换为你的实际文件路径
    INPUT_TIFF_FILE = "output_image.tiff"  
    OUTPUT_MAT_FILE = "restored_hyperspectral.mat"
    
    # 你可以自定义要在 mat 文件中生成的变量名称，比如 'indian_pines' 
    tiff_to_mat(INPUT_TIFF_FILE, OUTPUT_MAT_FILE, variable_name='my_hsi_data')
