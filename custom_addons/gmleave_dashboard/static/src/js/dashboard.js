odoo.define('gmleave_dashboard.dashboard', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    var DashboardAction = AbstractAction.extend({
        template: 'DashboardOverview',
        xmlDependencies: ['/gmleave_dashboard/static/src/xml/dashboard.xml'],
        jsLibs: [
            '/gmleave_dashboard/static/src/vendor/moment/moment.min.js',
            '/gmleave_dashboard/static/src/vendor/daterangepicker/daterangepicker.min.js',
            '/gmleave_dashboard/static/src/vendor/highcharts/highcharts.js',
            '/gmleave_dashboard/static/src/vendor/highcharts/modules/exporting.js',
            '/gmleave_dashboard/static/src/vendor/highcharts/modules/export-data.js',
        ],
    });

    var HomeAction = AbstractAction.extend({
        template: 'HomeOverview',
        xmlDependencies: ['/gmleave_dashboard/static/src/xml/home.xml'],
    });

    core.action_registry.add('dashboard_overview', DashboardAction);
    core.action_registry.add('home_overview', HomeAction);
    return {};
});
