// Copyright (c) 2024, ahmed.g.abdin and contributors
// For license information, please see license.txt
const VehicleStatus = {
    UNUSED: "Unused",
    SERVICED: "Serviced",
    OVERDUE: "Overdue",

    NOTIFIED: "Notified",
    EARLY_NOTIFIED: "Early Notified",
    IN_GARAGE: "In Garage",

    PENDING_APPROVAL: "Pending Approval",

    UPCOMING: "Upcoming",
    UNCHECKED: "Unchecked",
};
const differanceBWMaintenanceAndRemindingDate = -1
const onIsNew = (frm) => (frm.is_new() &&
    frappe.msgprint({
        title: __('Please Save then Selece the Quotation'),
    })
)

const calcTotal = (frm) => {
    console.log("on maintenance_visit_items")
    if (!frm.doc.quotation && frm.doc.maintenance_visit_items.length > 0) {
        const total = frm.doc.maintenance_visit_items.reduce((accumated, current) => {
            return accumated + (current.qty * current.rate)
        }, 0)
        total > 0 && total !== frm.doc.total && frm.set_value('total', total)
    }
}

const onQuotation = (frm) => {
    console.log("onQuotation")
    if (frm.is_new()) { onIsNew(frm); return }
    if (frm.doc.quotation) {
        frm.set_df_property('maintenance_visit_items', 'read_only', 1);
        frm.refresh_field('maintenance_visit_items');
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Quotation",
                name: frm.doc.quotation
            },
            callback: function(r) {
                if (r.message) {
                    const quotation = r.message;
                    frm.clear_table("maintenance_visit_items");
                    quotation.items.forEach(item => {
                        let child = frm.add_child("maintenance_visit_items");
                        child.item = item.item_code;
                        child.qty = item.qty;
                        child.rate = item.rate;
                        child.vehicle = frm.doc.vehicle
                        child.maintenance_visit = frm.doc.name
                        child.quotation = frm.doc.quotation
                    });
                    frm.refresh_field("maintenance_visit_items");
                }
            }
        });
    } else {
        // maintenance_visit_items
        frm.clear_table("maintenance_visit_items");
        frm.set_df_property('maintenance_visit_items', 'read_only', 0);
        frm.refresh_field("maintenance_visit_items");
        // total
        frm.set_value('total', '')
    }
    console.log(frm.doc.maintenance_visit_items)
}

frappe.ui.form.on("Maintenance Visit Items", {
    item(frm) {
        calcTotal(frm)
    },
    rate(frm) {
        calcTotal(frm)
    },
    qty(frm) {
        calcTotal(frm)
    },
    maintenance_visit_items_add(frm, cdt, cdn) {
        if (frm.is_new()) { onIsNew(frm); return }
        let child = frappe.get_doc(cdt, cdn);
        child.vehicle = frm.doc.vehicle
        child.maintenance_visit = frm.doc.name
        frm.refresh_field("maintenance_visit_items")
    }
})

