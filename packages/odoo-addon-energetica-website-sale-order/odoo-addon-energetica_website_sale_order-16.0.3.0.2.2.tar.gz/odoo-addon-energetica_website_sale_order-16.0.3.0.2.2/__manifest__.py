{
    "name": "Contract generation",
    "version": "16.0.3.0.2",
    "depends": [
        "base_rest",
        "portal",
        "sale",
        "web",
        "website",
    ],
    "author": "Coopdevs Treball SCCL",
    "category": "Sale Order",
    "website": "https://coopdevs.org",
    "license": "AGPL-3",
    "summary": """
        Contract generation from website to sale order.
    """,
    "data": [
        "security/ir.model.access.csv",
        "views/lead_template.xml",
        "views/sale_order.xml",
        "wizards/send_contract_wizard.xml",
    ],
    "installable": True,
}
