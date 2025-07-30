import os
import codecs
import shutil
import xml.etree.ElementTree as ET
from pypers.steps.base.extract_step import ExtractStep
from pypers.utils import utils
from datetime import datetime

class Designs(ExtractStep):
    """
    Extract WOID archives
    """
    spec = {
        "version": "0.1",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args": {
            "inputs": [
                {
                    "name": "xml_ref_dir",
                    "descr": "the directory that contains the ST.96 XML files ready to be processed",
                    "value": "/data/designs/woid-enriched"
                }
            ],
            "outputs": [
                {
                    "name": "manifest",
                    "descr": "otherwise does not seem accessible for binding, well it's pypers..."
                }
            ],
        }
    }

    def preprocess(self):
        print("designs extract preprocess")
        print("xml_ref_dir:", self.xml_ref_dir)
        
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        self.manifest = {}
        # self.archives is a tuple of (date, {archive_name: xxx, archives[]})

        extraction_date = datetime.today().strftime('%Y-%m-%d')
        # dummy name for the first import
        archive_name = "first_import"
        # prepare destination dir under pipeline scratch dir
        self.extraction_dir = os.path.join(
            self.meta['pipeline']['output_dir'],
            '__scratch',
            extraction_date,
            archive_name
        )

        print("self.extraction_dir:", self.extraction_dir)

        # deletes the directory if prev exists
        utils.mkdir_force(self.extraction_dir)
        self.xml_count = 0
        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive_name,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}

        for r, d, files in os.walk(self.xml_ref_dir):
            for file in files:
                if file.endswith(".st96.xml"):
                    self.add_xml_file(file, os.path.join(r, file))
                    #break

        #print(self.manifest)

    def add_xml_file(self, filename, fullpath):
        # go through the xml directory and collect XML files, 
        # images can be identified from the XML 

        print("add", filename, fullpath)

        appnum = filename.split(".")[0]
        print(appnum)

        self.manifest['data_files'].setdefault(appnum, {})
        #self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
        #    fullpath, self.extraction_dir
        #)
        self.manifest['data_files'][appnum]['ori'] = fullpath
    
    def add_img_file(self, appnum, url):
        path = os.path.relpath(fullpath, self.extraction_dir)

        # we need to parse the XML file and get each image information for download
        urls = [""]

        self.manifest['img_files'].setdefault(appnum, [])
        for url in urls:
            self.manifest['img_files'][appnum].append(
                {'url': url}
            )

    def process(self):
        # pypers is so confusing...
        self.manifest = [self.manifest]