frappe.ui.form.on("Maintenance Visit KA", {
    state(frm) {
        translateState(frm);
    },
    called(frm) {
        determineState(frm);
    },
    visited(frm) {
        determineState(frm);
    },
    quotation(frm) {
        onQuotation(frm)
    },
    maintenance_visit_items(frm) {
        calcTotal(frm)
    },
    visit_late(frm) {
        // TODO: for test remove when done
        // frappe.call({
        //     method: "ka_vehicle_maintenance.whitelist.sendemail"
        //     , args: {
        //         "args": frm.doc.name
        //     }
        //     , callback: function (r) {
        //         if (r.message) {
        //             location.reload();
        //         }
        //     }
        // })
        // console.log("email sent");
        determineState(frm);
    },
    // need_visit(frm) {
    //     determineState(frm);
    // },
    new_km(frm) {
        updateDistance(frm);
    },
    onload(frm) {
        translateState(frm);
        updateDistance(frm);
    },
    before_save(frm) {
        // if (!frm.doc.maintenance_date && frm.doc.reminding_date) {
        //     var date = frappe.datetime.add_days(frm.doc.reminding_date, 3);
        //     frm.set_value("maintenance_date", date);
        // }
        if (!frm.doc.reminding_date && frm.doc.maintenance_date) {
            var date = frappe.datetime.add_days(frm.doc.maintenance_date, differanceBWMaintenanceAndRemindingDate);
            frm.set_value("reminding_date", date);
        }
    },
    after_save(frm) {
        if (frm.doc.docstatus == 0 && !frm.doc.checked_at) {
            switch (frm.doc.state) {
                case VehicleStatus.SERVICED:
                case VehicleStatus.OVERDUE:
                case VehicleStatus.NOTIFIED:
                case VehicleStatus.EARLY_NOTIFIED:
                case VehicleStatus.IN_GARAGE:
                    frm.doc.checked_at = frm.doc.modified;
                    break;
            }
        }
    },
    before_submit(frm) {
        var new_km = frm.doc.new_km;
        if (!new_km || new_km == 0) {
            frappe.validated = false;
            frappe.throw({
                title: __("Missing New KM"),
                message: __("Please enter the new KM"),
            });
        }
        switch (frm.doc.state) {
            case VehicleStatus.PENDING_APPROVAL:
            case VehicleStatus.UNCHECKED:
            case VehicleStatus.UPCOMING:
            case VehicleStatus.UNUSED:
                // Prevent the default submit action
                frappe.validated = false;
                frappe.throw({
                    title: __("Unvalid State"),
                    message: __("You can not submit document in this State"),
                });
                break;

            case VehicleStatus.SERVICED:
            case VehicleStatus.OVERDUE:
                if (!frm.doc.attachment) {
                    // Prevent the default submit action
                    frappe.validated = false;
                    frappe.throw({
                        title: __("Missing Attachment"),
                        message: __("Attach the Document in order to submit"),
                    });
                }
                const after_8_days = frappe.datetime.add_days(
                    frm.doc.maintenance_date,
                    8
                );
                createNewMV(frm, after_8_days);

                break;

            case VehicleStatus.NOTIFIED:
            case VehicleStatus.EARLY_NOTIFIED:
            case VehicleStatus.IN_GARAGE:
                // Prevent the default submit action
                frappe.validated = false;
                frappe.prompt(
                    {
                        label: __("Reminding Date"),
                        fieldname: "date",
                        fieldtype: "Date",
                    },
                    (values) => {
                        if (!values.date)
                            frappe.throw({
                                title: __("Missing Next Reminding Date"),
                                message: __(
                                    "Please enter the next reminding date"
                                ),
                            });
                        frm.set_value("next_reminding_date", values.date);
                        createNewMV(frm, values.date);
                        if (!frm.doc.submitted_at)
                            frm.doc.submitted_at = frm.doc.modified;
                        // save the doc
                        // frm.save_or_update();
                        frm.save("Submit");
                    },
                    __("Next Reminding Date"),
                    __("Create")
                );
                break;

            default:
                break;
        }
        if (!frm.doc.submitted_at) frm.doc.submitted_at = frm.doc.modified;
    },
});

const createNewMV = (frm, reminding_date) => {
    frappe.call({
        method: "ka_vehicle_maintenance.events.create_new_maintenance_visit",
        args: {
            doc: frm.doc,
            reminding_date: reminding_date,
        },
        // callback: ({ message }) => {
        //     console.log(message);
        // },
    });
};

/**
 * called
 * need_visit
 * visited
 * visit_late
 */
