from conans import ConanFile

class OaiTestConan(ConanFile):
    generators = 'qbs'

    def build(self):
        self.run('qbs -f "%s"' % self.source_folder)

    def imports(self):
        self.copy('*', src='lib', dst='lib')

    def test(self):
        self.run('qbs run')

        # Ensure we only link to system libraries and to libraries we built.
        self.run('! (otool -L lib/liboai.dylib | tail +3 | egrep -v "^\s*(/usr/lib/|/System/|@rpath/)")')
        self.run('! (otool -l lib/liboai.dylib | grep -A2 LC_RPATH | cut -d"(" -f1 | grep "\s*path" | egrep -v "^\s*path @(executable|loader)_path")')
