import cv2


def get_image_gray(img_file, offset_y_percent=0.078, area=None):
    img = cv2.imread(img_file) if isinstance(img_file, str) else img_file
    h, w, _ = img.shape
    if area:
        x1, y1, x2, y2 = area
        img = img[max(0, y1):min(h, y2), max(0, x1):min(w, x2), :]
    if area is None and offset_y_percent > 0:
        img = img[int(w * offset_y_percent):, :, :]
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img_gray


class HashSimilar(object):

    @staticmethod
    def perception_hash(img_gray, precision=64):
        img_scale = cv2.resize(img_gray, (precision, precision))
        img_list = img_scale.flatten()
        avg = sum(img_list)*1./len(img_list)
        avg_list = ['0' if i < avg else '1' for i in img_list]
        return [int(''.join(avg_list[x:x+4]), 2) for x in range(0, precision*precision)]

    @staticmethod
    def hamming_dist(s1, s2):
        assert len(s1) == len(s2)
        return sum([ch1 != ch2 for ch1, ch2 in zip(s1, s2)])

    @staticmethod
    def get_similar_score(image1, image2, offset_y_percent=0.078, area=None):
        img1 = get_image_gray(image1, offset_y_percent, area)
        img2 = get_image_gray(image2, offset_y_percent, area)
        hash1 = HashSimilar.perception_hash(img1)
        hash2 = HashSimilar.perception_hash(img2)
        return 1-HashSimilar.hamming_dist(hash1, hash2)*1.0 / (64*64)

