import torch
import torch.nn as nn
import torch.optim as optim
from createGraph import createGraph
from torch_geometric.nn import GATConv
from torch_geometric.nn import MessagePassing
from torch_geometric.data import DataLoader
from torch_geometric.utils import add_self_loops, degree


class EdgeWeightLayer(MessagePassing):
    def __init__(self, in_channels, out_channels, heads=1):
        super(EdgeWeightLayer, self).__init__(aggr='add')
        self.lin = nn.Linear(in_channels, out_channels * heads)

    def forward(self, x, edge_index):
        edge_index, _ = add_self_loops(edge_index, num_nodes=x.size(0))
        return self.propagate(edge_index, x=x)

    def message(self, x_i, x_j, edge_index, size_i):
        return self.lin(x_j - x_i)

class CustomGAT(nn.Module):
    def __init__(self, in_channels, out_channels, num_heads):
        super(CustomGAT, self).__init__()
        self.conv_learnable = EdgeWeightLayer(in_channels, out_channels, heads=num_heads)
        # 定义需要固定为1的边权重
        self.fixed_edge_weights_1 = nn.Parameter(torch.tensor([1.0], dtype=torch.float))

        # 定义需要学习但不受节点特征影响的边权重
        self.learnable_edge_weights_2 = nn.Parameter(torch.tensor([-0.5], dtype=torch.float))

        # 定义需要学习但不受节点特征影响的另一类边权重
        self.learnable_edge_weights_3 = nn.Parameter(torch.tensor([1.5], dtype=torch.float))

    def forward(self, x, edge_index):
        # 计算学习到的边权重的注意力分数
        learned_edge_scores = self.conv_learnable(x, edge_index)

        # 获取固定为1的边的权重
        fixed_edge_weights_1 = self.fixed_edge_weights_1.expand_as(learned_edge_scores)

        # 获取学习但不受节点特征影响的边权重
        learnable_edge_weights_2 = self.learnable_edge_weights_2.expand_as(learned_edge_scores)

        # 获取另一类学习但不受节点特征影响的边权重
        learnable_edge_weights_3 = self.learnable_edge_weights_3.expand_as(learned_edge_scores)

        # 创建一个新的张量，与 fixed_edge_weights_1 形状相同
        final_edge_scores = torch.zeros(24, 1)

        # 将张量各部分赋值
        final_edge_scores[:8] = fixed_edge_weights_1[:8]
        final_edge_scores[8::2] = learnable_edge_weights_2[::2]
        final_edge_scores[9::2] = learnable_edge_weights_3[::2]
        final_edge_scores[8:] = final_edge_scores[8:] + learned_edge_scores

        # 1. 计算节点聚合的邻居特征，考虑边的方向和权重
        aggregated_neighbors = torch.zeros_like(x)
        for i in range(edge_index.size(1)):
            source, target = edge_index[0, i], edge_index[1, i]
            aggregated_neighbors[target] += x[source] * final_edge_scores[i]

        # 3. 应用激活函数
        output = torch.relu(aggregated_neighbors)

        # # 将注意力分数传递给 GATConv 层
        # x = self.conv_learnable(x, edge_index, edge_attr=final_edge_scores)
        return output


# class GATPredictor(nn.Module):
#     def __init__(self, in_channels, out_channels, num_heads):
#         super(GATPredictor, self).__init__()
#
#         # 定义 GATConv 层，用于学习不受节点特征影响的边权重
#         self.conv_learnable = GATConv(in_channels, out_channels, heads=num_heads)
#
#         # 定义需要固定为1的边权重
#         self.fixed_edge_weights_1 = nn.Parameter(torch.tensor([1.0], dtype=torch.float))
#
#         # 定义需要学习但不受节点特征影响的边权重
#         self.learnable_edge_weights_2 = nn.Parameter(torch.tensor([-0.5], dtype=torch.float))
#
#         # 定义需要学习但不受节点特征影响的另一类边权重
#         self.learnable_edge_weights_3 = nn.Parameter(torch.tensor([1.5], dtype=torch.float))
#
#     def forward(self, x, edge_index):
#         # 计算学习到的边权重的注意力分数
#         learned_edge_scores = self.conv_learnable(x, edge_index)
#
#         # 获取固定为1的边的权重
#         fixed_edge_weights_1 = self.fixed_edge_weights_1.expand_as(learned_edge_scores)
#
#         # 获取学习但不受节点特征影响的边权重
#         learnable_edge_weights_2 = self.learnable_edge_weights_2.expand_as(learned_edge_scores)
#
#         # 获取另一类学习但不受节点特征影响的边权重
#         learnable_edge_weights_3 = self.learnable_edge_weights_3.expand_as(learned_edge_scores)
#
#         # 最终的注意力分数是三者的和
#         final_edge_scores = learned_edge_scores + fixed_edge_weights_1 + learnable_edge_weights_2 + learnable_edge_weights_3
#
#         # 创建一个新的张量，与 fixed_edge_weights_1 形状相同
#         final_edge_scores = torch.zeros(24, 1)
#
#         # 将张量各部分赋值
#         final_edge_scores[:8] = fixed_edge_weights_1[:8]
#         final_edge_scores[8::2] = learnable_edge_weights_2[::2]
#         final_edge_scores[9::2] = learnable_edge_weights_3[::2]
#         final_edge_scores[8:] = final_edge_scores[8:] + learned_edge_scores
#
#         # 将注意力分数传递给 GATConv 层
#         x = self.conv_learnable(x, edge_index, edge_attr=final_edge_scores)
#         return x


# 主函数部分
N = 8  # 车站
M = 16  # 列车

# 获取图数据
graph_list = createGraph()

# 初始化模型、损失函数和优化器
model = CustomGAT(in_channels=1, out_channels=1, num_heads=1)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)



# 准备数据集和数据加载器
dataset = graph_list
loader = DataLoader(dataset, batch_size=1, shuffle=True)

# 训练模型
epochs = 10
model.train()

for epoch in range(epochs):
    for data in loader:
        # 将一部分边的特征固定为1
        edge_attr_fixed = torch.ones_like(data.edge_attr, dtype=torch.float)
        edge_attr_fixed[:M - N] = 1.0
        optimizer.zero_grad()
        out = model(data.x, data.edge_index)
        loss = criterion(out, data.y)
        loss.backward()
        optimizer.step()

# 模型训练完成后，可以用训练好的模型进行预测
model.eval()
predicted_traffics = []

# 模型训练完成后，你可以通过访问模型的参数来获取学到的边权重值
with torch.no_grad():
    learned_edge_weights = model.conv_learnable.att.data.numpy()
    fixed_edge_weights_1 = model.fixed_edge_weights_1.data.numpy()
    learnable_edge_weights_2 = model.learnable_edge_weights_2.data.numpy()
    learnable_edge_weights_3 = model.learnable_edge_weights_3.data.numpy()

# 打印学到的边权重值和固定边权重值
print("Learned Edge Weights:", learned_edge_weights)
print("Fixed Edge Weights 1:", fixed_edge_weights_1)
print("Learnable Edge Weights 2:", learnable_edge_weights_2)
print("Learnable Edge Weights 3:", learnable_edge_weights_3)

# 获取 GATConv 层的权重
with torch.no_grad():
    for graph_data in graph_list:
        output = model(data.x, data.edge_index, data.edge_attr)
        print(output)  # 添加这行，查看模型的实际输出
        attention_scores = output[1]  # 假设注意力分数是输出中的第二个元素
        edge_weights.append(attention_scores)


