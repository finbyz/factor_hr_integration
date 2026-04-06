// Copyright (c) 2026, Finbyz Tech Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('FactoHR Settings', {
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			// Add Sync Now button
			frm.add_custom_button(__('Sync Now'), function() {
				frappe.call({
					method: 'sync_employees',
					doc: frm.doc,
					freeze: true,
					freeze_message: __('Syncing employees from FactoHR...'),
					callback: function(r) {
						if (r.message) {
							frappe.msgprint({
								title: __('Sync Complete'),
								indicator: 'green',
								message: __('Total: {0}, Created: {1}, Updated: {2}, Failed: {3}',
									[r.message.total, r.message.created, r.message.updated, r.message.failed])
							});
							frm.reload_doc();
						}
					}
				});
			}).addClass('btn-primary');

			// Add Test Connection button
			frm.add_custom_button(__('Test Connection'), function() {
				frappe.call({
					method: 'test_connection',
					doc: frm.doc,
					callback: function(r) {
						if (r.message && r.message.success) {
							frappe.msgprint({
								title: __('Success'),
								indicator: 'green',
								message: r.message.message
							});
						} else {
							frappe.msgprint({
								title: __('Failed'),
								indicator: 'red',
								message: r.message ? r.message.message : 'Connection failed'
							});
						}
					}
				});
			});
		}
	}
});

// Made with Bob
