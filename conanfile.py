from conans import ConanFile, CMake, tools
import shutil

class OaiConan(ConanFile):
    name = 'oai'

	# Updating to a more recent version (https://b33p.net/kosada/node/13965) is blocking on C++11 support (https://b33p.net/kosada/node/9141).
    version = '3.2'

    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-oai'
    license = 'http://assimp.sourceforge.net/main_license.html'
    description = 'Imports various well-known 3D model formats in a uniform manner'
    source_dir = 'assimp-%s' % version
    build_dir = '_build'
    generators = 'cmake'

    def source(self):
        tools.get('https://github.com/assimp/assimp/archive/v%s.tar.gz' % self.version,
                  # sha256='60080d8ab4daaab309f65b3cffd99f19eb1af8d05623fff469b9b652818e286e'
                  )

        # https://b33p.net/kosada/node/13345
        # https://github.com/assimp/assimp/pull/1264
        tools.download('https://github.com/assimp/assimp/commit/2e455b78c8c39cf5507a1ced9887192c61fe85df.patch', '1264.patch')
        # Conan's built-in `patch` requires an exact line-number match (https://github.com/techtonik/python-patch/issues/47).
        # tools.patch(patch_file='1264.patch', base_path=self.source_dir)
        with tools.chdir(self.source_dir):
            self.run('patch -p1 < ../1264.patch')

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake = CMake(self)
            cmake.definitions['ASSIMP_BUILD_ASSIMP_TOOLS'] = False
            cmake.definitions['ASSIMP_BUILD_SAMPLES'] = False
            cmake.definitions['ASSIMP_BUILD_STATIC_LIB'] = False
            cmake.definitions['ASSIMP_BUILD_TESTS'] = False
            cmake.definitions['ASSIMP_ENABLE_BOOST_WORKAROUND'] = True
            cmake.definitions['ASSIMP_NO_EXPORT'] = True
            cmake.definitions['BUILD_SHARED_LIBS'] = True
            cmake.definitions['CMAKE_COMPILER_IS_GNUCC'] = True
            cmake.definitions['CMAKE_CXX_COMPILER'] = '/usr/local/bin/clang++'
            cmake.definitions['CMAKE_C_COMPILER'] = '/usr/local/bin/clang'
            cmake.definitions['CMAKE_C_FLAGS'] = cmake.definitions['CMAKE_CXX_FLAGS'] = '-Oz -mmacosx-version-min=10.8 -DNDEBUG'
            cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64'

            cmake.configure(source_dir='../%s' % self.source_dir,
                            build_dir='.')
            cmake.build()

            # The tagged version is 3.2, but the built version is 3.2.0...
            shutil.move('code/libassimp.3.2.0.dylib', 'code/liboai.dylib')
            self.run('install_name_tool -id @rpath/liboai.dylib code/liboai.dylib')

    def package(self):
        self.copy('*.h', src='%s/include' % self.source_dir, dst='include')
        self.copy('*.inl', src='%s/include' % self.source_dir, dst='include')
        self.copy('liboai.dylib', src='%s/code' % self.build_dir, dst='lib')
        # self.run('ln -s . include/assimp')

    def package_info(self):
        self.cpp_info.libs = ['oai']
        self.cpp_info.includedirs = ['include', 'include/assimp']
