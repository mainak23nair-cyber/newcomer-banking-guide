import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Newcomer Banking Guide",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 1.8rem; padding-bottom: 3rem;}
        .hero {
            padding: 1.4rem 1.5rem;
            border: 1px solid #e7e7e7;
            border-radius: 16px;
            background: #fafafa;
            margin-bottom: 1rem;
        }
        .verified {
            padding: .75rem 1rem;
            border-left: 4px solid #2e7d32;
            background: #f6fbf6;
            border-radius: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULTS = {
    "page": "Home",
    "profile_complete": False,
    "user_type": "International student",
    "ssn_status": "No",
    "itin_status": "No",
    "address_status": "Temporary address",
    "banking_needs": ["Pay bills", "International money transfers"],
    "priorities": ["Low/no monthly fees", "International transfers"],
    "saved_banks": [],
    "selected_bank": None,
    "checklist": {
        "Government-issued photo ID": False,
        "Visa / immigration-status document": False,
        "Proof of U.S. address": False,
        "University / employment information": False,
        "SSN / ITIN requirement verified": False,
        "Bank appointment / application method confirmed": False,
    },
    "journey_stage": 1,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, (dict, list)) else value

BANKS = [
    {
        "Bank": "MetroBank",
        "SSN": "Not always required",
        "Alternative ID": "Passport + secondary ID",
        "Proof of Address": "Required",
        "Monthly Fee": 0,
        "Minimum Balance": 0,
        "Fee Waiver": "Not needed",
        "International Transfers": "Yes",
        "Transfer Fee": 15,
        "ATM Access": "High",
        "Branch Access": "High",
        "Online Opening": "Yes",
        "Appointment": "Optional",
        "Credit Building": "Basic",
        "Bonus": "None",
    },
    {
        "Bank": "Harbor Bank",
        "SSN": "Varies by account",
        "Alternative ID": "Passport / ITIN may qualify",
        "Proof of Address": "Required",
        "Monthly Fee": 5,
        "Minimum Balance": 500,
        "Fee Waiver": "Direct deposit",
        "International Transfers": "Yes",
        "Transfer Fee": 10,
        "ATM Access": "Medium",
        "Branch Access": "Medium",
        "Online Opening": "Sometimes",
        "Appointment": "Recommended",
        "Credit Building": "Strong",
        "Bonus": "$100 demo bonus",
    },
    {
        "Bank": "Liberty Financial",
        "SSN": "Usually required",
        "Alternative ID": "Limited alternatives",
        "Proof of Address": "Required",
        "Monthly Fee": 12,
        "Minimum Balance": 1500,
        "Fee Waiver": "Balance or direct deposit",
        "International Transfers": "Yes",
        "Transfer Fee": 20,
        "ATM Access": "High",
        "Branch Access": "Medium",
        "Online Opening": "Yes",
        "Appointment": "Optional",
        "Credit Building": "Strong",
        "Bonus": "$200 demo bonus",
    },
    {
        "Bank": "CityTrust",
        "SSN": "Not always required",
        "Alternative ID": "Passport + tax ID options",
        "Proof of Address": "Alternative proofs considered",
        "Monthly Fee": 3,
        "Minimum Balance": 0,
        "Fee Waiver": "Student / newcomer criteria",
        "International Transfers": "Yes",
        "Transfer Fee": 8,
        "ATM Access": "Medium",
        "Branch Access": "Low",
        "Online Opening": "No",
        "Appointment": "Recommended",
        "Credit Building": "Basic",
        "Bonus": "None",
    },
]
BANK_DF = pd.DataFrame(BANKS)


def goto(page):
    st.session_state.page = page
    st.rerun()


def profile_summary():
    parts = [
        st.session_state.user_type,
        f"SSN: {st.session_state.ssn_status}",
        f"Address: {st.session_state.address_status}",
    ]
    if st.session_state.banking_needs:
        parts.extend(st.session_state.banking_needs[:2])
    return " • ".join(parts)


def recommendation_score(bank):
    score = 0
    reasons = []
    priorities = st.session_state.priorities
    needs = st.session_state.banking_needs

    if st.session_state.ssn_status in ["No", "In process", "Not sure"]:
        if bank["SSN"] in ["Not always required", "Varies by account"]:
            score += 3
            reasons.append("may support customers without a standard SSN path")

    if st.session_state.address_status in ["Temporary address", "No"]:
        if "Alternative" in bank["Proof of Address"]:
            score += 3
            reasons.append("offers more flexible proof-of-address guidance")

    if "Low/no monthly fees" in priorities and bank["Monthly Fee"] <= 5:
        score += 2
        reasons.append("low monthly fee")

    if "No minimum balance" in priorities and bank["Minimum Balance"] == 0:
        score += 2
        reasons.append("no minimum balance")

    if ("International transfers" in priorities or "International money transfers" in needs) and bank["International Transfers"] == "Yes":
        score += 2
        if bank["Transfer Fee"] <= 10:
            score += 1
            reasons.append("lower demo international-transfer fee")
        else:
            reasons.append("supports international transfers")

    if "Branch availability" in priorities and bank["Branch Access"] == "High":
        score += 2
        reasons.append("high branch access")

    if "ATM availability" in priorities and bank["ATM Access"] == "High":
        score += 2
        reasons.append("high ATM access")

    if "Credit-building options" in priorities and bank["Credit Building"] == "Strong":
        score += 2
        reasons.append("stronger credit-building options")

    if "Easy online banking" in priorities and bank["Online Opening"] == "Yes":
        score += 1
        reasons.append("online opening available")

    if "New-customer bonus" in priorities and bank["Bonus"] != "None":
        score += 1
        reasons.append("demo new-customer bonus")

    return score, reasons


def ranked_banks():
    rows = []
    for bank in BANKS:
        score, reasons = recommendation_score(bank)
        item = bank.copy()
        item["Match Score"] = score
        item["Why It Matches"] = ", ".join(reasons) if reasons else "general banking option"
        rows.append(item)
    return pd.DataFrame(rows).sort_values(
        ["Match Score", "Monthly Fee", "Transfer Fee"], ascending=[False, True, True]
    )


def current_requirements():
    reqs = [
        {
            "Requirement": "Government-issued photo ID",
            "Status": "Prepare",
            "Why": "Financial institutions use identification to verify who is opening the account.",
            "Examples": "Passport or another bank-accepted government-issued ID.",
        },
        {
            "Requirement": "Proof of U.S. address",
            "Status": "Verify",
            "Why": "Banks may need a residential or mailing address for customer identification and communication.",
            "Examples": "Lease, official mail, utility statement, or another bank-accepted document.",
        },
        {
            "Requirement": "University / employment information",
            "Status": "Prepare",
            "Why": "Some products or onboarding processes may ask about student or employment status.",
            "Examples": "Student ID, enrollment information, offer letter, or employment details.",
        },
    ]

    if st.session_state.user_type in ["International student", "International working professional"]:
        reqs.append(
            {
                "Requirement": "Visa / immigration-status document",
                "Status": "Prepare",
                "Why": "Banks may request immigration-related documents as part of identity or eligibility checks.",
                "Examples": "Applicable visa or immigration documentation.",
            }
        )

    if st.session_state.ssn_status == "Yes":
        reqs.append(
            {
                "Requirement": "SSN",
                "Status": "Ready / verify bank rules",
                "Why": "Banks may request a Social Security number for tax reporting and customer identification.",
                "Examples": "Provide it only directly to the financial institution, never to this prototype.",
            }
        )
    else:
        reqs.append(
            {
                "Requirement": "SSN / ITIN requirement",
                "Status": "Needs verification",
                "Why": "Requirements differ by financial institution and product.",
                "Examples": "Check whether the institution accepts an ITIN or another permitted identification route.",
            }
        )
    return reqs


def top_match():
    return ranked_banks().iloc[0].to_dict()


def overall_preparation():
    values = list(st.session_state.checklist.values())
    return sum(values) / len(values) if values else 0


def journey_stage_name():
    stages = {
        1: "Choose a bank",
        2: "Prepare documents",
        3: "Book appointment / apply",
        4: "Identity verification",
        5: "Account opened",
        6: "Set up banking",
    }
    return stages.get(st.session_state.journey_stage, "Choose a bank")


with st.sidebar:
    st.title("🏦 Banking Guide")
    st.caption("Prototype • newcomer-focused guidance")

    nav_items = [
        "Home",
        "About You",
        "My Banking Path",
        "Requirements",
        "Compare Banks",
        "Prepare",
        "My Journey",
        "Next Steps",
        "Ask the Guide",
    ]

    current_index = nav_items.index(st.session_state.page) if st.session_state.page in nav_items else 0
    selected = st.radio("Navigate", nav_items, index=current_index)
    if selected != st.session_state.page:
        st.session_state.page = selected
        st.rerun()

    st.divider()
    if st.session_state.profile_complete:
        st.caption("Current profile")
        st.write(profile_summary())
    else:
        st.caption("Complete **About You** to personalize the prototype.")

    if st.button("Reset prototype"):
        for key, value in DEFAULTS.items():
            st.session_state[key] = value.copy() if isinstance(value, (dict, list)) else value
        st.rerun()

    st.caption("Demo only. No real financial or identity data is collected.")


if st.session_state.page == "Home":
    st.markdown(
        """
        <div class="hero">
            <h1>Set up U.S. banking with confidence.</h1>
            <p>
                A personalized digital banking tour guide for newcomers:
                understand what applies to you, prepare the right requirements,
                compare suitable options, and know what to do next.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Start My Banking Guide", type="primary", use_container_width=True):
            goto("About You")
    with c2:
        if st.button("Jump to Demo Comparison", use_container_width=True):
            goto("Compare Banks")

    st.subheader("Your guided journey")
    cols = st.columns(5)
    journey = [
        ("1. Understand me", "Tell the guide about your situation."),
        ("2. Prepare me", "See requirements relevant to you."),
        ("3. Help me choose", "Compare options around your priorities."),
        ("4. Guide my action", "Know what to prepare and do next."),
        ("5. Build confidence", "Learn the basics after setup."),
    ]
    for col, (title, desc) in zip(cols, journey):
        with col:
            st.markdown(f"**{title}**")
            st.caption(desc)

    st.info(
        "This prototype provides guidance only. It does not open accounts, transfer money, "
        "pull credit, or collect SSNs, passport numbers, account numbers, or banking credentials."
    )

    with st.expander("Why this concept?"):
        st.write(
            "The prototype is designed around a simple insight: newcomers often do not need "
            "more banking information; they need help understanding which information applies "
            "to their situation, what to prepare, which option fits their priorities, and what to do next."
        )

    with st.expander("Future Trust Layer (concept only)"):
        st.write(
            "A future version could explore verified credentials or tamper-resistant information "
            "provenance to show where requirements originated and when they were reviewed. "
            "Sensitive personal or financial data should not be placed on a blockchain."
        )

elif st.session_state.page == "About You":
    st.title("Tell us about your situation")
    st.write("This prototype uses only demo selections. Do not enter sensitive personal information.")

    with st.form("profile_form"):
        user_type_options = ["International student", "International working professional", "Domestic newcomer", "Other newcomer"]
        user_type = st.radio(
            "What best describes you?",
            user_type_options,
            index=user_type_options.index(st.session_state.user_type),
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            ssn_options = ["Yes", "No", "In process", "Not sure"]
            ssn_status = st.selectbox(
                "Do you currently have an SSN?",
                ssn_options,
                index=ssn_options.index(st.session_state.ssn_status),
            )
        with c2:
            itin_options = ["Yes", "No", "Not sure what this is"]
            itin_status = st.selectbox(
                "Do you have an ITIN?",
                itin_options,
                index=itin_options.index(st.session_state.itin_status),
            )
        with c3:
            address_options = ["Yes", "Temporary address", "No"]
            address_status = st.selectbox(
                "Do you currently have a U.S. address?",
                address_options,
                index=address_options.index(st.session_state.address_status),
            )

        needs_options = [
            "Receive salary/direct deposit",
            "Pay bills",
            "International money transfers",
            "Debit card",
            "Build U.S. credit",
            "Savings",
            "ATM access",
        ]
        banking_needs = st.multiselect(
            "What are your main banking needs?",
            needs_options,
            default=[x for x in st.session_state.banking_needs if x in needs_options],
        )

        priority_options = [
            "Low/no monthly fees",
            "No minimum balance",
            "International transfers",
            "Branch availability",
            "ATM availability",
            "Easy online banking",
            "Customer service",
            "New-customer bonus",
            "Credit-building options",
        ]
        priorities = st.multiselect(
            "What matters most when choosing a bank?",
            priority_options,
            default=[x for x in st.session_state.priorities if x in priority_options],
        )

        submitted = st.form_submit_button("Build My Banking Path", type="primary", use_container_width=True)

    if submitted:
        st.session_state.user_type = user_type
        st.session_state.ssn_status = ssn_status
        st.session_state.itin_status = itin_status
        st.session_state.address_status = address_status
        st.session_state.banking_needs = banking_needs
        st.session_state.priorities = priorities
        st.session_state.profile_complete = True
        goto("My Banking Path")

elif st.session_state.page == "My Banking Path":
    st.title("Your Banking Path")
    if not st.session_state.profile_complete:
        st.warning("Complete the About You step first so the prototype can personalize this page.")
        if st.button("Go to About You"):
            goto("About You")
    else:
        st.caption(profile_summary())
        match = top_match()
        progress = min(
            1.0,
            0.15
            + (0.15 if st.session_state.profile_complete else 0)
            + (0.20 if st.session_state.selected_bank else 0)
            + 0.30 * overall_preparation()
            + 0.20 * ((st.session_state.journey_stage - 1) / 5),
        )
        st.progress(progress)
        st.caption(f"Prototype journey progress: {int(progress * 100)}%")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("### 📄 My Requirements")
            st.write("See what you should prepare and verify.")
            if st.button("Open Requirements", use_container_width=True):
                goto("Requirements")
        with c2:
            st.markdown("### 🏦 Compare Banks")
            st.write("Compare demo options around your priorities.")
            if st.button("Compare Options", use_container_width=True):
                goto("Compare Banks")
        with c3:
            st.markdown("### ✅ Prepare")
            st.write("Track your readiness before applying.")
            if st.button("Open Checklist", use_container_width=True):
                goto("Prepare")
        with c4:
            st.markdown("### 🧭 My Journey")
            st.write("See your current stage and next action.")
            if st.button("View Journey", use_container_width=True):
                goto("My Journey")

        st.divider()
        st.subheader("Current recommendation")
        st.success(f"Demo best match: **{match['Bank']}**")
        st.write(f"**Why it matches:** {match['Why It Matches']}")
        st.caption("Prototype recommendation based only on fictional data and your demo preferences. Not financial advice.")

        st.subheader("Your priorities")
        st.write(" • ".join(st.session_state.priorities) if st.session_state.priorities else "No priorities selected yet.")

elif st.session_state.page == "Requirements":
    st.title("Your Requirements")
    st.write("Based on what you told us, these are the items you should prepare or verify.")

    for req in current_requirements():
        with st.expander(f"{req['Requirement']} — {req['Status']}"):
            st.write(f"**Why it may matter:** {req['Why']}")
            st.write(f"**Examples / next step:** {req['Examples']}")

    if st.session_state.ssn_status != "Yes":
        st.warning(
            "You indicated that you do not currently have an SSN, or it is not confirmed. "
            "That does not automatically mean you cannot open an account. Requirements vary by institution and product."
        )

    if st.session_state.address_status in ["Temporary address", "No"]:
        st.warning(
            "Proof of address may become a friction point. Confirm which alternative documents your chosen institution accepts."
        )

    st.markdown(
        """
        <div class="verified">
            <b>Trust principle:</b> show the source of every requirement, when it was last reviewed,
            and direct the user back to the financial institution for final verification.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Compare My Options", type="primary"):
        goto("Compare Banks")

elif st.session_state.page == "Compare Banks":
    st.title("Compare Banking Options")
    st.caption("All institutions and offers below are fictional prototype data.")

    ranked = ranked_banks()

    c1, c2, c3 = st.columns(3)
    with c1:
        low_fee_only = st.checkbox("Monthly fee ≤ $5")
    with c2:
        no_minimum_only = st.checkbox("No minimum balance")
    with c3:
        branch_high_only = st.checkbox("High branch access")

    filtered = ranked.copy()
    if low_fee_only:
        filtered = filtered[filtered["Monthly Fee"] <= 5]
    if no_minimum_only:
        filtered = filtered[filtered["Minimum Balance"] == 0]
    if branch_high_only:
        filtered = filtered[filtered["Branch Access"] == "High"]

    sort_by = st.selectbox(
        "Sort by",
        ["Best match", "Lowest monthly fee", "Lowest transfer fee", "Lowest minimum balance"],
    )
    if sort_by == "Lowest monthly fee":
        filtered = filtered.sort_values("Monthly Fee")
    elif sort_by == "Lowest transfer fee":
        filtered = filtered.sort_values("Transfer Fee")
    elif sort_by == "Lowest minimum balance":
        filtered = filtered.sort_values("Minimum Balance")
    else:
        filtered = filtered.sort_values(["Match Score", "Monthly Fee"], ascending=[False, True])

    display_cols = [
        "Bank",
        "Match Score",
        "SSN",
        "Proof of Address",
        "Monthly Fee",
        "Minimum Balance",
        "Transfer Fee",
        "Branch Access",
        "Online Opening",
    ]
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

    if filtered.empty:
        st.info("No demo banks match the current filters. Clear one or more filters.")
    else:
        st.subheader("Compare details")
        chosen = st.selectbox("Choose a demo bank to inspect", filtered["Bank"].tolist())
        bank = next(b for b in BANKS if b["Bank"] == chosen)
        score, reasons = recommendation_score(bank)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Demo match score", score)
        with c2:
            st.metric("Monthly fee", f"${bank['Monthly Fee']}")
        with c3:
            st.metric("Transfer fee", f"${bank['Transfer Fee']}")

        st.write("**Why this may fit you:**")
        if reasons:
            for reason in reasons:
                st.write(f"✓ {reason}")
        else:
            st.write("This option does not strongly match the priorities you selected.")

        with st.expander("Eligibility & documents"):
            st.write(f"**SSN:** {bank['SSN']}")
            st.write(f"**Alternative ID:** {bank['Alternative ID']}")
            st.write(f"**Proof of address:** {bank['Proof of Address']}")

        with st.expander("Fees & access"):
            st.write(f"**Monthly fee:** ${bank['Monthly Fee']}")
            st.write(f"**Minimum balance:** ${bank['Minimum Balance']}")
            st.write(f"**Fee waiver:** {bank['Fee Waiver']}")
            st.write(f"**ATM access:** {bank['ATM Access']}")
            st.write(f"**Branch access:** {bank['Branch Access']}")

        with st.expander("Transfers & account setup"):
            st.write(f"**International transfers:** {bank['International Transfers']}")
            st.write(f"**Demo transfer fee:** ${bank['Transfer Fee']}")
            st.write(f"**Online opening:** {bank['Online Opening']}")
            st.write(f"**Appointment:** {bank['Appointment']}")
            st.write(f"**Credit-building options:** {bank['Credit Building']}")
            st.write(f"**Demo bonus:** {bank['Bonus']}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Save this option", use_container_width=True):
                if chosen not in st.session_state.saved_banks:
                    st.session_state.saved_banks.append(chosen)
                st.success(f"{chosen} saved.")
        with c2:
            if st.button("Add to My Banking Path", type="primary", use_container_width=True):
                st.session_state.selected_bank = chosen
                st.session_state.journey_stage = max(st.session_state.journey_stage, 2)
                goto("Prepare")

        st.info(
            "Prototype trust rule: requirements, fees, and offers must be re-verified directly with the financial institution before a real application."
        )

elif st.session_state.page == "Prepare":
    st.title("Prepare Before You Apply")

    if st.session_state.selected_bank:
        st.write(f"Preparing for: **{st.session_state.selected_bank}**")
    else:
        st.info("You have not selected a demo bank yet. You can still use the checklist.")

    updated = {}
    for item, value in st.session_state.checklist.items():
        updated[item] = st.checkbox(item, value=value, key=f"check_{item}")
    st.session_state.checklist = updated

    pct = overall_preparation()
    st.progress(pct)
    st.write(f"**You’re {int(pct * 100)}% prepared.**")

    if st.session_state.address_status in ["Temporary address", "No"]:
        st.warning(
            "Possible issue: your address may not be permanent. Verify which proof-of-address alternatives your selected institution accepts."
        )

    if st.session_state.ssn_status != "Yes":
        st.warning(
            "Possible issue: SSN / ITIN requirements differ. Confirm the exact requirement for the chosen account before applying."
        )

    if pct == 1.0:
        st.success("Your prototype checklist is complete. You can move to the guided opening journey.")
        if st.button("Continue to My Journey", type="primary"):
            st.session_state.journey_stage = max(st.session_state.journey_stage, 3)
            goto("My Journey")
    else:
        st.caption("Complete the checklist items as you prepare. This is a prototype, not a legal eligibility check.")

elif st.session_state.page == "My Journey":
    st.title("My Banking Journey")

    stages = [
        ("Choose Bank", "Compare options and select one that fits your priorities."),
        ("Prepare Documents", "Confirm identification, address, and eligibility requirements."),
        ("Book Appointment / Apply", "Choose the bank's real application or appointment channel."),
        ("Identity Verification", "Complete verification directly with the financial institution."),
        ("Account Opened", "Confirm the account is active and you can access it."),
        ("Set Up Banking", "Add direct deposit, transfers, AutoPay, and learn credit basics."),
    ]

    st.write(f"**Current stage:** {journey_stage_name()}")
    st.progress((st.session_state.journey_stage - 1) / 5)

    for idx, (name, desc) in enumerate(stages, start=1):
        status = "✓ Complete" if idx < st.session_state.journey_stage else ("→ Current" if idx == st.session_state.journey_stage else "Upcoming")
        with st.expander(f"{idx}. {name} — {status}", expanded=(idx == st.session_state.journey_stage)):
            st.write(desc)
            if idx == 1:
                st.write(f"**Selected demo bank:** {st.session_state.selected_bank or 'None yet'}")
            elif idx == 2:
                st.write(f"**Preparation:** {int(overall_preparation() * 100)}%")
            elif idx == 3:
                st.write("**What could delay you:** appointment availability, missing documents, or unclear eligibility.")
            elif idx == 4:
                st.write("**Important:** identity verification happens with the bank, not inside this prototype.")
            elif idx == 5:
                st.write("**Confirm:** access to online banking, debit card process, and account terms.")
            elif idx == 6:
                st.write("**Next:** direct deposit, transfers, AutoPay, fees, and credit basics.")

    c1, c2 = st.columns(2)
    with c1:
        if st.session_state.journey_stage > 1 and st.button("Previous stage", use_container_width=True):
            st.session_state.journey_stage -= 1
            st.rerun()
    with c2:
        if st.session_state.journey_stage < 6 and st.button("Mark current stage complete", type="primary", use_container_width=True):
            st.session_state.journey_stage += 1
            st.rerun()
        elif st.session_state.journey_stage == 6 and st.button("Go to Next Steps", type="primary", use_container_width=True):
            goto("Next Steps")

elif st.session_state.page == "Next Steps":
    st.title("Your account is open. What’s next?")
    st.write("The experience should continue until the newcomer feels confident managing everyday banking.")

    topics = {
        "Set Up Direct Deposit": (
            "Direct deposit sends salary or other payments directly into a bank account. "
            "Your employer normally provides the setup process and the bank provides routing/account information."
        ),
        "International Transfers": (
            "Compare transfer fees, exchange rates, delivery speed, and recipient requirements. "
            "The cheapest-looking option is not always the cheapest after exchange-rate costs."
        ),
        "Understand AutoPay": (
            "AutoPay can automatically pay recurring bills or credit-card balances. "
            "You still need enough money in the linked account when the payment is processed."
        ),
        "Avoid Common Fees": (
            "Review monthly maintenance fees, overdraft policies, ATM fees, transfer fees, "
            "and any conditions required to waive account fees."
        ),
        "Understand U.S. Credit": (
            "Credit history reflects how credit accounts are used and repaid. "
            "A checking account and a credit account serve different purposes."
        ),
        "What Is a Hard Inquiry?": (
            "A hard inquiry may occur when you apply for certain credit products. "
            "Repeated applications in a short period can affect a credit profile, so understand eligibility before applying."
        ),
    }

    cols = st.columns(2)
    for i, (topic, explanation) in enumerate(topics.items()):
        with cols[i % 2]:
            with st.expander(topic):
                st.write(explanation)
                st.caption("Educational prototype content only, not financial advice.")

    st.success(
        "Meaningful outcome: success is not only 'account opened.' "
        "It is 'I can manage my U.S. banking with confidence and less dependence on others.'"
    )

elif st.session_state.page == "Ask the Guide":
    st.title("Ask Your Banking Guide")
    st.write("A rule-based prototype showing how an assistant could provide simple, contextual explanations.")

    QA = {
        "Do I need an SSN?": (
            "Not every institution or account uses identical requirements. If you do not have an SSN, "
            "check whether the specific bank accepts an ITIN or another permitted identification route. Verify directly before applying."
        ),
        "What counts as proof of address?": (
            "Accepted documents vary. Banks may accept items such as a lease, utility statement, official mail, "
            "or another document they specify. Confirm the exact list with the institution."
        ),
        "What should I bring to the bank?": (
            "Start with accepted government identification, immigration/status documents if applicable, proof of address, "
            "and any student/employment information the bank requests. Use your personalized checklist and verify it before your visit."
        ),
        "How do international transfers work?": (
            "International transfers can differ in fee, exchange rate, speed, and recipient requirements. "
            "Compare the total cost, not just the advertised transfer fee."
        ),
        "What is a checking account?": (
            "A checking account is generally used for everyday transactions such as debit-card purchases, bill payments, withdrawals, and direct deposits."
        ),
        "What is a credit score?": (
            "A credit score is a numerical representation used by lenders to help evaluate credit risk. "
            "Newcomers may initially have limited or no U.S. credit history."
        ),
        "What is a hard inquiry?": (
            "A hard inquiry can occur when a lender checks your credit as part of a credit application. "
            "Understand product eligibility before submitting repeated applications."
        ),
        "What should I do next?": (
            f"Your current prototype stage is: {journey_stage_name()}. Open My Journey to see the action associated with that stage."
        ),
    }

    question = st.selectbox("Choose a question", list(QA.keys()))
    if st.button("Ask", type="primary"):
        st.info(QA[question])
        st.caption("Requirements vary by institution. Verify bank-specific requirements before applying.")

st.divider()
st.caption(
    "Newcomer Banking Guide — classroom prototype. All bank names, fees, bonuses, eligibility rules, "
    "and recommendations shown here are fictional demonstration data."
)
