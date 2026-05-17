import numpy as np

def fungsi_konvolusi(X, F):
    X_height, X_width = X.shape
    F_height, F_width = F.shape

    H = F_height // 2
    W = F_width // 2

    out = np.zeros((X_height, X_width))

    for i in range(H, X_height - H):
        for j in range(W, X_width - W):
            sum = 0

            for k in range(-H, H+1):
                for l in range(-W, W+1):
                    a = X[i+k, j+l]
                    w = F[H+k, W+l]
                    sum += w * a

            out[i, j] = sum

    return out
