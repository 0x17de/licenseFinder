import os
import tempfile
import subprocess
import re

class LicenseCollector:
    data = []
    licenseLines = {}

    def __init__(self):
        for filename in os.listdir('/usr/portage/licenses'):
            fullpath = os.path.join('/usr/portage/licenses', filename)
            self.data.append(fullpath)
            with open(fullpath) as f:
                self.licenseLines[fullpath] = list(map(lambda x: re.sub(r' [ ]+', ' ', x.strip()), f.read().lower().splitlines(keepends=True)))

    def match(self,filename,buffer):
        splitBuffer = list(map(lambda x: re.sub(r' [ ]+', ' ', x.strip()), buffer.lower().decode('ASCII').splitlines(keepends=True)))
        s = set()
        for line in splitBuffer:
            if line != '':
                s.add(line)

        bestSameLineScoreLicense = (0, '')
        for licensename in self.data:
            score = 0
            for line in self.licenseLines[licensename]:
                if line in s:
                    score += 1
            score /= len(self.licenseLines[licensename])
            if score > bestSameLineScoreLicense[0]:
                bestSameLineScoreLicense = (score, licensename)
        if bestSameLineScoreLicense[1] == '':
            bestSameLineScoreLicense = None

        bestDiffScoreLicense = (0.1, '')
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write('\n'.join(splitBuffer).encode('ASCII', 'ignore'))
            tmp.flush()
            for licensename in self.data:
                with tempfile.NamedTemporaryFile() as tmp2:
                    tmp2.write('\n'.join(self.licenseLines[licensename]).encode('ASCII', 'ignore'))
                    tmp2.flush()
                    out = None
                    try:
                        out = subprocess.check_output(["/bin/bash", "-c", "diff \"{0}\" \"{1}\" | grep -E '^>' | wc -l".format(tmp.name, tmp2.name)])
                    except subprocess.CalledProcessError as e:
                        out = e.output
                    score = float(out)/len(self.licenseLines[licensename]) # ratio of changes to original license file
                    if score < bestDiffScoreLicense[0]:
                        bestDiffScoreLicense = (score, licensename)
        if bestDiffScoreLicense[1] == '':
            bestDiffScoreLicense = None

        if bestSameLineScoreLicense is None and bestDiffScoreLicense is None:
            return None
        return (bestSameLineScoreLicense, bestDiffScoreLicense)


