import frappe


def company_wise_v(user):
    # Check if the user has permission for a specific company
    company_permissions = frappe.db.get_all(
        "User Permission",
        filters={"user": user, "allow": "Company"},
        fields=["user", "for_value"],
    )
    companies = [permission["for_value"] for permission in company_permissions]
    print("\n\n\n")
    companies_str = "', '".join(companies)
    print(companies)
    if len(companies) > 0:
        companies_str = "', '".join(companies)
        return f"(`tabVehicle KA`.company IN ('{companies_str}'))"
    return ""


def company_wise_vv(user):
    company_permissions = frappe.db.get_all(
        "User Permission",
        filters={"user": user, "allow": "Company"},
        fields=["user", "for_value"],
    )
    companies = [permission["for_value"] for permission in company_permissions]
    companies_str = "', '".join(companies)
    if len(companies) > 0:
        companies_str = "', '".join(companies)
        return f"(`tabVehicle Visit KA`.company IN ('{companies_str}'))"
    return ""


def company_wise_mv(user):
    # Check if the user has permission for a specific company
    company_permissions = frappe.db.get_all(
        "User Permission",
        filters={"user": user, "allow": "Company"},
        fields=["user", "for_value"],
    )
    companies = [permission["for_value"] for permission in company_permissions]
    companies_str = "', '".join(companies)
    if len(companies) > 0:
        companies_str = "', '".join(companies)
        return f"(`tabMaintenance Visit KA`.company IN ('{companies_str}'))"
    return ""


#  bench execute ka_vehicle_maintenance.permissions.update_company
def update_company():
    company = "Key Arabia"

    doctype = "Vehicle KA"
    docs = frappe.get_all(
        doctype, filters={"company": ["is", "not set"]}, fields=["name"]
    )
    for doc in docs:
        frappe.db.set_value(
            doctype, doc.name, "company", company, update_modified=False
        )
    frappe.db.commit()
    print(f"Updated {doctype} {len(docs)} records with company '{company}'")
    ###

    doctype = "Vehicle Visit KA"
    docs = frappe.get_all(
        doctype, filters={"company": ["is", "not set"]}, fields=["name"]
    )
    for doc in docs:
        frappe.db.set_value(
            doctype, doc.name, "company", company, update_modified=False
        )
    frappe.db.commit()
    print(f"Updated {doctype} {len(docs)} records with company '{company}'")
    ###

    doctype = "Maintenance Visit KA"
    docs = frappe.get_all(
        doctype, filters={"company": ["is", "not set"]}, fields=["name"]
    )
    for doc in docs:
        frappe.db.set_value(
            doctype, doc.name, "company", company, update_modified=False
        )
    frappe.db.commit()
    print(f"Updated {doctype} {len(docs)} records with company '{company}'")
