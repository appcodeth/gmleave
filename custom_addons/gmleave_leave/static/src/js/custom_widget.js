odoo.define('gmleave_leave.custom_widget', function (require) {
    var AbstractField = require('web.AbstractField');
    var registry = require('web.field_registry');

    var LabelStatusWidget = AbstractField.extend({
        _render: function () {
            var cssClass = 'status-default';
            if (this.value === 'approve') {
                cssClass = 'status-success';
            } else if (this.value === 'draft') {
                cssClass = 'status-warning';
            } else if (this.value === 'cancel' || this.value === 'refuse') {
                cssClass = 'status-danger';
            }

            var labelText = '';
            if(this.value == 'draft') {
                labelText = 'รออนุมัติ';
            } else if(this.value == 'approve') {
                labelText = 'อนุมัติ';
            } else if(this.value == 'refuse') {
                labelText = 'ไม่อนุมัติ';
            } else if(this.value == 'cancel') {
                labelText = 'ยกเลิก';
            }

            this.$el.html('<span class="' + cssClass + '">' + labelText + '</span>');
        }
    });

    registry.add('labelstatus', LabelStatusWidget)
    return {
        LabelStatusWidget: LabelStatusWidget,
    }
});

