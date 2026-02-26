def ipart(x: float) -> int:
    return int(x)

def fpart(x: float) -> float:
    return x - ipart(x)

def rfpart(x: float) -> float:
    return 1.0 - fpart(x)

def draw_by_line(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int, float]]:
    pixels = []
    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0

    if dx == 0.0 and dy == 0.0:
        plot(pixels, x0, y0, 1.0)
        return pixels

    if dx == 0.0:
        for y in range(min(y0, y1), max(y0, y1) + 1):
            plot(pixels, x0, y, 1.0)
        return pixels

    gradient = dy / dx

    # Обработка начальной точки
    xend = round(x0)
    yend = y0 + gradient * (xend - x0)
    xgap = rfpart(x0 + 0.5)
    xpxl1 = xend
    ypxl1 = ipart(yend)

    if steep:
        plot(pixels, ypxl1, xpxl1, rfpart(yend) * xgap)
        plot(pixels, ypxl1 + 1, xpxl1, fpart(yend) * xgap)
    else:
        plot(pixels, xpxl1, ypxl1, rfpart(yend) * xgap)
        plot(pixels, xpxl1, ypxl1 + 1, fpart(yend) * xgap)

    # Обработка конечной точки
    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = fpart(x1 + 0.5)
    xpxl2 = xend
    ypxl2 = ipart(yend)

    if steep:
        plot(pixels, ypxl2, xpxl2, rfpart(yend) * xgap)
        plot(pixels, ypxl2 + 1, xpxl2, fpart(yend) * xgap)
    else:
        plot(pixels, xpxl2, ypxl2, rfpart(yend) * xgap)
        plot(pixels, xpxl2, ypxl2 + 1, fpart(yend) * xgap)

    # Основной цикл
    if steep:
        for x in range(xpxl1 + 1, xpxl2):
            intery = y0 + gradient * (x - x0)
            plot(pixels, ipart(intery), x, rfpart(intery))
            plot(pixels, ipart(intery) + 1, x, fpart(intery))
    else:
        for x in range(xpxl1 + 1, xpxl2):
            intery = y0 + gradient * (x - x0)
            plot(pixels, x, ipart(intery), rfpart(intery))
            plot(pixels, x, ipart(intery) + 1, fpart(intery))

    return pixels

def plot(pixels: list, x: int, y: int, brightness: float):
    if brightness > 0.0:
        pixels.append((x, y, brightness))
