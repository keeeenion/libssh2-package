import mama
import os
from mama.utils.gnu_project import BuildProduct

# Explore Mama docs at https://github.com/RedFox20/Mama
class libssh2(mama.BuildTarget):

    local_workspace = 'packages'

    def init(self):
        # libgpg-error-1.47.tar.bz2
        self.libgpg_error = self.gnu_project('libgpg-error', '1.40',
            url='https://kratt.codefox.ee/linux/{{project}}.tar.bz2',
            build_products=[
                BuildProduct('{{installed}}/lib/libgpg-error.a', None),
            ])

        # libgcrypt-1.10.3.tar.bz2
        self.gcrypt = self.gnu_project('libgcrypt', '1.10.3',
            url='https://kratt.codefox.ee/linux/{{project}}.tar.bz2',
            build_products=[
                BuildProduct('{{installed}}/lib/libgcrypt.a', None),
            ])

    def settings(self):
        self.config.prefer_gcc(self.name)
        if self.mips:
            self.config.set_mips_toolchain('mipsel')

    def dependencies(self):
        self.add_git('zlib', 'https://github.com/RedFox20/zlib-package.git')

    def configure(self):
        if self.libgpg_error.should_build():
            self.libgpg_error.build('--enable-static --disable-shared --disable-tests '
                                   +'--disable-doc --disable-languages --with-pic')

        gpg_err = self.libgpg_error.install_dir()

        if self.gcrypt.should_build():
            self.gcrypt.build(f'--without-libgpg-error --with-libgpg-error-prefix={gpg_err} '
                              +'--disable-noexecstack --disable-doc --with-pic '
                              +'--enable-static --disable-shared ')

        zlib = self.find_target('zlib')
        zlib_inc = zlib.exported_includes[0]
        zlib_lib = zlib.exported_libs[0]
        gcrypt = self.gcrypt.install_dir()
        self.add_cmake_options('WITH_SERVER=OFF', 
                               'WITH_GSSAPI=OFF',
                               'WITH_EXAMPLES=OFF',
                               'UNIT_TESTING=OFF',
                               'WITH_NACL=OFF',
                               'BUILD_SHARED_LIBS=OFF',
                               f'WITH_GCRYPT=ON',
                               f'GCRYPT_LIBRARIES={gcrypt}/lib/libgcrypt.a',
                               f'GCRYPT_INCLUDE_DIR={gcrypt}/include',
                               f'GPGERR_INCLUDE_DIR={gpg_err}/include',
                               f'ZLIB_INCLUDE_DIR={zlib_inc}',
                               f'ZLIB_LIBRARY={zlib_lib}')

    def package(self):
        self.export_include('include', build_dir=True)
        self.export_lib('lib/libssh2.a', build_dir=True)
        self.export_lib(self.gcrypt.install_dir('lib/libgcrypt.a'))
        self.export_lib(self.libgpg_error.install_dir('lib/libgpg-error.a'))