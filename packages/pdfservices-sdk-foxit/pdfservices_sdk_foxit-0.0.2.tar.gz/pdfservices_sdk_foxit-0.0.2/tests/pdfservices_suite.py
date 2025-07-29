import unittest 
import sys
import os 

target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src/pdfservices_sdk_foxit'))
sys.path.append(target_dir)
from pdf_service_sdk import PDFServiceSDK 
class TestPDFServiceSDK(unittest.TestCase):

	def setUp(self):
		self.sdk = PDFServiceSDK(os.environ.get('CLIENT_ID'), os.environ.get('CLIENT_SECRET'))
		self.thisdir = os.path.dirname(os.path.abspath(__file__))
		
	def test_upload(self):
		result = self.sdk.upload(f'{self.thisdir}/input/input.docx')
		self.assertIsNotNone(result)

	def test_word_to_pdf(self):
		self.sdk.word_to_pdf(f'{self.thisdir}/input/input.docx', f'{self.thisdir}/output/output.pdf')
		self.assertTrue(os.path.exists(f'{self.thisdir}/output/output.pdf'))		

	def test_combine(self):
		inputs = [f'{self.thisdir}/input/input.pdf', f'{self.thisdir}/input/second.pdf']
		self.sdk.combine(inputs, f'{self.thisdir}/output/output_combined.pdf')
		self.assertTrue(os.path.exists(f'{self.thisdir}/output/output_combined.pdf'))		

	"""
	Currently there isn't a way to confirm the option *worked*, but I want to ensure 
	it doesn't throw at least.
	"""
	def test_combine_with_options(self):
		inputs = [f'{self.thisdir}/input/input.pdf', f'{self.thisdir}/input/second.pdf']
		config = {
			"addBookmark":False
		}
		self.sdk.combine(inputs, f'{self.thisdir}/output/output_combined_nobookmarks.pdf',config)
		self.assertTrue(os.path.exists(f'{self.thisdir}/output/output_combined_nobookmarks.pdf'))		

if __name__ == '__main__':
	unittest.main()