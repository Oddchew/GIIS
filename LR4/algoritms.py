import math

class Transform3D:
    """Матричные геометрические преобразования (4x4)
    Строго по методичке: вектор-СТОЛБЕЦ"""

    def __init__(self):
        self.identity = [[1, 0, 0, 0],
                         [0, 1, 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]]

    def mat_vec_mul(self, M, v):
        """M (4x4) * v (4x1)"""
        return [sum(M[i][j] * v[j] for j in range(4)) for i in range(4)]

    def mat_mul(self, A, B):
        """A * B (4x4)"""
        return [[sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


    def translate(self, dx, dy, dz):
        """Перенос (1.16)"""
        return [[1, 0, 0, dx],
                [0, 1, 0, dy],
                [0, 0, 1, dz],
                [0, 0, 0, 1]]

    def rotate_x(self, theta):
        """Поворот вокруг X (1.18)"""
        c, s = math.cos(theta), math.sin(theta)
        return [[1, 0, 0, 0],
                [0, c, -s, 0],
                [0, s, c, 0],
                [0, 0, 0, 1]]

    def rotate_y(self, theta):
        """Поворот вокруг Y (1.23)"""
        c, s = math.cos(theta), math.sin(theta)
        return [[c, 0, s, 0],
                [0, 1, 0, 0],
                [-s, 0, c, 0],
                [0, 0, 0, 1]]

    def rotate_z(self, theta):
        """Поворот вокруг Z"""
        c, s = math.cos(theta), math.sin(theta)
        return [[c, -s, 0, 0],
                [s, c, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]]

    def scale(self, sx, sy, sz):
        """Масштабирование"""
        return [[sx, 0, 0, 0],
                [0, sy, 0, 0],
                [0, 0, sz, 0],
                [0, 0, 0, 1]]


    def reflect_xy(self):
        return self.scale(1, 1, -1)

    def reflect_xz(self):
        return self.scale(1, -1, 1)

    def reflect_yz(self):
        return self.scale(-1, 1, 1)



    def perspective(self, d):
        """Центральная проекция (корректнее через w)"""
        return [[1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 1 / d, 0]]


    def apply(self, points, matrix):
        result = []
        for p in points:
            v = [p[0], p[1], p[2], 1.0]
            v_trans = self.mat_vec_mul(matrix, v)

            w = v_trans[3]
            if abs(w) < 1e-9:
                w = 1e-9

            result.append((v_trans[0] / w,
                           v_trans[1] / w,
                           v_trans[2] / w))
        return result


    def compose(self, matrices):
        """
        Композиция для вектора-столбца:
        """
        res = self.identity
        for m in reversed(matrices):
            res = self.mat_mul(m, res)
        return res