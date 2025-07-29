# ringfit/extraction.py

import numpy as np

def _img_to_array(img):
    """
    Coerce an ehtim Image (or similar) to a 2D numpy array.
    """
    if hasattr(img, "val"):
        arr = img.val
    elif hasattr(img, "data"):
        arr = img.data
    else:
        arr = img
    arr = np.array(arr)
    # if extra singleton dimension, squeeze it out
    if arr.ndim > 2 and 1 in arr.shape:
        arr = arr.squeeze()
    if arr.ndim != 2:
        raise ValueError(f"Expected 2D image array, got shape {arr.shape}")
    return arr

def rbp_find_bright_points(img, threshold, radius, margin=None, max_it=999):
    """
    Finds bright peaks above `threshold`, then blanks out
    a circular region of `radius` around each found peak
    to avoid duplicates. Also ignores any peaks within
    `margin` pixels of the image edge.

    Returns an (N,2) array of (x, y) coordinates.
    """
    data = _img_to_array(img)
    h, w = data.shape

    # set default margin to twice the radius if not given
    if margin is None:
        margin = int(radius * 2)

    # initial mask: Ones everywhere except a border of width `margin`
    mask = np.ones_like(data, bool)
    mask[:margin, :] = False
    mask[-margin:, :] = False
    mask[:, :margin] = False
    mask[:, -margin:] = False

    pts = []
    for _ in range(max_it):
        # apply mask and find the brightest remaining pixel
        m = data * mask
        y, x = np.unravel_index(np.argmax(m), m.shape)
        if m[y, x] < threshold:
            break
        pts.append((x, y))
        # blank out a disk of radius `radius` around that point
        yy, xx = np.ogrid[:h, :w]
        mask[(yy - y)**2 + (xx - x)**2 <= radius**2] = False

    return np.array(pts)


def polygon_for_ring(xs, ys, r_in, r_out, angs):
    """
    Build a closed polygon following two arcs (inner & outer).
    - xs, ys: center of ring
    - r_in, r_out: inner and outer radii
    - angs: 1D numpy array of angles in radians

    Returns an array of shape (2*len(angs), 2) giving the
    polygon vertices.
    """
    xi = xs + r_in * np.cos(angs)
    yi = ys + r_in * np.sin(angs)
    xo = xs + r_out * np.cos(angs[::-1])
    yo = ys + r_out * np.sin(angs[::-1])

    x = np.concatenate([xi, xo])
    y = np.concatenate([yi, yo])
    return np.vstack([x, y]).T
