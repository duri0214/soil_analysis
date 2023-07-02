from unittest import TestCase

from crm.domain.valueobject.capturelocation import CaptureLocation
from crm.domain.valueobject.photo.androidphoto import AndroidPhoto


class TestAndroidPhoto(TestCase):
    def setUp(self):
        self.file_path = r"D:/OneDrive/ダウンロード/android/ススムＢ1_right.jpg"
        self.android_photo = AndroidPhoto(self.file_path)
        self.android_photo.exif_data = self.android_photo._extract_exif_data()

    def test_extract_date(self):
        # 正常な値のテスト
        expected_date = "2023-06-18"
        actual_date = self.android_photo._extract_date()
        self.assertEqual(expected_date, actual_date)

        # GPS GPSDate が None の場合のテスト
        self.android_photo.exif_data["GPS GPSDate"] = None
        with self.assertRaises(ValueError):
            self.android_photo._extract_date()

    def test_extract_location(self):
        # 正常な値のテスト
        expected_location = CaptureLocation(137.6494111111111, 34.745)
        actual_location = self.android_photo._extract_location()
        self.assertEqual(expected_location.corrected.get_coords(), actual_location.corrected.get_coords())

        # GPS GPSLongitude が None の場合のテスト
        self.android_photo.exif_data["GPS GPSLongitude"] = None
        with self.assertRaises(ValueError):
            self.android_photo._extract_location()

        # GPS GPSLatitude が None の場合のテスト
        self.android_photo.exif_data["GPS GPSLatitude"] = None
        with self.assertRaises(ValueError):
            self.android_photo._extract_location()
