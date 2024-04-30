import logging
import glob
import cv2 as cv
import numpy as np

logger = logging.getLogger(__name__)


class Camera:
    """
    Hold camera data. Can give frames with calibration, resizing, and other modifications
    """
    def __init__(self,
                 output_resolution: tuple[int],
                 inclination_fov: tuple[float],
                 azimuth_fov: tuple[float],
                 calibration=None,
                 ):
        """
        :param output_resolution: The output resolution of the camera
        :param inclination_fov: The fov on the inclination axis
        :param azimuth_fov: The fov on the azimuth axis
        :param calibration: The calibration profile of the camera. Optional. Can either pass it here or generate a new
        profile with calibrate(). Must be organized to match cv.undistort (mtx, dist, None, newcameramtx). See
        documentation in calibrate()
        """
        self.camera = cv.VideoCapture(0)

        self.camera_resolution = None   # Must take first image to get this
        self.output_resolution = output_resolution
        self.inclination_fov = inclination_fov
        self.azimuth_fov = azimuth_fov

        self.calibration = calibration

    def read(self):
        """
        Get a single frame
        :return: A frame taken from the camera
        """
        ret, image = self.camera.read()

        # Make sure camera took a picture
        if not ret:
            logger.warning('could not get image')

        # calibrate
        if self.calibration is not None:
            image = cv.undistort(image, *self.calibration)

        # If no calibration is available, still resize image
        else:
            image = cv.resize(image, self.output_resolution)

        # Return image
        return image

    def calibrate(self, checkerboard_size: tuple[int]):
        """
        Calibrate the camera
        :return: None
        """

        # Get camera resolution if needed
        if self.camera_resolution is None:
            self.read() # Read finds camera resolution from a test image

        # termination criteria
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

        # Arrays to store object points and image points from all the images.
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.

        images = glob.glob('/calibration_images/*.jpeg')

        for fname in images:
            img = cv.imread(fname)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv.findChessboardCorners(gray, checkerboard_size, None)

            # If found, add object points, image points (after refining them)
            if ret:
                objpoints.append(objp)

            corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            cv.drawChessboardCorners(img, checkerboard_size, corners2, ret)
            cv.imshow('img', img)
            cv.waitKey(500)

        cv.destroyAllWindows()

        # Post-processing
        ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        newcameramtx, roi =(mtx, dist, self.camera_resolution, 1, self.output_resolution)

        # Pack in order to unpack in cv.undistort
        self.calibration = (mtx, dist, None, newcameramtx)

        # Return incase the programs wants it back to save for a later use
        return self.calibration