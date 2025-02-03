// Copyright (c) 2024, ahmed.g.abdin and contributors
// For license information, please see license.txt

const VehicleStatus = {
    SERVICED: "Serviced",
    NOTIFIED: "Notified",
    IN_GARAGE: "In Garage",
    UNCHECKED: "Unchecked",
};
const OwnershipStatus = {
    LTO: "LTO",
    Rental: "Rental",
};

const calcTotal = (frm) => {
    const visits_total = frm.doc.visits.reduce((sum, visit) => sum + visit.total, 0)
    const quotations_total = frm.doc.quotations.reduce((sum, quo) => sum + quo.total, 0)
    frm.set_value('total', visits_total + quotations_total)
}

// const populateQuotations = (frm) => {
//     console.log("populateQuotations ")
//     frappe.call({
//         method: "frappe.client.get_list",
//         args: {
//             doctype: "Quotation",
//             filters: [
//                 ["custom_vehicle", "=", frm.doc.name],
//             ],
//             fields: ["name", "custom_vehicle", "grand_total", "creation", "status", "workflow_state"],
//             order_by: "creation desc",
//         },
//         callback: function(res) {
//             if (res.message) {
//                 const quotations = res.message;
//                 console.log(quotations)
//                 const isDifferent = areItemsDifferent(frm.doc.quotations, quotations)
//                 if (isDifferent) {
//                     frm.clear_table("quotations");
//                     let total = 0
//                     quotations.forEach(quot => {
//                         let child = frm.add_child("quotations");
//                         child.quotation = quot.name;
//                         child.vehicle = quot.custom_vehicle;
//                         child.total = quot.grand_total;
//                         child.status = quot.status;
//                         total += quot.grand_total;
//                     });
//                     //frm.set_value('last_quotation_status', quotations[0].workflow_state)
//                     console.log(quotations)
//                     frm.set_value('total', total)
//                     frm.refresh_field("quotations");
//                 }
//             } else {
//                 frm.clear_table("quotations");
//                 frm.refresh_field("quotations");
//             }
//         }
//     });
// }

function areItemsDifferent(currentItems = [], newItems = []) {
    if (newItems.length !== currentItems.length) {
        return true;
    }
    for (let i = 0; i < newItems.length; i++) {
        const retrievedItem = newItems[i];
        const currentItem = currentItems[i];
        if (
            retrievedItem.name !== currentItem.quotation ||
            retrievedItem.grand_total !== currentItem.total ||
            retrievedItem.custom_vehicle !== currentItem.vehicle ||
            retrievedItem.status !== currentItem.status
        ) {
            console.log({ retrievedItem, currentItem })
            return true;
        }
    }
    return false;
}

frappe.ui.form.on("Vehicle KA", {
    ownership_type(frm) {
        toggleLTODoc(frm)
    },
    onload(frm) {
        toggleLTODoc(frm)
        toggleClosestRemindingDate(frm)
        translateState(frm);
        reorderChildTable(frm);
        // populateQuotations(frm);
        // calcTotal(frm)
    },
    refresh(frm) {
        // Custom buttons in groups
        // frm.add_custom_button("Test", () => {
        //     console.log("HI");
        //     someFuntion();
        // });
        reorderChildTable(frm);
        // calcTotal(frm)
    },
    before_save(frm) {
        validateLTODoc(frm)
    }
});

const toggleLTODoc = (frm) => {
    if (frm.doc.ownership_type == OwnershipStatus.LTO) {
        frm.toggle_display("lto_doc", true);
    } else {
        frm.toggle_display("lto_doc", false);
    }
}

const toggleClosestRemindingDate = (frm) => {
    if (frm.doc.state == VehicleStatus.IN_GARAGE)
        frm.toggle_display("closest_reminding_date", true)
    else
        frm.toggle_display("closest_reminding_date", false)
}

const validateLTODoc = (frm) => {
    if (frm.doc.ownership_type == OwnershipStatus.LTO && !frm.doc.lto_doc) {
        // frm.set_value("ownership_type", OwnershipStatus.Rental)
        // frm.save()
        frappe.throw({
            title: __("Missing LTO Document"),
            message: __("Attach the LTO Document in order to save Ownership Type as LTO"),
        });
    }
}

const reorderQuotationsTable = (frm) => {
    let child_table_data = frm.doc.quotations;
    child_table_data.sort((a, b) =>
        b.creation.localeCompare(a.creation)
    );
    child_table_data.forEach((item, index) => {
        item.idx = index + 1;
    });
    frm.refresh_field("quotations");
};
const reorderChildTable = (frm) => {
    let child_table_data = frm.doc.visits;
    child_table_data.sort((a, b) =>
        b.maintenance_date.localeCompare(a.maintenance_date)
    );
    child_table_data.forEach((item, index) => {
        item.idx = index + 1;
    });
    frm.refresh_field("visits");
};

const someFuntion = () => { };

/**
 * called
 * need_visit
 * visited
 * visit_late
 */
const translateState = (frm) => {
    const state = frm.doc.state;
    switch (state) {
        case VehicleStatus.SERVICED:
            frm.set_value("called", "Yes");
            // frm.set_value("need_visit", "Yes");
            frm.set_value("visited", "Yes");
            // frm.set_value("visit_late", "No");
            break;
        // case VehicleStatus.OVERDUE:
        //     frm.set_value("called", "Yes");
        //     frm.set_value("need_visit", "Yes");
        //     frm.set_value("visited", "Yes");
        //     frm.set_value("visit_late", "Yes");
        //     break;
        case VehicleStatus.NOTIFIED:
            frm.set_value("called", "Yes");
            frm.set_value("need_visit", "Yes");
            frm.set_value("visited", "No");
            frm.set_value("visit_late", "No");
            break;
        // case VehicleStatus.EARLY_NOTIFIED:
        //     frm.set_value("called", "Yes");
        //     frm.set_value("need_visit", "No");
        //     frm.set_value("visited", "No");
        //     frm.set_value("visit_late", "No");
        //     break;
        // case VehicleStatus.PENDING_APPROVAL:
        //     frm.set_value("called", "Yes");
        //     frm.set_value("need_visit", "Yes");
        //     frm.set_value("visited", "Yes");
        //     frm.set_value("visit_late", "No");
        //     break;
        case VehicleStatus.UNCHECKED:
        case VehicleStatus.UPCOMING:
            frm.set_value("called", "No");
            // frm.set_value("need_visit", "No");
            frm.set_value("visited", "No");
            // frm.set_value("visit_late", "No");
            break;
    }
    // frm.save();
};
