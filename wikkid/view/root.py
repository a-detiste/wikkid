#
# Copyright (C) 2010 Wikkid Developers
#
# This software is licensed under the GNU Affero General Public License
# version 3 (see the file LICENSE).

"""View classes for the wiki root."""

from twisted.web.util import redirectTo

from wikkid.interface.resource import IRootResource
from wikkid.view.base import BaseView


class RootPage(BaseView):
    """The default view for the root page redirects to the home page."""

    for_interface = IRootResource
    name = 'view'
    is_default = True

    def _render(self, skin):
        """Redirect to Home (or the default page)."""
        preferred = self.context.preferred_path
        return redirectTo(preferred, self.request)