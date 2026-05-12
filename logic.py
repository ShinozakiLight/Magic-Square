def generate_magic_square(n: int):
    if n == 4:
        grid = [[r * 4 + c + 1 for c in range(4)] for r in range(4)]
        flip = {(0, 0), (0, 3), (3, 0), (3, 3), (1, 1), (1, 2), (2, 1), (2, 2)}
        for r in range(4):
            for c in range(4):
                if (r, c) in flip: grid[r][c] = 17 - grid[r][c]
        return grid
    else:
        grid = [[0] * n for _ in range(n)]
        num, r, c = 1, 0, n // 2
        while num <= n * n:
            grid[r][c] = num
            num += 1
            nr, nc = (r - 1) % n, (c + 1) % n
            if grid[nr][nc] != 0: r = (r + 1) % n
            else: r, c = nr, nc
        return grid

def rotate_grid(grid, k):
    res = [row[:] for row in grid]
    for _ in range(k % 4):
        res = [list(row) for row in zip(*res[::-1])]
    return res