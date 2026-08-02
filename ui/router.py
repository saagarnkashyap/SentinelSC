from modules.control_tower import render_control_tower
from modules.inventory import render_inventory
from modules.simulation import render_simulation
from modules.analytics import render_analytics
from modules.advisor import render_advisor
from modules.about import render_about


def render_page(page):
    if page == "Control Tower":
        render_control_tower()
    elif page == "Inventory Intelligence":
        render_inventory()
    elif page == "Scenario Simulator":
        render_simulation()
    elif page == "Analytics":
        render_analytics()
    elif page == "AI Advisor":
        render_advisor()
    elif page == "About":
        render_about()