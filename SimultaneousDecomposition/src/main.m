% 加载图像（示例）
cover{1} = imread('lena.png');
cover{2} = imread('baboon.png');
cover{3} = imread('peppers.png');
cover{4} = imread('flamingos.png');
cover{5} = imread('dog.png');

% 隐秘信息（可以使用同一张logo，或5张不同的）
secret_img = imread('logo.png');
for i = 1:5
    secret{i} = secret_img;  % 假设所有载体嵌入相同隐秘信息
end

% 嵌入强度（可根据论文表4.1选择）
alpha = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2];

% 执行嵌入
[embedded, keys] = embed_quaternion_images(cover, secret, alpha);

% 显示结果
for i = 1:5
    figure;
    subplot(1,2,1); imshow(cover{i}); title('原始载体');
    subplot(1,2,2); imshow(embedded{i}); title('嵌入后');
end