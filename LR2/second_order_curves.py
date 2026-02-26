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
    def hyperbola(a, b, steps=200):
        """
        Генерация гиперболы.
        Возвращает список точек, принадлежащих гиперболе во всех четвертях.
        """
        points = []
        if a <= 0 or b <= 0:
            return points

        # Правая и левая ветви гиперболы
        for x in range(-steps, steps + 1):
            if x != 0 and abs(x) >= a:
                y_squared = b*b * ((x/a) ** 2 - 1)
                if y_squared >= 0:
                    y = math.sqrt(y_squared)
                    points.extend([(x, int(y)), (x, int(-y))])

        return points

    @staticmethod
    def parabola(p, steps=200):
        """
        Генерация полной параболы с ветвями вверх и вниз.
        Возвращает список точек, принадлежащих параболе.
        """
        points = []
        if p == 0:
            return points

        elif p > 0:
            for x in range(-steps, steps + 1):
                y = (x ** 2) / (2 * abs(p))
                points.append((x, int(y)))

        elif p < 0:
            for x in range(-steps, steps + 1):
                y = -(x ** 2) / (2 * abs(p))
                points.append((x, int(y)))

        return points