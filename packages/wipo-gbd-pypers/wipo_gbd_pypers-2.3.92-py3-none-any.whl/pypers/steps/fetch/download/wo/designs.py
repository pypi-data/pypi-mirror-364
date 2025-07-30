import os
import re
import json
import requests

from pypers.steps.base.fetch_step import FetchStep

class Designs(FetchStep):

    def _process_from_local_folder(self):
        # getting files from local dir
        if self.fetch_from.get('from_dir'):
            self.logger.info(
                'getting %s files that match the regex [%s] from %s' % (
                    'all' if self.limit == 0 else self.limit,
                    '%s or %s' % (self.file_xml_regex, self.file_img_regex),
                    self.fetch_from['from_dir']))
            xml_files = ls_dir(
                os.path.join(self.fetch_from['from_dir'], '*'),
                regex=self.file_xml_regex, limit=self.limit,
                skip=self.done_archives)

            self.output_files = xml_files
            return True
        return False
        
