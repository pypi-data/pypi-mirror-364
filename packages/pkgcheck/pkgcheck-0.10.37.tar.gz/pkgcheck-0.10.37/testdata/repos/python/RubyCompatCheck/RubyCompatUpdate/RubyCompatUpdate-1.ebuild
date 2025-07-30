EAPI=7

USE_RUBY="ruby27 ruby30 ruby31"
inherit ruby-ng

DESCRIPTION="Ebuild with potential USE_RUBY updates"
HOMEPAGE="https://github.com/pkgcore/pkgcheck"
LICENSE="BSD"
SLOT="0"

RDEPEND="
	stub/stub2
"

ruby_add_depend "
	stub/ruby-dep
"
