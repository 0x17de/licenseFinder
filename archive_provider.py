import tarfile
import re
import tempfile
import magic


class ArchiveProvider:
    mime = magic.Magic(mime=True)
    tar = None
    def __init__(self, tarpath):
        self.tar = tarfile.open(tarpath, 'r')

        self.members = self.tar.getmembers()
        self.members.sort(key=lambda info: re.sub(r'^.*/', r'', info.name))
        self.members.sort(key=lambda info: re.sub(r'^(.*/)[^/]*', r'\1', info.name))

    def get_candidates(self):
        for info in self.members:
            if not info.isfile():
                continue

            if re.search(r"/license(\.|$)", info.name.lower()) or re.search(r"/copying(\.|$)", info.name.lower()):
                yield (info.name,self.tar.extractfile(info).read())

    def get_further_candidates(self):
        for info in self.members:
            if not info.isfile():
                continue

            data = self.tar.extractfile(info)
            with tempfile.NamedTemporaryFile() as tmp:
                buf = data.read()
                type = self.mime.from_buffer(buf)
                if type == b'text/plain':
                    yield (info.name,buf)

