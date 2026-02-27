import math


class SecondOrderCurves:
    @staticmethod
    def bresenham_circle(radius):
        """
        Алгоритм Брезенхема для генерации окружности.
        """
        x = 0
        y = radius
        d = 2 * (1 - radius)
        points = set()

        while y >= 0:
            points.update([(x, y), (x, -y), (-x, y), (-x, -y),
                           (y, x), (y, -x), (-y, x), (-y, -x)])
            if d < 0:
                d1 = 2 * (d + y) - 1
                x += 1
                if d1 <= 0:
                    d += 2 * x + 1
                else:
                    y -= 1
                    d += 2 * (x - y) + 1
            else:
                d2 = 2 * (d - x) - 1
                y -= 1
                if d2 > 0:
                    d += 1 - 2 * y
                else:
                    x += 1
                    d += 2 * (x - y)
        return points

    @staticmethod
    def bresenham_ellipse(a, b):
        """
        Алгоритм Брезенхема для генерации эллипса.
        """
        x = 0
        y = b
        a_sq = a * a
        b_sq = b * b
        d = b_sq - a_sq * b + 0.25 * a_sq
        points = set()

        while x * b_sq < y * a_sq:
            points.update([(x, y), (x, -y), (-x, y), (-x, -y)])
            if d < 0:
                d += b_sq * (2 * x + 1)
            else:
                d += b_sq * (2 * x + 1) + a_sq * (-2 * y + 1)
                y -= 1
            x += 1

        d = b_sq * (x + 0.5) ** 2 + a_sq * (y - 1) ** 2 - a_sq * b_sq
        while y >= 0:
            points.update([(x, y), (x, -y), (-x, y), (-x, -y)])
            if d > 0:
                d += a_sq * (-2 * y + 1)
            else:
                d += b_sq * (2 * x + 1) + a_sq * (-2 * y + 1)
                x += 1
            y -= 1
        return points

    @staticmethod
    def hyperbola(c_x, c_y, a, b):
        """
        Алгоритм Брезенхема для генерации гиперболы с центром (c_x, c_y).
        Рисует обе ветви (правую и левую) во всех четырёх четвертях.
        """
        points = []
        if a < 1:
            return points

        x0, y0 = c_x, c_y
        x, y = a, 0
        a2, b2 = a * a, b * b
        d1 = b2 - a2 * 0.75

        # Регион 1
        while b2 * x > a2 * y:
            # 4 симметричные точки: правая/левая ветвь, верх/низ
            points.extend([
                (x0 + x, y0 + y),
                (x0 + x, y0 - y),
                (x0 - x, y0 + y),
                (x0 - x, y0 - y),
            ])

            if d1 < 0:
                d1 += b2 * (2 * y + 3)
            else:
                d1 += b2 * (2 * y + 3) - a2 * (2 * x - 2)
                x += 1
            y += 1
            if x > 10000 or y > 10000:
                break

        # Регион 2
        d2 = b2 * (x + 0.5) ** 2 - a2 * (y + 1) ** 2 - a2 * b2
        while x < 500:
            points.extend([
                (x0 + x, y0 + y),
                (x0 + x, y0 - y),
                (x0 - x, y0 + y),
                (x0 - x, y0 - y),
            ])

            if d2 > 0:
                d2 -= a2 * (2 * x - 3)
            else:
                d2 += b2 * (2 * y + 2) - a2 * (2 * x - 3)
                y += 1
            x += 1
            if x > 10000 or y > 10000:
                break

        return points


    @staticmethod
    def parabola(c_x, c_y, p):
        """
        Алгоритм Брезенхема для генерации параболы с вершиной в (c_x, c_y).
        Рисует ветви вверх и вниз.
        """
        points = []
        if p < 1:
            return points

        x0, y0 = c_x, c_y
        x, y = 0, 0
        d = 1.0 - 2.0 * p

        # Регион 1
        while x * x < 4 * p * y:
            points.extend([
                (x0 + x, y0 + y),  # вверх
                (x0 + x, y0 - y),  # вниз
                (x0 - x, y0 + y),
                (x0 - x, y0 - y),
            ])

            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * x + 3 - 4 * p
                y += 1
            x += 1

        # Регион 2
        d2 = (x + 0.5) ** 2 - 4.0 * p * (y + 1)
        while y < 10000:
            points.extend([
                (x0 + x, y0 + y),
                (x0 + x, y0 - y),
                (x0 - x, y0 + y),
                (x0 - x, y0 - y),
            ])

            if d2 > 0:
                d2 += -4.0 * p + 2
            else:
                d2 += 2 * x - 4.0 * p + 2
                x += 1
            y += 1

        return points
