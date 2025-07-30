import cv2

img = cv2.imread("docs/assets/logo.jpeg")
img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
cv2.imshow("logo", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

