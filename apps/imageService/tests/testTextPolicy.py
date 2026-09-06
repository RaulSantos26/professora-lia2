import unittest
from types import SimpleNamespace
from unittest.mock import patch
from app.imageServiceApplication import ZImageRuntime, ImageJobRequest


class TextPolicyTests(unittest.TestCase):
    def check(self, x, y, w, h, allowed):
        data = dict(text=['marks', 'marks'], conf=[90, 90], left=[x, x], top=[y, y], width=[w, w], height=[h, h])
        image = SimpleNamespace(size=(768, 576), convert=lambda mode: None)
        with patch('pytesseract.image_to_data', return_value=data):
            return ZImageRuntime._containsDetectedText(image, allowSceneMarks=allowed)

    def testSmallInteriorMarksAllowedOnlyWhenRequested(self):
        self.assertFalse(self.check(300, 250, 60, 12, True))
        self.assertTrue(self.check(300, 250, 60, 12, False))

    def testLargeCaptionRejected(self):
        self.assertTrue(self.check(300, 250, 190, 50, True))

    def testMarginCaptionRejected(self):
        self.assertTrue(self.check(20, 10, 60, 12, True))

    def testDefaultPolicyRemainsStrict(self):
        job = ImageJobRequest(requestId='test-request', prompt='A historical scene without labels', title='Teste', imageMode='ILLUSTRATION')
        self.assertEqual(job.textPolicy, 'NO_TEXT')


if __name__ == '__main__':
    unittest.main()
