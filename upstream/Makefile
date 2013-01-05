VERSION=$(shell awk '/Version/ { print $$2 }' generic-release.spec)

CVSROOT = $(shell cat CVS/Root 2>/dev/null || :)

CVSTAG = V$(subst .,-,$(VERSION))

all:

tag-archive:
	@cvs -Q tag -F $(CVSTAG)

create-archive:
	@rm -rf /tmp/fedora-release
	@cd /tmp ; cvs -Q -d $(CVSROOT) export -r$(CVSTAG) generic-release || echo "Um... export aborted."
	@mv /tmp/generic-release /tmp/generic-release-$(VERSION)
	@cd /tmp ; tar -czSpf generic-release-$(VERSION).tar.gz generic-release-$(VERSION)
	@rm -rf /tmp/generic-release-$(VERSION)
	@cp /tmp/generic-release-$(VERSION).tar.gz .
	@rm -f /tmp/generic-release-$(VERSION).tar.gz
	@echo ""
	@echo "The final archive is in generic-release-$(VERSION).tar.gz"

archive: tag-archive create-archive
