classdef Quaternion
    % 四元数类：a + b*i + c*j + d*k
    properties
        a  % 实部
        b  % i虚部
        c  % j虚部
        d  % k虚部
    end
    
    methods
        function obj = Quaternion(a, b, c, d)
            % 构造函数
            if nargin == 0
                obj.a = 0; obj.b = 0; obj.c = 0; obj.d = 0;
            elseif nargin == 1 && isa(a, 'Quaternion')
                obj = a;
            elseif nargin == 1 && isreal(a)
                obj.a = a; obj.b = 0; obj.c = 0; obj.d = 0;
            elseif nargin == 4
                obj.a = a; obj.b = b; obj.c = c; obj.d = d;
            else
                error('不支持的输入格式');
            end
        end
        
        function q = conj(obj)
            % 共轭
            q = Quaternion(obj.a, -obj.b, -obj.c, -obj.d);
        end
        
        function n = norm(obj)
            % 模
            n = sqrt(obj.a^2 + obj.b^2 + obj.c^2 + obj.d^2);
        end
        
        function disp(obj)
            % 显示
            fprintf('%g + %gi + %gj + %gk\n', obj.a, obj.b, obj.c, obj.d);
        end
        
        function result = mtimes(a, b)
            % 标量乘法
            if isscalar(a) && isa(b, 'Quaternion')
                % scalar * quaternion
                result = Quaternion(a * b.a, a * b.b, a * b.c, a * b.d);
            elseif isa(a, 'Quaternion') && isscalar(b)
                % quaternion * scalar
                result = Quaternion(a.a * b, a.b * b, a.c * b, a.d * b);
            else
                error('标量乘法只支持标量与四元数的乘积');
            end
        end
        
        function result = plus(a, b)
            % 四元数加法
            if isa(a, 'Quaternion') && isa(b, 'Quaternion')
                result = Quaternion(a.a + b.a, a.b + b.b, a.c + b.c, a.d + b.d);
            else
                error('加法只支持两个四元数的相加');
            end
        end
    end

    methods (Static)
        function Q = zeros(m, n)
            % 创建全零四元数矩阵
            if nargin == 1
                n = m;
            end
            % 初始化四元数矩阵
            Q = repmat(Quaternion(0, 0, 0, 0), m, n);
        end
        
        function Q = from_rgb_channel(R, G, B)
            % 从三个通道矩阵创建四元数矩阵
            [m, n] = size(R);
            assert(all(size(G) == [m, n]) && all(size(B) == [m, n]), ...
                   '三个通道必须具有相同的尺寸');
            
            Q = Quaternion.zeros(m, n);
            for i = 1:m
                for j = 1:n
                    Q(i, j) = Quaternion(0, R(i, j), G(i, j), B(i, j));
                end
            end
        end
        
        function [R, G, B] = to_rgb_channel(Q)
            % 将四元数矩阵分解为三个通道
            [m, n] = size(Q);
            R = zeros(m, n);
            G = zeros(m, n);
            B = zeros(m, n);
            
            for i = 1:m
                for j = 1:n
                    q = Q(i, j);
                    R(i, j) = q.b;
                    G(i, j) = q.c;
                    B(i, j) = q.d;
                end
            end
        end
    end
end