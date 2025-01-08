from psycopg2.extensions import AsIs

from odoo import api, models
from odoo.exceptions import AccessError
from odoo.http import request


class ImpersonateMixin(models.AbstractModel):
    _name = "impersonate.mixin"
    _description = "Mixin for Impersonation methods"

    def read(self, fields=None, load='_classic_read'):
        if (
            request
            and request.session.impersonate_from_uid
        ):
            try:
                res = super().read(fields, load)
            except AccessError:
                new_self = self.with_user(
                    request.session.impersonate_from_uid
                ).with_context(is_impersonated=True)
                try:
                    res = super(ImpersonateMixin, new_self).read()
                except AccessError as inner_err:
                    import wdb; wdb.set_trace()
                    raise inner_err
        else:
            res = super().read(fields, load)
        return res
