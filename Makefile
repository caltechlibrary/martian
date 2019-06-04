# =============================================================================
# @file    Makefile
# @brief   Makefile for some steps in creating a Martian application
# @author  Michael Hucka
# @date    2018-09-13
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/martian
# =============================================================================

# Variables.

release	   := $(shell egrep 'version.*=' martian/__version__.py | awk '{print $$3}' | tr -d "'")
platform   := $(shell python3 -c 'import sys; print(sys.platform)')
distro	   := $(shell python3 -c 'import platform; print(platform.dist()[0].lower())')
linux_vers := $(shell python3 -c 'import platform; print(platform.dist()[1].lower())' | cut -f1-2 -d'.')
macos_vers := $(shell sw_vers -productVersion 2>/dev/null | cut -f1-2 -d'.' || true)
github-css := dev/github-css/github-markdown-css.html

about-file := ABOUT.html
help-file  := martian/data/help.html

# Main build targets.

build: | dependencies build-$(platform)

# Platform-specific instructions.

build-darwin: dist/Martian.app $(about-file) $(help-file) # NEWS.html
#	packagesbuild dev/installer-builders/macos/packages-config/Martian.pkgproj
#	mv dist/Martian-mac.pkg dist/Martian-$(release)-macos-$(macos_vers).pkg 

build-linux: dist/martian
	(cd dist; tar czf Martian-$(release)-$(distro)-$(linux_vers).tar.gz martian)

dist/Martian.app:
	pyinstaller --clean pyinstaller-$(platform).spec
	sed -i '' -e 's/0.0.0/$(release)/' dist/Martian.app/Contents/Info.plist
	rm -f dist/Martian.app/Contents/Info.plist.bak
	rm -f dist/martian

dist/martian dist/Martian.exe:
	pyinstaller --clean pyinstaller-$(platform).spec

dependencies:;
	pip3 install -r requirements.txt

# Component files placed in the installers.

$(about-file): README.md
	pandoc --standalone --quiet -f gfm -H $(github-css) -o README.html README.md
	inliner -n < README.html > ABOUT.html
	rm -f README.html

$(help-file): martian/data/help.md
	pandoc --standalone --quiet -f gfm -H $(github-css) -o help-tmp.html $<
	inliner -n < help-tmp.html > $@
	rm -f help-tmp.html

NEWS.html: NEWS.md
	pandoc --standalone --quiet -f gfm -H $(github-css) -o NEWS.html NEWS.md
	inliner -n < NEWS.html > NEWS-inlined.html
	mv NEWS-inlined.html NEWS.html

# Miscellaneous directives.

clean: clean-dist clean-html

clean-dist:;
	-rm -fr dist/Martian.app dist/martian dist/martian.exe build

clean-html:;
	-rm -fr ABOUT.html NEWS.html

.PHONY: html clean clean-dist clean-html
