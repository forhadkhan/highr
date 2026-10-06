"""Privacy Policy and Terms of Use text (templates, not legal advice; have counsel review before launch)."""

UPDATED = "October 1, 2026"
COMPANY = "Highr Real Estate, Inc."
EMAIL = "contact@highr.example"
ADDRESS = "100 Market Street, San Francisco, CA 94105"

# Each page: slug, title, description, intro, sections [(heading, [paragraph | ("ul", [items])])]
PAGES = [
    {
        "slug": "privacy",
        "title": "Privacy Policy",
        "description": f"How {COMPANY} collects, uses and protects your personal information.",
        "intro": f"This policy explains what personal information {COMPANY} (\"Highr\", \"we\") collects through this website, how we use it, and the choices you have.",
        "sections": [
            ("Information we collect", [
                "We collect the information you give us when you request details, book a tour or contact us:",
                ("ul", ["Contact details: name, email address and phone number.",
                        "Your message and the community or home you are interested in.",
                        "Your marketing preferences, if you choose to receive updates."]),
                "We do not ask for payment card numbers, Social Security numbers or government ID through this website.",
            ]),
            ("How we use it", [
                ("ul", ["To reply to your enquiry and arrange tours or calls.",
                        "To send floor plans, pricing and availability you asked for.",
                        "To improve our website and communities.",
                        "To meet legal and licensing obligations."]),
                "We send marketing email or text messages only with your consent, and you can withdraw it at any time.",
            ]),
            ("Who we share it with", [
                "We share information with service providers that help us run the website and our sales process (for example hosting, email and customer-relationship tools), with mortgage or title partners only when you ask us to introduce you, and when the law requires it. We do not sell your personal information.",
            ]),
            ("Cookies and analytics", [
                "This website does not set advertising cookies. If we add analytics later, we will update this page and ask for consent where the law requires it.",
            ]),
            ("How long we keep it", [
                "We keep enquiry records for as long as needed to follow up and for up to three years after your last contact, unless a longer period is required by law or a purchase contract.",
            ]),
            ("Your rights", [
                "Depending on where you live, including California under the CCPA/CPRA, you may have the right to know what we hold about you, to correct or delete it, and to opt out of sale or sharing. We do not sell or share personal information for cross-context advertising. To make a request, email us at the address below; we respond within 45 days.",
            ]),
            ("Security and children", [
                "We use reasonable technical and organizational measures to protect your information, but no system is completely secure. This website is not directed to children under 13 and we do not knowingly collect their information.",
            ]),
            ("Changes and contact", [
                f"We may update this policy and will change the date above when we do. Questions or requests: {EMAIL}, or write to {COMPANY}, {ADDRESS}.",
            ]),
        ],
    },
    {
        "slug": "terms",
        "title": "Terms of Use",
        "description": f"The terms for using the {COMPANY} website.",
        "intro": f"These terms govern your use of this website, operated by {COMPANY} (\"Highr\", \"we\"). By using the site you agree to them.",
        "sections": [
            ("Information only", [
                "Content on this website, including prices, sizes, completion dates, floor plans, renderings and photographs, is for general information. It is not an offer to sell and does not form part of any contract. Prices, availability, specifications and dates may change without notice. Renderings and photographs are illustrative.",
            ]),
            ("Purchases", [
                "A home is reserved or sold only under a written purchase agreement signed by you and Highr. If anything on this website differs from that agreement, the agreement prevails.",
            ]),
            ("Using the site", [
                ("ul", ["Do not misuse the site, attempt to gain unauthorized access, or interfere with its operation.",
                        "Do not copy or reuse our text, photographs or logos without written permission.",
                        "Information you submit must be accurate and yours to share."]),
            ]),
            ("Intellectual property", [
                f"The site, its content and the Highr name and logo belong to {COMPANY} or its licensors and are protected by law. You may view and print pages for personal, non-commercial use.",
            ]),
            ("Third-party links", [
                "The site may link to or embed third-party services, such as maps. We do not control them and are not responsible for their content or practices.",
            ]),
            ("Disclaimer and liability", [
                "The site is provided \"as is\". To the fullest extent the law allows, Highr is not liable for indirect or consequential loss arising from your use of the site or reliance on its content.",
            ]),
            ("Fair housing", [
                "Highr is committed to equal housing opportunity. We do not discriminate on the basis of race, color, religion, sex, disability, familial status, national origin or any other protected characteristic.",
            ]),
            ("Governing law and contact", [
                f"These terms are governed by the laws of the State of California. Questions: {EMAIL}, or {COMPANY}, {ADDRESS}. See also our Privacy Policy.",
            ]),
        ],
    },
]
