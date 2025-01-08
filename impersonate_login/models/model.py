# Copyright (C) 2024 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.http import request


class BaseModel(models.AbstractModel):
    _inherit = "base"

    impersonated_create_uid = fields.Integer("Created by (impersonated)", readonly=True)

    @api.model
    def _create(self, data_list):
        res = super()._create(data_list)
        if (
            request
            and request.session.impersonate_from_uid
            and "create_uid" in self._fields
            and not self.env.context.get("do_not_impersonate", False)
        ):
            self.env.cr.execute(
                """
                UPDATE %(table)s
                SET create_uid = %(impersonator_id)s
                WHERE id IN %(record_ids)s
                """,
                {
                    "table": AsIs(self._table),
                    "impersonator_id": request.session.impersonate_from_uid,
                    "record_ids": tuple(rec.id for rec in res),
                },
            )

            # , impersonated_create_uid= % (impersonated_uid)s
            # "impersonated_uid": self.env.uid,
        return res

    def read(self, fields=None, load='_classic_read'):
        # if self._name == "grifoflex.order":
        #     import wdb; wdb.set_trace()
        if (
            request
            and request.session.impersonate_from_uid
        ):
            try:
                res = super().read(fields, load)
            except AccessError:
                new_self = self.sudo().with_context(do_not_impersonate=True).copy()
                new_self = new_self.with_user(self.env.uid)
                try:
                    super(BaseModel, new_self).read()
                except AccessError as inner_err:
                    raise inner_err
                finally:
                    new_self.sudo().unlink()
                res = super().with_user(request.session.impersonate_from_uid).read(fields, load)
        else:
            res = super().read(fields, load)
        return res

    def write(self, vals):
        res = super().write(vals)
        if (
            request
            and request.session.impersonate_from_uid
            and "write_uid" in self._fields
        ):
            self._fields["write_uid"].write(self, request.session.impersonate_from_uid)
        return res
