import streamlit as st

from compatibility import check_compatibility, compatible_modules, load_components


def format_price(price):
    return f"${price:.2f}"


def main():
    st.set_page_config(
        page_title="Part Pair",
        page_icon="🌱",
        layout="wide"
    )

    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #f3fff6 0%, #ffffff 55%);
            color: #23452f;
        }

        [data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.75);
        }

        .hero {
            background: #dff5e5;
            border: 1px solid #b8dfc3;
            border-radius: 22px;
            padding: 28px 30px;
            margin-bottom: 22px;
            box-shadow: 0 8px 22px rgba(76, 132, 93, 0.10);
        }

        .hero h1 {
            color: #285c38;
            margin: 0 0 6px 0;
        }

        .hero p {
            color: #4e7058;
            margin: 0;
            font-size: 1.05rem;
        }

        .section-label {
            color: #39764b;
            font-size: 1.35rem;
            font-weight: 700;
            margin-top: 12px;
        }

        div[data-testid="stButton"] button {
            background: #7fc996;
            color: #173e24;
            border: none;
            border-radius: 12px;
            font-weight: 700;
        }

        div[data-testid="stButton"] button:hover {
            background: #68b982;
            color: white;
        }

        div[data-testid="stSelectbox"] > div > div {
            border-radius: 12px;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #cce8d3;
            border-radius: 14px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero">
            <h1>🌱 Part Pair</h1>
            <p>Pick a board and a component to see if they can work together.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    try:
        data = load_components()
    except (OSError, ValueError) as error:
        st.error("I couldn't load the component data: " + str(error))
        st.stop()

    controllers = {}
    for item in data["microcontrollers"]:
        controllers[item["name"]] = item

    modules = {}
    for item in data["modules"]:
        modules[item["name"]] = item

    st.markdown('<p class="section-label">Choose your parts</p>', unsafe_allow_html=True)

    left_column, right_column = st.columns(2)

    with left_column:
        controller_name = st.selectbox(
            "Microcontroller",
            list(controllers.keys())
        )

    with right_column:
        module_name = st.selectbox(
            "Sensor or module",
            list(modules.keys())
        )

    controller = controllers[controller_name]
    module = modules[module_name]

    if st.button("Check this pair", use_container_width=True):
        compatible, checks = check_compatibility(controller, module)

        if compatible:
            st.success(controller_name + " and " + module_name + " are compatible!")
        else:
            st.error(controller_name + " and " + module_name + " are not compatible.")

        for label, passed, explanation in checks:
            if passed:
                st.write("✅ **" + label + ":** " + explanation)
            else:
                st.write("❌ **" + label + ":** " + explanation)

    st.divider()
    st.markdown(
        '<p class="section-label">Other matches for ' + controller_name + '</p>',
        unsafe_allow_html=True
    )
    st.caption("These options pass every check and are listed from lowest to highest price.")

    matches = compatible_modules(controller, data["modules"])
    table_rows = []

    for item in matches:
        row = {
            "Component": item["name"],
            "Connection": ", ".join(item["interfaces"]),
            "Pins needed": item["required_pins"],
            "Price": format_price(item["price"])
        }
        table_rows.append(row)

    if table_rows:
        st.dataframe(table_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No components in the sample data match this board yet.")


if __name__ == "__main__":
    main()
