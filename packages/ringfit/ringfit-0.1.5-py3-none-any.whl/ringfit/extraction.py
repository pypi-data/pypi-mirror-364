# ringfit/extraction.py

import numpy as np

def _img_to_array(img):
    """
    Coerce an ehtim Image (or similar) to a 2D numpy array.
    Handles singleton dimensions and multi‐Stokes images by taking
    the first plane if needed.
    """
    # grab raw data
    if hasattr(img, "val"):
        arr = img.val
    elif hasattr(img, "data"):
        arr = img.data
    else:
        arr = img

    arr = np.array(arr)
    # remove any singleton dimensions
    arr = np.squeeze(arr)

    # if we still have >2 dims (e.g. Stokes IQUV shape (4,H,W)), take the first plane
    if arr.ndim > 2:
        arr = arr[0]

    if arr.ndim != 2:
        raise ValueError(f"Expected 2D image array, got shape {arr.shape}")

    return arr


def rbp_find_bright_points(img, threshold, radius, margin=None, max_it=999):
    """
    Find bright peaks above `threshold`, ignoring any within `margin` pixels of the edge,
    then blank out a disk of `radius` around each found peak to avoid duplicates.
    Returns an (N,2) array of (x, y) pixel coordinates.
    """
    data = _img_to_array(img)
    h, w = data.shape

    # default margin: twice the disk radius
    if margin is None:
        margin = int(radius * 2)

    # start with a mask that excludes a border of width `margin`
    mask = np.ones_like(data, bool)
    mask[:margin, :] = False
    mask[-margin:, :] = False
    mask[:, :margin] = False
    mask[:, -margin:] = False

    pts = []
    for _ in range(max_it):
        # apply mask and pick the brightest remaining pixel
        m = data * mask
        y, x = np.unravel_index(np.argmax(m), m.shape)
        if m[y, x] < threshold:
            break
        pts.append((x, y))
        # blank out a disk around that point
        yy, xx = np.ogrid[:h, :w]
        mask[(yy - y)**2 + (xx - x)**2 <= radius**2] = False

    return np.array(pts)


def polygon_for_ring(xs, ys, r_in, r_out, angs):
    """
    Build a closed polygon following the inner arc at radius r_in and
    outer arc at r_out, around center (xs, ys), over angles `angs`.
    Returns an array of shape (2*len(angs), 2) of (x,y) vertices.
    """
    xi = xs + r_in * np.cos(angs)
    yi = ys + r_in * np.sin(angs)
    xo = xs + r_out * np.cos(angs[::-1])
    yo = ys + r_out * np.sin(angs[::-1])

    x = np.concatenate([xi, xo])
    y = np.concatenate([yi, yo])
    return np.vstack([x, y]).T
