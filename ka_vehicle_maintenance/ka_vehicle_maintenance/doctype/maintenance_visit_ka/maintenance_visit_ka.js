// Copyright (c) 2024, ahmed.g.abdin and contributors
// For license information, please see license.txt
const VehicleStatus = {
    SERVICED: "Serviced",
    NOTIFIED: "Notified",
    UPCOMING: "Upcoming",
    UNCHECKED: "Unchecked",
}
const VehicleOwnershipType = {
    LTO: "LTO",
    RENTAL: "Rental"
}
const VehicleAvailabilityStatus = {
    IN_GARAGE: "In Garage",
    On_Road: "On Road",
    AVAILABLE: "Available"
}

const differanceBWMaintenanceAndRemindingDate = -1
const onIsNew = (frm) => (frm.is_new() &&
    frappe.msgprint({
        title: __('Please Save then Selece the Quotation'),
    })
)

const calcTotal = (frm) => {
    console.log("on maintenance_visit_items")
    if (!frm.doc.quotation) {
        const total = frm.doc.maintenance_visit_items.reduce((accumated, current) => {
            return accumated + (current.qty * current.rate)
        }, 0)
        total !== frm.doc.total && frm.set_value('total', total)
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
    },
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
    new_km(frm) {
        updateDistance(frm);
    },
    onload(frm) {
        translateState(frm);
        updateDistance(frm);
    },
    validate(frm) {
        const distance = frm.doc.distance
        if (distance < 0) {
            frappe.throw({
                title: __('Wrong KM'),
                message: __('Please Verifiy the distance it is less than the previse visit!'),
            })
        }
    },
    before_save(frm) {
        // if (!frm.doc.maintenance_date && frm.doc.reminding_date) {
        //     var date = frappe.datetime.add_days(frm.doc.reminding_date, 3);
        //     frm.set_value("maintenance_date", date);
        // }
        console.log("before_save")
        if (!frm.doc.reminding_date && frm.doc.maintenance_date) {
            var date = frappe.datetime.add_days(frm.doc.maintenance_date, differanceBWMaintenanceAndRemindingDate);
            frm.set_value("reminding_date", date);
        }
        console.log("done", frm.doc)
    },
    after_save(frm) {
        console.log("after_save")
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
    availability_status(frm) {
        console.log("before_submit")
        var new_km = frm.doc.new_km;
        if (!new_km || new_km == 0) {
            frappe.validated = false;
            frappe.throw({
                title: __("Missing New KM"),
                message: __("Please enter the new KM"),
            });
        }
        if (frm.ownership_type == VehicleOwnershipType.LTO) {
            prepareRentApplicationToClose(frm, {})
            return
        }
        switch (frm.doc.availability_status) {
            case VehicleAvailabilityStatus.IN_GARAGE:
                frappe.validated = false;
                frappe.prompt(
                    [{
                        label: __("Reminding Date"),
                        fieldname: "date",
                        fieldtype: "Date",
                    },
                    {
                        label: __("New Assigned Vehicle"),
                        fieldname: "vehicle",
                        fieldtype: "Link",
                        options: "Vehicle KA",
                        filters: {
                            "availability_status": VehicleAvailabilityStatus.AVAILABLE
                        }
                    }],
                    (values) => {
                        if (!values.date)
                            frappe.throw({
                                title: __("Missing Next Reminding Date"),
                                message: __(
                                    "Please enter the next reminding date"
                                ),
                            });
                        if (!values.vehicle)
                            frappe.throw({
                                title: __("Missing New Assigned Vehicle"),
                                message: __(
                                    "Please enter the new assigned vehicle"
                                ),
                            });
                        frm.next_reminding_date = values.date
                        createNewMV(frm, values.date);
                        rentApplicationPreparedToClose = prepareRentApplicationToClose(frm, values);
                        if (!frm.doc.submitted_at)
                            frm.doc.submitted_at = frm.doc.modified;
                        console.log({
                            rentApplicationPreparedToClose,
                        })
                        if (rentApplicationPreparedToClose)
                            frm.save("Submit");
                    },
                    __("Next Reminding Date"),
                    __("Create")
                );
                break;
            case VehicleAvailabilityStatus.AVAILABLE:
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
                        frm.next_reminding_date = values.date
                        createNewMV(frm, values.date);
                        prentApplicationPreparedToClose = prepareRentApplicationToClose(frm, {});
                        if (!frm.doc.submitted_at)
                            frm.doc.submitted_at = frm.doc.modified;
                        if (rentApplicationPreparedToClose)
                            frm.save("Submit");
                    },
                    __("Next Reminding Date"),
                    __("Create")
                );
                break;
        }
        if (frm.doc.avalibility_status == VehicleAvailabilityStatus.On_Road)
            switch (frm.doc.state) {
                case VehicleStatus.PENDING_APPROVAL:
                case VehicleStatus.UNCHECKED:
                case VehicleStatus.UPCOMING:
                case VehicleStatus.UNUSED:
                    // Prevent the default submit action
                    frappe.throw({
                        title: __("Unvalid State"),
                        message: __("You can not submit document in this State"),
                    });
                    break;

                case VehicleStatus.SERVICED:
                case VehicleStatus.OVERDUE:
                    if (!frm.doc.attachment) {
                        // Prevent the default submit action
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
                            frm.next_reminding_date = values.date
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
    });
};
const prepareRentApplicationToClose = (frm, values) => {
    frappe.call({
        method: "ka_vehicle_maintenance.events.prepare_rent_application_to_close",
        args: {
            doc: frm.doc,
            values: values,
        },
        callback: ({ message }) => {
            console.log("rentApplicationPreparedToClose", message);
        },
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
            frm.set_value("visited", "Yes");
            break;
        case VehicleStatus.OVERDUE:
            frm.set_value("called", "Yes");
            frm.set_value("visited", "Yes");
            break;
        case VehicleStatus.NOTIFIED:
            frm.set_value("called", "Yes");
            frm.set_value("visited", "No");
            break;
        case VehicleStatus.UNCHECKED:
        case VehicleStatus.UPCOMING:
            frm.set_value("called", "No");
            frm.set_value("visited", "No");
            break;
    }
};

const determineState = (frm) => {
    if (frm.doc.docstatus === 1) return;
    const called = frm.doc.called;
    const visited = frm.doc.visited;

    if (
        called === "Yes" &&
        visited === "Yes"
    ) {
        frm.set_value("state", VehicleStatus.SERVICED);
    } else if (
        called === "Yes" &&
        visited === "No"
    ) {
        frm.set_value("state", VehicleStatus.NOTIFIED);
    } else if (
        called === "No" &&
        visited === "No"
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
