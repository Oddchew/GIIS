class InterpolationCurves:
    def matrix_vector_multiply(self, matrix, vector):
        """
        Умножение матрицы на вектор: matrix * vector (column)
        """
        return [sum(matrix[i][j] * vector[j] for j in range(len(vector))) for i in range(len(matrix))]

    def vector_dot(self, vec1, vec2):
        """
        Скалярное произведение двух векторов.
        """
        return sum(vec1[i] * vec2[i] for i in range(len(vec1)))

    def hermite(self, P1, R1, P4, R4):
        """
        Генерация точек для кривой Эрмита с использованием матричной формы.
        """
        points = []
        M = [
            [2, -2, 1, 1],
            [-3, 3, -2, -1],
            [0, 0, 1, 0],
            [1, 0, 0, 0]
        ]
        Gx = [P1[0], P4[0], R1[0], R4[0]]
        Gy = [P1[1], P4[1], R1[1], R4[1]]
        MGx = self.matrix_vector_multiply(M, Gx)
        MGy = self.matrix_vector_multiply(M, Gy)
        steps = 100
        for i in range(steps + 1):
            t = i / steps
            T = [t**3, t**2, t, 1]
            x = round(self.vector_dot(T, MGx))
            y = round(self.vector_dot(T, MGy))
            points.append((x, y))
        return list(set(points))

    def bezier(self, P1, P2, P3, P4):
        """
        Генерация точек для кривой Безье с использованием матричной формы.
        """
        points = []
        M = [
            [-1, 3, -3, 1],
            [3, -6, 3, 0],
            [-3, 3, 0, 0],
            [1, 0, 0, 0]
        ]
        Gx = [P1[0], P2[0], P3[0], P4[0]]
        Gy = [P1[1], P2[1], P3[1], P4[1]]
        MGx = self.matrix_vector_multiply(M, Gx)
        MGy = self.matrix_vector_multiply(M, Gy)
        steps = 100
        for i in range(steps + 1):
            t = i / steps
            T = [t**3, t**2, t, 1]
            x = round(self.vector_dot(T, MGx))
            y = round(self.vector_dot(T, MGy))
            points.append((x, y))
        return list(set(points))

    def b_spline(self, controls):
        """
        Генерация точек для B-сплайна с использованием матричной формы.
        """
        if len(controls) < 4:
            return []
        # Для открытого сплайна дублируем концы
        full_controls = [controls[0]] + controls + [controls[-1]]
        points = []
        M = [ [x/6 for x in row] for row in [[-1,3,-3,1],[3,-6,3,0],[-3,0,3,0],[1,4,1,0]] ]
        n = len(controls)
        steps = 100
        for i in range(1, n):
            Gx = [full_controls[i-1][0], full_controls[i][0], full_controls[i+1][0], full_controls[i+2][0]]
            Gy = [full_controls[i-1][1], full_controls[i][1], full_controls[i+1][1], full_controls[i+2][1]]
            MGx = self.matrix_vector_multiply(M, Gx)
            MGy = self.matrix_vector_multiply(M, Gy)
            for j in range(steps + 1):
                t = j / steps
                T = [t**3, t**2, t, 1]
                x = round(self.vector_dot(T, MGx))
                y = round(self.vector_dot(T, MGy))
                points.append((x, y))
        return list(set(points))