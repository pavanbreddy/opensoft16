from document import document
import subprocess
import re

#requires Ghost Script installed in system Which is default in Ubuntu
def process(pdf_path="a.pdf",job_number = 1):	#pdf_path is pdf name in current directory and job_number is for processing multiple pdf files
	Extraction = subprocess.check_output("gs -sDEVICE=jpeg -o file-"+ str(job_number) +"-%03d.jpg -r144 " +pdf_path,shell=True);
	num_vector = map(int, re.findall(r'\d+', Extraction));
	pages_processed = num_vector[len(num_vector)-1];
	return pages_processed;

def __main__():
	# This function process all the pdfs in the docList
	e = document()
	docList = []
	docList.append(e)
	
	for d in docList:
		d.process()
