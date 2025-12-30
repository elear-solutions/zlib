import os
import shutil
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
    _modified_files_backup = {}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        self._build_zlib()
        cmake = CMake(self)
        cmake.configure(source_folder=".")
        cmake.build()
        cmake.install()
        self._restore_modified_files()

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
        # Get source directory where conanfile is located
        source_dir = os.path.dirname(os.path.abspath(__file__))
        
        files_to_modify = ['gzguts.h', 'zconf.h', 'zconf.h.cmakein', 'zconf.h.in']
        
        # Backup files before modifying
        for filename in files_to_modify:
            filepath = os.path.join(source_dir, filename)
            if os.path.isfile(filepath) and filename not in self._modified_files_backup:
                backup_path = filepath + ".conan_backup"
                # If backup exists from previous crashed build, restore first
                if os.path.isfile(backup_path):
                    shutil.copy2(backup_path, filepath)
                    self.output.info("Restored %s from previous backup" % filename)
                # Create new backup
                shutil.copy2(filepath, backup_path)
                self._modified_files_backup[filename] = backup_path
                self.output.info("Backed up %s" % filename)
        
        try:
            gzguts_path = os.path.join(source_dir, 'gzguts.h')
            tools.replace_in_file(gzguts_path, '#if defined(_WIN32) || defined(__CYGWIN__)', 
                                  '#if defined(_WIN32) || defined(__MINGW32__)')
            if self.settings.os == "iOS":
                tools.replace_in_file(gzguts_path, '#ifdef _LARGEFILE64_SOURCE',
                                      '#include <unistd.h>\n\n#ifdef _LARGEFILE64_SOURCE')
            for filename in ['zconf.h', 'zconf.h.cmakein', 'zconf.h.in']:
                filepath = os.path.join(source_dir, filename)
                if os.path.isfile(filepath):
                    tools.replace_in_file(filepath, '#ifdef HAVE_UNISTD_H    ''/* may be set to #if 1 by ./configure */',
                                          '#if defined(HAVE_UNISTD_H) && (1-HAVE_UNISTD_H-1 != 0)')
                    tools.replace_in_file(filepath, '#ifdef HAVE_STDARG_H    ''/* may be set to #if 1 by ./configure */',
                                          '#if defined(HAVE_STDARG_H) && (1-HAVE_STDARG_H-1 != 0)')
        except Exception as e:
            self.output.info("File modifications failed or already applied: %s" % str(e))

    def _restore_modified_files(self):
        """Restore modified files from backup after build completes"""
        source_dir = os.path.dirname(os.path.abspath(__file__))
        for filename, backup_path in self._modified_files_backup.items():
            filepath = os.path.join(source_dir, filename)
            if os.path.isfile(backup_path):
                shutil.copy2(backup_path, filepath)
                os.remove(backup_path)
                self.output.info("Restored %s from backup" % filename)
        self._modified_files_backup.clear()
