odoo.define('gmleave_theme.WebClient', function (require) {
    "use strict";
    var AbstractWebClient = require('web.AbstractWebClient');
    AbstractWebClient = AbstractWebClient.include({
        start: function (parent) {
            this.set('title_part', {"zopenerp": "GM-Leave"});
            this._super(parent);
        },
    });
});