const translateState = (frm) => {
    if (frm.doc.docstatus === 1) return;
    const state = frm.doc.state;
    switch (state) {
        case VehicleStatus.SERVICED:
            frm.set_value("called", "Yes");
            // frm.set_value("need_visit", "Yes");
            frm.set_value("visited", "Yes");
            frm.set_value("visit_late", "No");
            break;
        case VehicleStatus.OVERDUE:
            frm.set_value("called", "Yes");
            // frm.set_value("need_visit", "Yes");
            frm.set_value("visited", "Yes");
            frm.set_value("visit_late", "Yes");
            break;
        case VehicleStatus.NOTIFIED:
            frm.set_value("called", "Yes");
            // frm.set_value("need_visit", "Yes");
            frm.set_value("visited", "No");
            frm.set_value("visit_late", "No");
            break;
        case VehicleStatus.EARLY_NOTIFIED:
            frm.set_value("called", "Yes");
            // frm.set_value("need_visit", "No");
            frm.set_value("visited", "No");
            frm.set_value("visit_late", "No");
            break;
        case VehicleStatus.PENDING_APPROVAL:
            frm.set_value("called", "Yes");
            // frm.set_value("need_visit", "Yes");
            frm.set_value("visited", "Yes");
            frm.set_value("visit_late", "No");
            break;
        case VehicleStatus.UNCHECKED:
        case VehicleStatus.UPCOMING:
        case VehicleStatus.UNUSED:
            frm.set_value("called", "No");
            // frm.set_value("need_visit", "No");
            frm.set_value("visited", "No");
            frm.set_value("visit_late", "No");
            break;
    }
};

const determineState = (frm) => {
    if (frm.doc.docstatus === 1) return;
    const called = frm.doc.called;
    // const need_visit = frm.doc.need_visit;
    const visited = frm.doc.visited;
    const visit_late = frm.doc.visit_late;

    // allow write only if yes based on order
    // if (called === "No") {
    // frm.set_df_property("need_visit", "read_only", 1);
    //     frm.set_df_property("visited", "read_only", 1);
    //     frm.set_df_property("visit_late", "read_only", 1);
    // } else {
    // frm.set_df_property("need_visit", "read_only", 0);
    //     frm.set_df_property("visited", "read_only", 0);
    //     frm.set_df_property("visit_late", "read_only", 0);
    // }
    // if (need_visit === "No") {
    //     frm.set_df_property("visited", "read_only", 1);
    //     frm.set_df_property("visit_late", "read_only", 1);
    // } else {
    //     frm.set_df_property("visited", "read_only", 0);
    //     frm.set_df_property("visit_late", "read_only", 0);
    // }
    // if (visited === "No") {
    //     frm.set_df_property("visit_late", "read_only", 1);
    // } else {
    //     frm.set_df_property("visit_late", "read_only", 0);
    // }

    if (
        called === "Yes" &&
        // need_visit === "Yes" &&
        visited === "Yes" &&
        visit_late === "No"
    ) {
        frm.set_value("state", VehicleStatus.SERVICED);
    } else if (
        called === "Yes" &&
        // need_visit === "Yes" &&
        visited === "Yes" &&
        visit_late === "Yes"
    ) {
        frm.set_value("state", VehicleStatus.OVERDUE);
    } else if (
        called === "Yes" &&
        // need_visit === "Yes" &&
        visited === "No" &&
        visit_late === "No"
    ) {
        frm.set_value("state", VehicleStatus.NOTIFIED);
    } else if (
        called === "Yes" &&
        // need_visit === "No" &&
        visited === "No" &&
        visit_late === "No"
    ) {
        frm.set_value("state", VehicleStatus.EARLY_NOTIFIED);
    } else if (
        called === "Yes" &&
        // need_visit === "Yes" &&
        visited === "Yes" &&
        visit_late === "No"
    ) {
        frm.set_value("state", VehicleStatus.PENDING_APPROVAL);
    } else if (
        called === "No" &&
        // need_visit === "No" &&
        visited === "No" &&
        visit_late === "No"
    ) {
        frm.set_value("state", VehicleStatus.UNCHECKED); // Or UNCHECKED, depending on the logic
    }
};

const updateDistance = (frm) => {
    if (frm.doc.docstatus === 1) return;
    const last_km = frm.doc.last_km;
    const new_km = frm.doc.new_km;
    if (last_km && new_km) {
        const distance = frm.doc.new_km - frm.doc.last_km;
        frm.set_value("distance", distance);
    } else if ((!last_km || last_km == 0) && new_km) {
        frm.set_value("distance", new_km);
    }
    else frm.set_value("distance", 0);
};
