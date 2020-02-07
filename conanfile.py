from conans import ConanFile, CMake, tools


class ZlibConan(ConanFile):
    name = "zlib"
    version = "1.2.11"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "https://github.com/elear-solutions/zlib"
    description = "This recipe file used to build and package binaries of zlib repository"
    topics = ("compression", "data")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "minizip": [True, False]
    }
    default_options = {key: False for key in options.keys()}
    default_options ["fPIC"] = True
    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        self._build_zlib()
        cmake = CMake(self)
        cmake.configure(source_folder=".")
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*.h", dst="include", src="package/include")
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", src="package/lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", src="package/lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = [ "z" ]

    def _build_zlib(self):
        # https://github.com/madler/zlib/issues/268
        try:
            tools.replace_in_file('../gzguts.h','#if defined(_WIN32) || defined(__CYGWIN__)','#if defined(_WIN32) || defined(__MINGW32__)')
            if self.settings.os == "iOS":
                tools.replace_in_file("../gzguts.h", '#ifdef _LARGEFILE64_SOURCE','#include <unistd.h>\n\n#ifdef _LARGEFILE64_SOURCE')
            for filename in ['../zconf.h', '../zconf.h.cmakein', '../zconf.h.in']:
                tools.replace_in_file(filename,'#ifdef HAVE_UNISTD_H    ''/* may be set to #if 1 by ./configure */','#if defined(HAVE_UNISTD_H) && (1-HAVE_UNISTD_H-1 != 0)')
                tools.replace_in_file(filename,'#ifdef HAVE_STDARG_H    ''/* may be set to #if 1 by ./configure */','#if defined(HAVE_STDARG_H) && (1-HAVE_STDARG_H-1 != 0)')
        except:
            self.output.info("already replaced")
