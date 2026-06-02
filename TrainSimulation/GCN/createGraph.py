import torch
from torch_geometric.data import Data
import pandas as pd
import numpy as np

def createGraph():

    N = 8  # 车站
    M = 16  # 列车
    i = 10 # 状态向量列车上标
    k = 2 # 状态向量车站下标
    # 指定 Excel 文件路径
    excel_file = 'error_free.xlsx'
    # 读取 Excel 文件到 DataFrame
    df = pd.read_excel(excel_file)
    # 获取 data_feature
    data_feature = []
    data_featureY = []
    for datanum in range(8):
        if datanum%2 == 0:
            data_featurenow=[]
            for n in range(M):
                if n<8:
                    i_now = (i+datanum-M+n)%M
                    if i_now == 0:
                        i_now = 16
                    if i_now < i+datanum-8:
                        k_now = k+N
                    else:
                        k_now = k
                    data_xnow = df.iloc[k_now-2,i_now-1]
                    # 提供矩阵少一行，并且序号是从0开始
                    data_featurenow.append(data_xnow)
                else:
                    i_now = (i+datanum-N+n-8)%M
                    if i_now == 0:
                        i_now = 16
                    k_now = (k-n+8+8)%N+abs((k-n+8+8)//N)*N
                    data_xnow = df.iloc[k_now-2,i_now-1]
                    data_featurenow.append(data_xnow)
            if data_feature == []:
                data_feature = data_featurenow.copy()
            else:
                data_feature = np.vstack((data_feature, data_featurenow))
        else:
            data_featurenow = []
            for n in range(M):
                if n < 8:
                    i_now = (i+datanum-M+n)%M
                    if i_now == 0:
                        i_now = 16
                    if i_now < i+datanum-8:
                        k_now = k + N
                    else:
                        k_now = k
                    data_xnow = df.iloc[k_now-2, i_now-1]
                    data_featurenow.append(data_xnow)
                else:
                    i_now = (i+datanum-N+n-8)%M
                    if i_now == 0:
                        i_now = 16
                    k_now = (k-n+8+8)%N+abs((k-n+8+8)//N)*N
                    data_xnow = df.iloc[k_now-2, i_now-1]
                    data_featurenow.append(data_xnow)
            if data_featureY == []:
                data_featureY = data_featurenow.copy()
            else:
                data_featureY = np.vstack((data_featureY, data_featurenow))
    # 默认的边权重（假设默认为1.0）
    default_edge_weight = 1.0
    # data_edge 仍然使用你提供的固定值
    matrix1 = np.concatenate((np.linspace(1, 8, 8), [8], np.sort(np.tile(np.linspace(9, 15, 7), (1, 2)))[0], [1]), axis=0)
    matrix2 = np.concatenate((np.linspace(0, 7, 8), np.sort(np.tile(np.linspace(8, 15, 8), (1, 2)))[0]), axis=0)
    data_edge = [matrix1, matrix2]
    graph_list = []
    list_num = 0
    for n in range(4):
        x = torch.tensor(data_feature[n, 0:M], dtype=torch.float)
        x = x.unsqueeze(1)
        e = torch.tensor(data_edge, dtype=torch.long)
        y = torch.tensor(data_featureY[n, 0:M], dtype=torch.float)
        edge_attr = torch.ones(M, 1)  # 初始设定所有边的权重为1
        edge_attr[:M-N] = 1.0  # 设定前8条边的权重为1
        edge_attr[M-N:] = 0.0  # 设定后8条边的权重为0，表示需要学习但不受节点特征影响
        graph_data = Data(x=x, edge_index=e, y=y, edge_attr=edge_attr, dtype=torch.float)
        graph_list.append(graph_data)
    return graph_list


