from conans import ConanFile, CMake, tools
import platform
import os
import shutil

class OaiConan(ConanFile):
    name = 'oai'

    source_version = '5.0.1'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
        'vuoutils/1.2@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://www.assimp.org/'
    license = 'http://www.assimp.org/index.php/license'
    description = 'Imports various well-known 3D model formats in a uniform manner'
    source_dir = 'assimp-%s' % source_version
    build_dir = '_build'
    install_dir = '_install'
    generators = 'cmake'
    libs = {
        'IrrXML': '',
        'assimp': '5.0.0',
    }

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://github.com/assimp/assimp/archive/v%s.tar.gz' % self.source_version,
                  sha256='11310ec1f2ad2cd46b95ba88faca8f7aaa1efe9aa12605c55e3de2b977b3dbfc')

        self.run('mv %s/LICENSE %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake = CMake(self)
            cmake.definitions['ASSIMP_BUILD_ASSIMP_TOOLS'] = False
            cmake.definitions['ASSIMP_BUILD_SAMPLES'] = False
            cmake.definitions['ASSIMP_BUILD_STATIC_LIB'] = False
            cmake.definitions['ASSIMP_BUILD_TESTS'] = False
            cmake.definitions['ASSIMP_NO_EXPORT'] = True
            cmake.definitions['BUILD_SHARED_LIBS'] = True
            cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
            cmake.definitions['CMAKE_COMPILER_IS_GNUCC'] = True
            cmake.definitions['CMAKE_CXX_COMPILER'] = self.deps_cpp_info['llvm'].rootpath + '/bin/clang++'
            cmake.definitions['CMAKE_C_COMPILER'] = self.deps_cpp_info['llvm'].rootpath + '/bin/clang'
            cmake.definitions['CMAKE_C_FLAGS'] = cmake.definitions['CMAKE_CXX_FLAGS'] = '-Oz -DNDEBUG'
            cmake.definitions['CMAKE_CXX_FLAGS'] += ' -stdlib=libc++ -I' + ' -I'.join(self.deps_cpp_info['llvm'].include_paths)
            cmake.definitions['CMAKE_INSTALL_NAME_DIR'] = '@rpath'
            cmake.definitions['CMAKE_INSTALL_PREFIX'] = '%s/../%s' % (os.getcwd(), self.install_dir)
            if platform.system() == 'Darwin':
                cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64;arm64'
                cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.11'
                cmake.definitions['CMAKE_OSX_SYSROOT'] = self.deps_cpp_info['macos-sdk'].rootpath

            cmake.configure(source_dir='../%s' % self.source_dir,
                            build_dir='.')
            cmake.build()
            cmake.install()

    def package(self):
        import VuoUtils
        with tools.chdir('%s/lib' % self.install_dir):
            VuoUtils.fixLibs(self.libs, self.deps_cpp_info)
            shutil.move('libassimp.dylib', 'liboai.dylib')
            self.run('install_name_tool -id @rpath/liboai.dylib liboai.dylib')

        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        self.copy('*.h', src='%s/include' % self.install_dir, dst='include')
        self.copy('*.inl', src='%s/include' % self.install_dir, dst='include')
        self.copy('libIrrXML.%s' % libext, src='%s/lib' % self.install_dir, dst='lib')
        self.copy('liboai.%s' % libext, src='%s/lib' % self.install_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['oai']
        self.cpp_info.includedirs = ['include', 'include/assimp']
