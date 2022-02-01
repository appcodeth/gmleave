odoo.define('gmleave_report.report_home', function (require) {
  "use strict";

  var AbstractAction = require('web.AbstractAction');
  var core = require('web.core');

  var LeaveReportAction = AbstractAction.extend({
    template: 'LeaveReport',
    xmlDependencies: ['/gmleave_report/static/src/xml/leaveReport.xml'],
  });

  var LeaveWaitingReportAction = AbstractAction.extend({
    template: 'LeaveWaitingReport',
    xmlDependencies: ['/gmleave_report/static/src/xml/leaveWaitingReport.xml'],
  });

  var LeaveUsageReportAction = AbstractAction.extend({
    template: 'LeaveUsageReport',
    xmlDependencies: ['/gmleave_report/static/src/xml/leaveUsageReport.xml'],
  });

  var LeaveTopRankReportAction = AbstractAction.extend({
    template: 'LeaveTopRankReport',
    xmlDependencies: ['/gmleave_report/static/src/xml/leaveTopRankReport.xml'],
  });

  var LeaveHolidayReportAction = AbstractAction.extend({
    template: 'LeaveHolidayReport',
    xmlDependencies: ['/gmleave_report/static/src/xml/leaveHolidayReport.xml'],
  });

  core.action_registry.add('gmleave_leave_report', LeaveReportAction);
  core.action_registry.add('gmleave_leave_waiting_report', LeaveWaitingReportAction);
  core.action_registry.add('gmleave_leave_usage_report', LeaveUsageReportAction);
  core.action_registry.add('gmleave_leave_toprank_report', LeaveTopRankReportAction);
  core.action_registry.add('gmleave_leave_holiday_report', LeaveHolidayReportAction);

  return {
    LeaveReportAction: LeaveReportAction,
    LeaveWaitingReportAction: LeaveWaitingReportAction,
    LeaveUsageReportAction: LeaveUsageReportAction,
    LeaveTopRankReportAction: LeaveTopRankReportAction,
    LeaveHolidayReportAction: LeaveHolidayReportAction,
  }
});
